import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
from .sales_tracker import SalesTracker

class StockManager:
    def __init__(self):
        self.stock_file = "sample_stock.json"
        self.recipes_file = "recipes.json"
        self.stock_data = self.load_stock_data()
        self.recipes = self.load_recipes()
        self.sales_tracker = SalesTracker()
        
    def load_stock_data(self) -> Dict:
        """Load current stock data from JSON file"""
        try:
            with open(self.stock_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Stock file {self.stock_file} not found")
            return {}
            
    def load_recipes(self) -> Dict:
        """Load recipes from JSON file"""
        try:
            with open(self.recipes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Recipes file {self.recipes_file} not found")
            return {"recipes": []}
    
    def save_stock_data(self):
        """Save current stock data to JSON file"""
        try:
            with open(self.stock_file, 'w', encoding='utf-8') as f:
                json.dump(self.stock_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving stock data: {e}")
            return False
    
    def get_stock_list(self) -> List[Dict]:
        """Get formatted stock list for frontend"""
        stock_list = []
        
        for category, items in self.stock_data.get("stock_data", {}).items():
            for item_name, item_data in items.items():
                stock_list.append({
                    "id": f"{category}_{item_name}",
                    "name": item_name,
                    "category": category,
                    "current_stock": item_data.get("current_stock", 0),
                    "min_stock": item_data.get("min_stock_level", 0),
                    "unit": item_data.get("unit", ""),
                    "package_size": item_data.get("package_size", 0),
                    "package_unit": item_data.get("package_unit", ""),
                    "cost_per_unit": item_data.get("cost_per_unit", 0.0),
                    "is_ready_made": item_data.get("is_ready_made", False),
                    "usage_per_order": item_data.get("usage_per_order", 0),
                    "usage_per_day": item_data.get("usage_per_day", 0),
                    "usage_type": item_data.get("usage_type", "")
                })
        
        return stock_list
    
    def find_recipe_by_name(self, product_name: str) -> Optional[Dict]:
        """Find recipe by product name"""
        for recipe in self.recipes.get("recipes", []):
            if recipe["name"] == product_name:
                return recipe
        return None
    
    def update_stock_for_recipe(self, product_name: str, quantity: int) -> Dict:
        """Update stock based on recipe ingredients or direct consumption for ready-made products"""
        recipe = self.find_recipe_by_name(product_name)
        if not recipe:
            return {"success": False, "message": f"Recipe not found for {product_name}"}
        
        if recipe.get("product_type") == "ready_made":
            # Ready-made products consume their own stock directly
            stock_item = self.find_stock_item(product_name)
            if not stock_item:
                return {"success": False, "message": f"Ready-made product {product_name} not found in stock"}
            
            # Check if we have enough stock
            if stock_item["current_stock"] < quantity:
                return {"success": False, "message": f"Insufficient stock for {product_name}: need {quantity}, have {stock_item['current_stock']}"}
            
            # Update ready-made product stock directly
            old_stock = stock_item["current_stock"]
            stock_item["current_stock"] -= quantity
            
            if self.save_stock_data():
                return {
                    "success": True,
                    "message": f"Ready-made product {product_name} stock updated: {old_stock} → {stock_item['current_stock']}",
                    "consumed_items": [{
                        "name": product_name,
                        "consumed": quantity,
                        "unit": stock_item.get("unit", "adet"),
                        "old_stock": old_stock,
                        "new_stock": stock_item["current_stock"]
                    }]
                }
            else:
                return {"success": False, "message": "Failed to save stock data"}
        
        # Process recipe-based products (existing logic)
        consumed_items = []
        errors = []
        
        for ingredient in recipe.get("ingredients", []):
            ingredient_name = ingredient["name"]
            required_amount = ingredient["quantity"] * quantity
            unit = ingredient["unit"]
            
            # Find the ingredient in stock
            stock_item = self.find_stock_item(ingredient_name)
            if not stock_item:
                errors.append(f"Ingredient {ingredient_name} not found in stock")
                continue
            
            # Check if we have enough stock
            if stock_item["current_stock"] < required_amount:
                errors.append(f"Insufficient stock for {ingredient_name}: need {required_amount} {unit}, have {stock_item['current_stock']} {unit}")
                continue
            
            # Update stock
            old_stock = stock_item["current_stock"]
            stock_item["current_stock"] -= required_amount
            consumed_items.append({
                "name": ingredient_name,
                "consumed": required_amount,
                "unit": unit,
                "old_stock": old_stock,
                "new_stock": stock_item["current_stock"]
            })
        
        if errors:
            return {"success": False, "message": "Stock update failed", "errors": errors}
        
        # Save updated stock data
        if self.save_stock_data():
            return {
                "success": True, 
                "message": f"Stock updated for {quantity}x {product_name}",
                "consumed_items": consumed_items
            }
        else:
            return {"success": False, "message": "Failed to save stock data"}
    
    def find_stock_item(self, item_name: str) -> Optional[Dict]:
        """Find stock item by name across all categories (case-insensitive)"""
        # Normalize Turkish characters and make case-insensitive
        normalized_search = item_name.upper().replace('İ', 'I').replace('Ğ', 'G').replace('Ü', 'U').replace('Ş', 'S').replace('Ö', 'O').replace('Ç', 'C')
        
        for category, items in self.stock_data.get("stock_data", {}).items():
            for stock_name, stock_data in items.items():
                normalized_stock = stock_name.upper().replace('İ', 'I').replace('Ğ', 'G').replace('Ü', 'U').replace('Ş', 'S').replace('Ö', 'O').replace('Ç', 'C')
                if normalized_search == normalized_stock:
                    return stock_data
        return None
    
    def process_daily_consumables(self) -> Dict:
        """Process daily fixed consumables (napkins, garbage bags, etc.)"""
        consumed_items = []
        errors = []
        
        for category, items in self.stock_data.get("stock_data", {}).items():
            for item_name, item_data in items.items():
                if item_data.get("usage_type") == "gunluk":
                    usage_per_day = item_data.get("usage_per_day", 0)
                    if usage_per_day > 0:
                        current_stock = item_data.get("current_stock", 0)
                        if current_stock >= usage_per_day:
                            old_stock = current_stock
                            item_data["current_stock"] -= usage_per_day
                            consumed_items.append({
                                "name": item_name,
                                "consumed": usage_per_day,
                                "unit": item_data.get("unit", ""),
                                "old_stock": old_stock,
                                "new_stock": item_data["current_stock"]
                            })
                        else:
                            errors.append(f"Insufficient stock for daily consumption: {item_name}")
        
        if errors:
            return {"success": False, "message": "Daily consumption processing failed", "errors": errors}
        
        # Save updated stock data
        if self.save_stock_data():
            return {
                "success": True,
                "message": "Daily consumables processed",
                "consumed_items": consumed_items
            }
        else:
            return {"success": False, "message": "Failed to save stock data"}
    
    def get_stock_alerts(self) -> List[Dict]:
        """Get stock alerts for items below minimum levels"""
        alerts = []
        
        for category, items in self.stock_data.get("stock_data", {}).items():
            for item_name, item_data in items.items():
                current_stock = item_data.get("current_stock", 0)
                min_stock = item_data.get("min_stock_level", 0)
                
                if current_stock <= min_stock:
                    alert_type = "out_of_stock" if current_stock == 0 else "low_stock"
                    message = f"{item_name} is {'out of stock' if current_stock == 0 else 'below minimum level'}"
                    
                    alerts.append({
                        "material_id": f"{category}_{item_name}",
                        "material_name": item_name,
                        "current_stock": current_stock,
                        "min_stock": min_stock,
                        "alert_type": alert_type,
                        "message": message,
                        "category": category
                    })
        
        return alerts
    
    def update_stock_manually(self, material_id: str, new_stock: float, reason: str = "manual_update") -> Dict:
        """Manually update stock for a specific item"""
        try:
            # Find the item by ID across all categories
            item_found = False
            for category, items in self.stock_data.get("stock_data", {}).items():
                for item_name, item_data in items.items():
                    if f"{category}_{item_name}" == material_id:
                        old_stock = item_data["current_stock"]
                        item_data["current_stock"] = new_stock
                        item_data["last_updated"] = datetime.now().isoformat()
                        item_found = True
                        break
                if item_found:
                    break
            
            if not item_found:
                return {"success": False, "message": f"Item with ID {material_id} not found"}
            
            if self.save_stock_data():
                return {
                    "success": True,
                    "message": f"Stock updated successfully",
                    "old_stock": old_stock,
                    "new_stock": new_stock,
                    "reason": reason
                }
            else:
                return {"success": False, "message": "Failed to save stock data"}
                
        except Exception as e:
            return {"success": False, "message": f"Error updating stock: {str(e)}"}
    
    def process_sales_excel(self, excel_file_path: str) -> Dict:
        """Process sales Excel file and update stock accordingly"""
        try:
            # Read Excel file
            df = pd.read_excel(excel_file_path)
            
            if df.empty:
                return {"success": False, "message": "Excel file is empty"}
            
            # Process each sale
            processed_sales = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Handle multiple possible column names for product and quantity
                    product_name = str(row.get('Product', row.get('Ürün', row.get('Ürün Adı', '')))).strip()
                    quantity = int(row.get('Quantity', row.get('Miktar', row.get('Adet', 1))))
                    
                    if not product_name or quantity <= 0:
                        continue
                    
                    # Debug: Print what we're processing
                    print(f"Processing: '{product_name}' (quantity: {quantity})")
                    
                    # Update stock for this product
                    result = self.update_stock_for_recipe(product_name, quantity)
                    
                    if result["success"]:
                        processed_sales.append({
                            "product": product_name,
                            "quantity": quantity,
                            "status": "success",
                            "message": result["message"]
                        })
                    else:
                        errors.append(f"Row {index + 1}: {result['message']}")
                        processed_sales.append({
                            "product": product_name,
                            "quantity": quantity,
                            "status": "failed",
                            "message": result["message"]
                        })
                        
                except Exception as e:
                    errors.append(f"Row {index + 1}: Error processing - {str(e)}")
                    continue
            
            # Track sales data for analytics
            try:
                # Extract successful sales for tracking
                successful_sales = [
                    {"product_name": sale["product"], "quantity": sale["quantity"]}
                    for sale in processed_sales if sale["status"] == "success"
                ]
                
                if successful_sales:
                    self.sales_tracker.add_bulk_sales(successful_sales)
                    print(f"Added {len(successful_sales)} sales records to analytics")
            except Exception as e:
                print(f"Warning: Could not track sales data: {e}")
            
            # Process daily consumables
            daily_result = self.process_daily_consumables()
            if not daily_result["success"]:
                errors.extend(daily_result.get("errors", []))
            
            return {
                "success": True,
                "message": f"Excel processed successfully! {len(processed_sales)} sales records processed.",
                "processed_sales": processed_sales,
                "errors": errors,
                "daily_consumption": daily_result
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error processing Excel file: {str(e)}"}
    
    def get_stock_summary(self) -> Dict:
        """Get summary statistics for stock"""
        total_items = 0
        low_stock_items = 0
        out_of_stock_items = 0
        total_value = 0.0
        
        for category, items in self.stock_data.get("stock_data", {}).items():
            for item_name, item_data in items.items():
                total_items += 1
                current_stock = item_data.get("current_stock", 0)
                min_stock = item_data.get("min_stock_level", 0)
                cost_per_unit = item_data.get("cost_per_unit", 0.0)
                
                if current_stock == 0:
                    out_of_stock_items += 1
                elif current_stock <= min_stock:
                    low_stock_items += 1
                
                total_value += current_stock * cost_per_unit
        
        return {
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "total_value": total_value,
            "last_updated": datetime.now().isoformat()
        }
    
    def apply_daily_consumption(self) -> Dict:
        """Apply daily consumption for raw materials based on daily_usage_config.json"""
        try:
            # Load daily usage configuration
            config_file = "daily_usage_config.json"
            if not os.path.exists(config_file):
                return {"success": False, "message": f"Daily usage config file {config_file} not found"}
            
            with open(config_file, 'r', encoding='utf-8') as f:
                daily_config = json.load(f)
            
            consumed_items = []
            errors = []
            total_consumed = 0
            
            # Process each category of daily consumption
            for category_name, category_items in daily_config.get("daily_usage_config", {}).items():
                for item_name, item_config in category_items.items():
                    daily_amount = item_config.get("daily_amount", 0)
                    unit = item_config.get("unit", "")
                    config_category = item_config.get("category", "")
                    
                    if daily_amount <= 0:
                        continue
                    
                    # Find the item in stock
                    stock_item = self.find_stock_item(item_name)
                    if not stock_item:
                        errors.append(f"Item {item_name} not found in stock")
                        continue
                    
                    # Check if we have enough stock
                    current_stock = stock_item.get("current_stock", 0)
                    if current_stock < daily_amount:
                        # If not enough stock, consume what's available (but don't go below 0)
                        if current_stock > 0:
                            consumed_amount = current_stock
                            old_stock = current_stock
                            stock_item["current_stock"] = 0
                            consumed_items.append({
                                "name": item_name,
                                "category": config_category,
                                "consumed": consumed_amount,
                                "unit": unit,
                                "old_stock": old_stock,
                                "new_stock": 0,
                                "description": f"{item_config.get('description', 'Daily consumption')} (partial - limited stock)",
                                "partial_consumption": True
                            })
                            total_consumed += 1
                        else:
                            errors.append(f"No stock available for {item_name}")
                        continue
                    
                    # Update stock (normal consumption)
                    old_stock = current_stock
                    stock_item["current_stock"] -= daily_amount
                    consumed_items.append({
                        "name": item_name,
                        "category": config_category,
                        "consumed": daily_amount,
                        "unit": unit,
                        "old_stock": old_stock,
                        "new_stock": stock_item["current_stock"],
                        "description": item_config.get("description", "Daily consumption")
                    })
                    total_consumed += 1
            
            # Save updated stock data
            if self.save_stock_data():
                partial_count = len([item for item in consumed_items if item.get("partial_consumption", False)])
                if partial_count > 0:
                    message = f"Daily consumption applied! {total_consumed} items processed ({partial_count} with partial consumption due to limited stock)."
                else:
                    message = f"Daily consumption applied successfully! {total_consumed} items consumed."
                
                return {
                    "success": True,
                    "message": message,
                    "consumed_items": consumed_items,
                    "total_consumed": total_consumed,
                    "partial_consumption_count": partial_count
                }
            else:
                return {"success": False, "message": "Failed to save stock data"}
                
        except Exception as e:
            return {"success": False, "message": f"Error applying daily consumption: {str(e)}"}
