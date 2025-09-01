#!/usr/bin/env python3
"""
Migration script to move data from JSON files to Supabase
Run this after setting up your Supabase project and configuring environment variables
"""

import json
import os
from dotenv import load_dotenv
from app.services.supabase_service import SupabaseService

def load_json_data():
    """Load data from existing JSON files"""
    try:
        # Load stock data
        with open('sample_stock.json', 'r', encoding='utf-8') as f:
            stock_data = json.load(f)
        
        # Load daily usage config
        with open('daily_usage_config.json', 'r', encoding='utf-8') as f:
            daily_usage_config = json.load(f)
        
        # Load recipes
        with open('recipes.json', 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        # Load sales history
        with open('sales_history.json', 'r', encoding='utf-8') as f:
            sales_history = json.load(f)
        
        return stock_data, daily_usage_config, recipes, sales_history
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file {e.filename}")
        return None, None, None, None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}")
        return None, None, None, None

def main():
    """Main migration function"""
    print("🚀 Starting migration to Supabase...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if Supabase credentials are set
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
        print("\nPlease create a .env file with:")
        print("SUPABASE_URL=your_supabase_project_url")
        print("SUPABASE_ANON_KEY=your_supabase_anon_key")
        return
    
    try:
        # Initialize Supabase service
        print("🔌 Connecting to Supabase...")
        supabase_service = SupabaseService()
        
        # Test connection
        connection_test = supabase_service.test_connection()
        if not connection_test["success"]:
            print(f"❌ Connection failed: {connection_test['message']}")
            return
        
        print("✅ Supabase connection successful!")
        
        # Load JSON data
        print("📁 Loading data from JSON files...")
        stock_data, daily_usage_config, recipes, sales_history = load_json_data()
        
        if not all([stock_data, daily_usage_config, recipes, sales_history]):
            print("❌ Failed to load JSON data")
            return
        
        print(f"📊 Loaded data:")
        print(f"   - Stock items: {len(stock_data.get('stock_data', {}))} categories")
        
        # Count daily usage config items correctly
        daily_config_count = 0
        if "daily_usage_config" in daily_usage_config:
            config_data = daily_usage_config["daily_usage_config"]
            for category, items in config_data.items():
                daily_config_count += len(items)
        print(f"   - Daily usage config: {daily_config_count} items")
        
        # Count recipes correctly
        recipes_count = 0
        if "recipes" in recipes:
            recipes_count = len(recipes["recipes"])
        else:
            recipes_count = len(recipes) if isinstance(recipes, list) else 1
        print(f"   - Recipes: {recipes_count} recipes")
        
        # Count sales history correctly
        sales_count = 0
        if "sales_records" in sales_history:
            sales_count = len(sales_history["sales_records"])
        else:
            sales_count = len(sales_history) if isinstance(sales_history, list) else 1
        print(f"   - Sales history: {sales_count} records")
        
        # Confirm migration
        print("\n⚠️  WARNING: This will replace all existing data in Supabase!")
        confirm = input("Are you sure you want to continue? (yes/no): ").lower().strip()
        
        if confirm != "yes":
            print("Migration cancelled.")
            return
        
        # Perform migration
        print("\n🔄 Starting migration...")
        migration_result = supabase_service.migrate_from_json(
            stock_data, daily_usage_config, recipes, sales_history
        )
        
        if migration_result["success"]:
            print("✅ Migration completed successfully!")
            migrated = migration_result["migrated"]
            print(f"   - Stock items: {migrated['stock_items']}")
            print(f"   - Daily usage config: {migrated['daily_usage_config']}")
            print(f"   - Recipes: {migrated['recipes']}")
            print(f"   - Sales history: {migrated['sales_history']}")
            
            print("\n🎉 Your data is now in Supabase!")
            print("You can now update your backend to use Supabase instead of JSON files.")
            
        else:
            print(f"❌ Migration failed: {migration_result['message']}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
