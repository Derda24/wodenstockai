#!/usr/bin/env python3
"""
Test script to process Excel files and check stock levels
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.excel_processor import ExcelProcessor

def load_stock_data():
    """Load the current stock data"""
    try:
        # Look for stock data in the backend directory
        stock_file = Path(__file__).parent / "sample_stock.json"
        with open(stock_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ sample_stock.json not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing sample_stock.json: {e}")
        return None

def load_recipes():
    """Load the recipes data"""
    try:
        # Look for recipes in the backend directory
        recipes_file = Path(__file__).parent / "recipes.json"
        with open(recipes_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ recipes.json not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing recipes.json: {e}")
        return None

def process_excel_file(file_path, excel_processor):
    """Process a single Excel file"""
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        filename = os.path.basename(file_path)
        success, sale_data, errors = excel_processor.process_excel_file(file_content, filename)
        
        if success:
            print(f"✅ {filename} processed successfully")
            print(f"   Sales records: {len(sale_data.get('items', []))}")
            # Show some sample data
            if sale_data.get('items'):
                print("   Sample sales:")
                for i, item in enumerate(sale_data['items'][:3]):  # Show first 3 items
                    print(f"     {i+1}. {item.get('product_name', 'Unknown')} - Qty: {item.get('quantity', 0)}")
                if len(sale_data['items']) > 3:
                    print(f"     ... and {len(sale_data['items']) - 3} more items")
            return sale_data
        else:
            print(f"❌ {filename} processing failed:")
            for error in errors:
                print(f"   - {error}")
            return None
            
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def check_stock_levels(stock_data, recipes):
    """Check which raw materials are running low"""
    print("\n🔍 Checking Stock Levels...")
    
    low_stock_items = []
    
    for category, items in stock_data["stock_data"].items():
        for item_name, item_data in items.items():
            current_stock = item_data.get("current_stock", 0)
            min_stock = item_data.get("min_stock_level", 0)
            
            if current_stock <= min_stock:
                low_stock_items.append({
                    "name": item_name,
                    "category": category,
                    "current": current_stock,
                    "minimum": min_stock,
                    "unit": item_data.get("unit", "unknown")
                })
    
    if low_stock_items:
        print("⚠️  LOW STOCK ALERTS:")
        for item in low_stock_items:
            print(f"   • {item['name']} ({item['category']}): {item['current']} {item['unit']} (min: {item['minimum']})")
    else:
        print("✅ All stock levels are above minimum thresholds")
    
    return low_stock_items

def analyze_recipe_usage(recipes, stock_data):
    """Analyze which ingredients are most used in recipes"""
    print("\n📊 Recipe Ingredient Analysis...")
    
    ingredient_usage = {}
    
    # Check if recipes is a list or has a different structure
    if isinstance(recipes, dict) and "recipes" in recipes:
        recipe_list = recipes["recipes"]
    elif isinstance(recipes, list):
        recipe_list = recipes
    else:
        print("   ❌ Unexpected recipes data structure")
        return
    
    for recipe in recipe_list:
        if isinstance(recipe, dict) and recipe.get("ingredients"):
            for ingredient in recipe["ingredients"]:
                ingredient_name = ingredient.get("name", "")
                if ingredient_name:
                    if ingredient_name not in ingredient_usage:
                        ingredient_usage[ingredient_name] = 0
                    ingredient_usage[ingredient_name] += 1
    
    if ingredient_usage:
        print("   Most used ingredients in recipes:")
        sorted_ingredients = sorted(ingredient_usage.items(), key=lambda x: x[1], reverse=True)
        for ingredient, count in sorted_ingredients[:10]:  # Top 10
            print(f"     • {ingredient}: used in {count} recipes")
    else:
        print("   No ingredients found in recipes")

def check_excel_file_issues(excel_files):
    """Check for common issues with Excel files"""
    print("\n🔍 Excel File Analysis...")
    
    for excel_file in excel_files:
        if excel_file.exists():
            print(f"   ✅ {excel_file.name} - Found")
        else:
            print(f"   ❌ {excel_file.name} - Not found")
    
    # Check for the typo in filename
    typo_file = Path(__file__).parent.parent / "29.008.2025.xlsx"
    if typo_file.exists():
        print(f"   ⚠️  Found file with typo: 29.008.2025.xlsx (should be 29.08.2025.xlsx)")
        print("   💡 Consider renaming this file to fix the date format")

def main():
    """Main test function"""
    print("🧪 Testing Excel Processing and Stock Management System")
    print("=" * 60)
    
    # Load data
    print("\n📊 Loading data...")
    stock_data = load_stock_data()
    if not stock_data:
        return
    
    recipes = load_recipes()
    if not recipes:
        return
    
    print("✅ Data loaded successfully")
    
    # Initialize Excel processor
    excel_processor = ExcelProcessor()
    
    # Process Excel files - look in the parent directory (root of project)
    excel_files = [
        Path(__file__).parent.parent / "27.08.2025.xlsx",
        Path(__file__).parent.parent / "28.08.2025.xlsx", 
        Path(__file__).parent.parent / "29.08.2025.xlsx"
    ]
    
    print(f"\n📁 Processing {len(excel_files)} Excel files...")
    
    # Check for Excel file issues first
    check_excel_file_issues(excel_files)
    
    all_sales = []
    for excel_file in excel_files:
        if excel_file.exists():
            sale_data = process_excel_file(str(excel_file), excel_processor)
            if sale_data:
                all_sales.append(sale_data)
        else:
            print(f"⚠️  {excel_file.name} not found, skipping...")
    
    print(f"\n📈 Total sales processed: {len(all_sales)}")
    
    # Check current stock levels
    low_stock_items = check_stock_levels(stock_data, recipes)
    
    # Analyze recipe ingredient usage
    analyze_recipe_usage(recipes, stock_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print(f"   • Excel files processed: {len([f for f in excel_files if f.exists()])}")
    print(f"   • Sales records found: {sum(len(s.get('items', [])) for s in all_sales)}")
    print(f"   • Low stock items: {len(low_stock_items)}")
    
    if low_stock_items:
        print("\n🚨 ACTION REQUIRED: Some raw materials are running low!")
        print("   Consider placing orders for the items listed above.")
    else:
        print("\n✅ All systems operational - stock levels are healthy!")

if __name__ == "__main__":
    main()
