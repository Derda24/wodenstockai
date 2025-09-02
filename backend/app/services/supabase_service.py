from supabase import create_client, Client
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class SupabaseService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Supabase connection"""
        try:
            # Try to query a simple table or use a health check
            response = self.client.table("stock_items").select("id").limit(1).execute()
            return {"success": True, "message": "Supabase connection successful"}
        except Exception as e:
            return {"success": False, "message": f"Supabase connection failed: {str(e)}"}
    
    def get_stock_list(self) -> Dict[str, Any]:
        """Get all stock items from Supabase"""
        try:
            response = self.client.table("stock_items").select("*").execute()
            
            if response.data:
                # Transform the data to match the expected format
                stock_data = {"stock_data": {}}
                
                for item in response.data:
                    category = item.get("category_name", "unknown")
                    item_name = item.get("item_name", "unknown")
                    
                    if category not in stock_data["stock_data"]:
                        stock_data["stock_data"][category] = {}
                    
                    stock_data["stock_data"][category][item_name] = {
                        "current_stock": item.get("current_stock", 0.0),
                        "min_stock": item.get("min_stock", 0.0),
                        "unit": item.get("unit", ""),
                        "material_id": item.get("material_id", ""),
                        "can_edit": True,
                        "edit_reason": "",
                        "edit_message": "",
                        "last_manual_update": {},
                        "last_daily_consumption": {}
                    }
                
                return {"success": True, "data": stock_data}
            else:
                return {"success": True, "data": {"stock_data": {}}}
                
        except Exception as e:
            return {"success": False, "message": f"Error fetching stock list: {str(e)}"}
    
    def update_stock_manually(self, material_id: str, new_stock: float, reason: str) -> Dict[str, Any]:
        """Update stock manually in Supabase"""
        try:
            # First, get the current stock item
            response = self.client.table("stock_items").select("*").eq("material_id", material_id).execute()
            
            if not response.data:
                return {"success": False, "message": f"Item with ID '{material_id}' not found"}
            
            item = response.data[0]
            old_stock = item.get("current_stock", 0.0)
            item_name = item.get("item_name", "")
            category_name = item.get("category_name", "")
            
            # Update the stock
            update_response = self.client.table("stock_items").update({
                "current_stock": float(new_stock),
                "updated_at": datetime.now().isoformat()
            }).eq("material_id", material_id).execute()
            
            if update_response.data:
                # Create a transaction record
                transaction_data = {
                    "stock_item_id": item["id"],
                    "transaction_type": "manual_update",
                    "old_stock": old_stock,
                    "new_stock": float(new_stock),
                    "change_amount": float(new_stock) - old_stock,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.client.table("stock_transactions").insert(transaction_data).execute()
                
                # Create/update manual update record for protection
                manual_update_data = {
                    "stock_item_id": item["id"],
                    "old_stock": old_stock,
                    "new_stock": float(new_stock),
                    "reason": reason,
                    "manual_update_flag": True,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Check if manual update record exists
                existing_manual = self.client.table("manual_updates").select("*").eq("stock_item_id", item["id"]).execute()
                
                if existing_manual.data:
                    # Update existing record
                    self.client.table("manual_updates").update(manual_update_data).eq("stock_item_id", item["id"]).execute()
                else:
                    # Create new record
                    self.client.table("manual_updates").insert(manual_update_data).execute()
                
                return {
                    "success": True,
                    "message": f"Stock updated successfully for {item_name}",
                    "item_name": item_name,
                    "category": category_name,
                    "old_stock": old_stock,
                    "new_stock": float(new_stock),
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "message": "Failed to update stock"}
                
        except Exception as e:
            return {"success": False, "message": f"Error updating stock: {str(e)}"}
    
    def apply_daily_consumption(self, force: bool = False) -> Dict[str, Any]:
        """Apply daily consumption to all stock items.
        If force is True, bypass recent manual-update protection and consume anyway.
        """
        try:
            # Get all stock items
            stock_response = self.client.table("stock_items").select("*").execute()
            
            if not stock_response.data:
                return {"success": False, "message": "No stock items found"}
            
            # Get daily usage configuration
            daily_config_response = self.client.table("daily_usage_config").select("*").eq("is_active", True).execute()
            daily_config = {item["material_id"]: item["daily_amount"] for item in daily_config_response.data} if daily_config_response.data else {}
            
            updated_count = 0
            skipped_count = 0
            
            for stock_item in stock_response.data:
                material_id = stock_item.get("material_id")
                daily_amount = daily_config.get(material_id, 0.0)
                
                if daily_amount <= 0:
                    continue
                
                should_skip = False
                if not force:
                    # Check if this item was manually updated recently (4 hour protection)
                    manual_response = self.client.table("manual_updates").select("*").eq("stock_item_id", stock_item["id"]).execute()
                    if manual_response.data:
                        manual_update = manual_response.data[0]
                        if manual_update.get("manual_update_flag", False):
                            update_time_str = manual_update.get("timestamp", "")
                            if update_time_str:
                                try:
                                    update_time = datetime.fromisoformat(update_time_str.replace('Z', '+00:00'))
                                    cutoff_time = datetime.now() - timedelta(hours=4)
                                    if update_time > cutoff_time:
                                        print(f"DEBUG: Skipping daily consumption for {stock_item.get('item_name')} due to recent manual update")
                                        skipped_count += 1
                                        should_skip = True
                                except ValueError:
                                    pass
                
                if should_skip:
                    continue
                
                # Apply daily consumption
                current_stock = stock_item.get("current_stock", 0.0)
                new_stock = max(0.0, current_stock - daily_amount)
                
                # Update stock
                self.client.table("stock_items").update({
                    "current_stock": new_stock,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", stock_item["id"]).execute()
                
                # Create transaction record
                transaction_data = {
                    "stock_item_id": stock_item["id"],
                    "transaction_type": "daily_consumption",
                    "old_stock": current_stock,
                    "new_stock": new_stock,
                    "change_amount": -daily_amount,
                    "reason": "daily_consumption",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.client.table("stock_transactions").insert(transaction_data).execute()
                
                updated_count += 1
            
            return {
                "success": True,
                "message": f"Daily consumption applied to {updated_count} items, {skipped_count} skipped due to recent manual updates",
                "updated_count": updated_count,
                "skipped_count": skipped_count
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error applying daily consumption: {str(e)}"}
    
    def clear_manual_update_flags(self) -> Dict[str, Any]:
        """Clear manual update flags to allow daily consumption for all items"""
        try:
            update_response = self.client.table("manual_updates").update({
                "manual_update_flag": False
            }).execute()
            
            if update_response.data:
                cleared_count = len(update_response.data)
                return {
                    "success": True,
                    "message": f"Manual update flags cleared for {cleared_count} items",
                    "cleared_count": cleared_count
                }
            else:
                return {"success": True, "message": "No manual update flags to clear"}
                
        except Exception as e:
            return {"success": False, "message": f"Error clearing manual flags: {str(e)}"}
    
    def migrate_from_json(self, stock_data: Dict, daily_usage_config: Dict, recipes: Dict, sales_history: Dict) -> Dict[str, Any]:
        """Migrate data from JSON files to Supabase"""
        try:
            # Clear existing data
            self.client.table("stock_transactions").delete().neq("id", 0).execute()
            self.client.table("manual_updates").delete().neq("id", 0).execute()
            self.client.table("stock_items").delete().neq("id", 0).execute()
            self.client.table("daily_usage_config").delete().neq("id", 0).execute()
            self.client.table("recipes").delete().neq("id", 0).execute()
            self.client.table("sales_history").delete().neq("id", 0).execute()
            
            # Migrate stock items
            stock_items_count = 0
            for category, items in stock_data.get("stock_data", {}).items():
                for item_name, item_data in items.items():
                    stock_item_data = {
                        "material_id": f"{category}_{item_name}",
                        "item_name": item_name,
                        "category_name": category,
                        "current_stock": item_data.get("current_stock", 0.0),
                        "min_stock": item_data.get("min_stock", 0.0),
                        "unit": item_data.get("unit", "")
                    }
                    
                    self.client.table("stock_items").insert(stock_item_data).execute()
                    stock_items_count += 1
            
            # Migrate daily usage config
            daily_config_count = 0
            # Handle the nested structure with daily_usage_config wrapper
            config_data = daily_usage_config.get("daily_usage_config", daily_usage_config)
            for category, items in config_data.items():
                for item_name, item_data in items.items():
                    material_id = f"{category}_{item_name}"
                    daily_amount = item_data.get("daily_amount", 0.0)
                    
                    config_record = {
                        "material_id": material_id,
                        "daily_amount": daily_amount,
                        "is_active": True
                    }
                    
                    self.client.table("daily_usage_config").insert(config_record).execute()
                    daily_config_count += 1
            
            # Migrate recipes
            recipes_count = 0
            # Handle the array structure with recipes wrapper
            recipes_list = recipes.get("recipes", recipes) if isinstance(recipes, dict) else recipes
            for recipe in recipes_list:
                recipe_data = {
                    "recipe_name": recipe.get("name", ""),
                    "ingredients": json.dumps(recipe.get("ingredients", []))
                }
                
                self.client.table("recipes").insert(recipe_data).execute()
                recipes_count += 1
            
            # Migrate sales history
            sales_count = 0
            # Handle the array structure with sales_records wrapper
            sales_list = sales_history.get("sales_records", sales_history) if isinstance(sales_history, dict) else sales_history
            for sale in sales_list:
                # Group sales by date and calculate totals
                date = sale.get("date", "")
                product_name = sale.get("product_name", "")
                quantity = sale.get("quantity", 0)
                
                # For now, create a simple record per sale
                sales_record = {
                    "date": date,
                    "total_sales": float(quantity),
                    "items_sold": json.dumps({product_name: quantity})
                }
                
                self.client.table("sales_history").insert(sales_record).execute()
                sales_count += 1
            
            return {
                "success": True,
                "message": f"Migration completed successfully",
                "migrated": {
                    "stock_items": stock_items_count,
                    "daily_usage_config": daily_config_count,
                    "recipes": recipes_count,
                    "sales_history": sales_count
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Migration failed: {str(e)}"}
