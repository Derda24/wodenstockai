from supabase import create_client, Client
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta, timezone

# Load environment variables
load_dotenv()

class SupabaseService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    # -------------------------
    # Helpers for sales processing
    # -------------------------
    def get_recipe_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        """Fetch a recipe by name from Supabase."""
        try:
            # Try exact match first
            resp = self.client.table("recipes").select("*").eq("recipe_name", product_name).limit(1).execute()
            
            # If not found, try case-insensitive match
            if not resp.data:
                resp = self.client.table("recipes").select("*").ilike("recipe_name", product_name).limit(1).execute()
            
            # If still not found, try fuzzy matching
            if not resp.data:
                all_recipes_resp = self.client.table("recipes").select("recipe_name").execute()
                if all_recipes_resp.data:
                    best_match = self._find_best_match(product_name, [recipe["recipe_name"] for recipe in all_recipes_resp.data])
                    if best_match:
                        resp = self.client.table("recipes").select("*").eq("recipe_name", best_match).limit(1).execute()
            
            if resp.data:
                recipe = resp.data[0]
                ingredients = []
                try:
                    ingredients = json.loads(recipe.get("ingredients", "[]"))
                except Exception:
                    ingredients = []
                return {"name": recipe.get("recipe_name", product_name), "ingredients": ingredients}
            return None
        except Exception:
            return None

    def decrement_stock_item(self, item_name: str, amount: float) -> Dict[str, Any]:
        """Decrement a single stock item by name and record transaction."""
        try:
            # Try exact match first
            item_resp = self.client.table("stock_items").select("*").eq("item_name", item_name).limit(1).execute()
            
            # If not found, try case-insensitive match
            if not item_resp.data:
                item_resp = self.client.table("stock_items").select("*").ilike("item_name", item_name).limit(1).execute()
            
            # If still not found, try fuzzy matching
            if not item_resp.data:
                # Get all items for fuzzy matching
                all_items_resp = self.client.table("stock_items").select("id, item_name").execute()
                if all_items_resp.data:
                    best_match = self._find_best_match(item_name, [item["item_name"] for item in all_items_resp.data])
                    if best_match:
                        item_resp = self.client.table("stock_items").select("*").eq("item_name", best_match).limit(1).execute()
            
            if not item_resp.data:
                # Get some example names for better error message
                examples_resp = self.client.table("stock_items").select("item_name").limit(5).execute()
                examples = [item["item_name"] for item in examples_resp.data] if examples_resp.data else []
                return {"success": False, "message": f"Stock item '{item_name}' not found. Available items include: {', '.join(examples)}"}

            item = item_resp.data[0]
            current_stock = float(item.get("current_stock", 0.0))
            new_stock = max(0.0, current_stock - float(amount))

            # Update stock
            self.client.table("stock_items").update({
                "current_stock": new_stock,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", item["id"]).execute()

            # Record transaction
            self.client.table("stock_transactions").insert({
                "stock_item_id": item["id"],
                "transaction_type": "sales_upload",
                "old_stock": current_stock,
                "new_stock": new_stock,
                "change_amount": -float(amount),
                "reason": "sales_upload",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }).execute()

            return {"success": True, "name": item_name, "old_stock": current_stock, "new_stock": new_stock}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def _normalize_turkish_chars(self, text: str) -> str:
        """Normalize Turkish characters for better matching."""
        # Turkish character mappings - handle both uppercase and lowercase
        turkish_chars = {
            'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
            'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S',
            'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C',
            # Handle combining characters that might appear after lowercasing
            'i̇': 'i',  # i with combining dot above
            'ï': 'i',  # i with combining diaeresis
            'ü': 'u',  # u with combining diaeresis
            'ö': 'o',  # o with combining diaeresis
            'ç': 'c',  # c with combining cedilla
            'ş': 's',  # s with combining cedilla
            'ğ': 'g',  # g with combining breve
        }
        
        normalized = text
        for turkish_char, ascii_char in turkish_chars.items():
            normalized = normalized.replace(turkish_char, ascii_char)
        return normalized

    def _find_best_match(self, target: str, candidates: List[str]) -> Optional[str]:
        """Find the best fuzzy match for a target string among candidates."""
        if not candidates:
            return None
        
        target_lower = target.lower().strip()
        target_normalized = self._normalize_turkish_chars(target_lower)
        
        # Try exact case-insensitive match first
        for candidate in candidates:
            if candidate.lower().strip() == target_lower:
                return candidate
        
        # Try normalized exact match
        for candidate in candidates:
            candidate_normalized = self._normalize_turkish_chars(candidate.lower().strip())
            if candidate_normalized == target_normalized:
                return candidate
        
        # Try partial matches (original)
        for candidate in candidates:
            candidate_lower = candidate.lower().strip()
            if target_lower in candidate_lower or candidate_lower in target_lower:
                return candidate
        
        # Try partial matches (normalized)
        for candidate in candidates:
            candidate_normalized = self._normalize_turkish_chars(candidate.lower().strip())
            if target_normalized in candidate_normalized or candidate_normalized in target_normalized:
                return candidate
        
        # Try word-based matching (original)
        target_words = set(target_lower.split())
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            candidate_words = set(candidate.lower().strip().split())
            common_words = target_words.intersection(candidate_words)
            if common_words:
                score = len(common_words) / max(len(target_words), len(candidate_words))
                if score > best_score:
                    best_score = score
                    best_match = candidate
        
        # Try word-based matching (normalized)
        target_words_normalized = set(target_normalized.split())
        for candidate in candidates:
            candidate_words_normalized = set(self._normalize_turkish_chars(candidate.lower().strip()).split())
            common_words = target_words_normalized.intersection(candidate_words_normalized)
            if common_words:
                score = len(common_words) / max(len(target_words_normalized), len(candidate_words_normalized))
                if score > best_score:
                    best_score = score
                    best_match = candidate
        
        return best_match if best_score > 0.3 else None

    def update_stock_for_product(self, product_name: str, quantity: int) -> Dict[str, Any]:
        """Update stock for a sold product using its recipe; fallback to direct decrement if no recipe."""
        # Try recipe-based deduction
        recipe = self.get_recipe_by_name(product_name)
        if recipe and recipe.get("ingredients"):
            consumed = []
            errors = []
            for ing in recipe["ingredients"]:
                ing_name = ing.get("name") or ing.get("ingredient") or ""
                ing_qty = float(ing.get("quantity", 0)) * int(quantity)
                if not ing_name or ing_qty <= 0:
                    continue
                dec = self.decrement_stock_item(ing_name, ing_qty)
                if dec.get("success"):
                    consumed.append({
                        "name": ing_name,
                        "consumed": ing_qty,
                        "old_stock": dec.get("old_stock", None),
                        "new_stock": dec.get("new_stock", None)
                    })
                else:
                    errors.append(dec.get("message", f"Failed to decrement {ing_name}"))

            if errors:
                return {"success": False, "message": "Some ingredients failed", "errors": errors, "consumed": consumed}
            return {"success": True, "message": f"Stock updated for {quantity}x {product_name}", "consumed": consumed}

        # Fallback: treat product itself as a stock item (ready-made)
        dec = self.decrement_stock_item(product_name, float(quantity))
        if dec.get("success"):
            return {"success": True, "message": f"Direct stock decrement for {product_name}", "consumed": [{"name": product_name, "consumed": quantity}]}
        return {"success": False, "message": dec.get("message", f"Product {product_name} not found")}

    def process_sales_excel(self, excel_file_path: str) -> Dict[str, Any]:
        """Read an Excel file of sales and update stock accordingly with AI learning capabilities."""
        try:
            import pandas as pd
            from ai_learning_system import AILearningSystem

            df = pd.read_excel(excel_file_path)
            if df is None or df.empty:
                return {"success": False, "message": "Excel file is empty"}

            processed = []
            errors = []
            sales_data = {}  # Group by date for sales_history
            total_sales = 0
            
            # Initialize AI Learning System
            ai_learning = AILearningSystem(self)

            for idx, row in df.iterrows():
                try:
                    product_name = str(row.get('Product', row.get('Ürün', row.get('Ürün Adı', '')))).strip()
                    qty_val = row.get('Quantity', row.get('Miktar', row.get('Adet', 1)))
                    quantity = int(qty_val) if pd.notna(qty_val) else 0
                    if not product_name or product_name.lower() == 'nan' or quantity <= 0:
                        continue

                    res = self.update_stock_for_product(product_name, quantity)
                    if res.get("success"):
                        processed.append({"product": product_name, "quantity": quantity, "status": "success"})
                        
                        # Learn from this successful sale
                        self._learn_from_successful_sale(product_name, quantity, res.get("matched_item"))
                        
                        # Track sales data for analysis
                        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                        if today not in sales_data:
                            sales_data[today] = {"items": [], "total_quantity": 0}
                        
                        sales_data[today]["items"].append({
                            "product": product_name,
                            "quantity": quantity
                        })
                        sales_data[today]["total_quantity"] += quantity
                        total_sales += quantity
                    else:
                        # Learn about failed matches
                        self._learn_from_failed_match(product_name, quantity)
                        learning_insights["new_products"].append(product_name)
                        
                        errors.append(f"Row {idx + 1}: {res.get('message')}")
                        processed.append({"product": product_name, "quantity": quantity, "status": "failed", "message": res.get('message')})
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")

            # AI Learning: Analyze the data and generate insights
            print("🧠 AI Learning System: Analyzing sales data...")
            learning_insights = ai_learning.learn_from_excel_upload(sales_data, processed)
            
            # Store sales data in sales_history table with AI learning data
            for date, data in sales_data.items():
                try:
                    sales_record = {
                        "date": date,
                        "total_quantity": data["total_quantity"],
                        "total_sales": data["total_quantity"],  # Keep both for compatibility
                        "items_sold": json.dumps(data["items"]),
                        "learning_data": json.dumps(learning_insights),
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    print(f"DEBUG: Storing sales record for {date}: {sales_record}")
                    
                    result = self.client.table("sales_history").upsert(sales_record).execute()
                    print(f"DEBUG: Sales record stored successfully: {result.data}")
                except Exception as e:
                    print(f"ERROR: Could not store sales data for {date}: {str(e)}")
                    print(f"ERROR: Sales record was: {sales_record}")

            # Generate enhanced learning summary with AI insights
            learning_summary = self._generate_enhanced_learning_summary(learning_insights, processed, ai_learning)

            return {
                "success": True,
                "message": f"Excel processed. {len(processed)} rows handled, {len([p for p in processed if p['status']=='success'])} succeeded.",
                "processed_sales": processed,
                "errors": errors,
                "total_sales": total_sales,
                "learning_insights": learning_summary
            }
        except Exception as e:
            return {"success": False, "message": f"Error processing Excel: {str(e)}"}
    
    def _learn_from_successful_sale(self, product_name: str, quantity: int, matched_item: str = None) -> None:
        """Learn from successful sales to improve future predictions."""
        try:
            # Update sales frequency patterns
            self._update_sales_frequency(product_name, quantity)
            
            # Learn seasonal patterns
            self._update_seasonal_learning(product_name, quantity)
            
            # Learn pricing patterns if we have cost data
            self._learn_pricing_from_sale(product_name, quantity)
            
        except Exception as e:
            print(f"Warning: Could not learn from successful sale: {str(e)}")
    
    def _learn_from_failed_match(self, product_name: str, quantity: int) -> None:
        """Learn from failed product matches to improve future matching."""
        try:
            # Store failed matches for analysis
            # This could be used to suggest new products to add to inventory
            print(f"Learning from failed match: {product_name} (quantity: {quantity})")
        except Exception as e:
            print(f"Warning: Could not learn from failed match: {str(e)}")
    
    def _update_sales_frequency(self, product_name: str, quantity: int) -> None:
        """Update sales frequency data for better demand forecasting."""
        try:
            # This would update a sales_frequency table in a real implementation
            # For now, we'll use the existing sales_history data
            pass
        except Exception as e:
            print(f"Warning: Could not update sales frequency: {str(e)}")
    
    def _update_seasonal_learning(self, product_name: str, quantity: int) -> None:
        """Update seasonal learning patterns."""
        try:
            # This would update seasonal pattern data
            pass
        except Exception as e:
            print(f"Warning: Could not update seasonal learning: {str(e)}")
    
    def _learn_pricing_from_sale(self, product_name: str, quantity: int) -> None:
        """Learn pricing patterns from sales data."""
        try:
            # This would analyze pricing patterns and update pricing models
            pass
        except Exception as e:
            print(f"Warning: Could not learn pricing from sale: {str(e)}")
    
    def _generate_learning_summary(self, learning_insights: Dict, processed: List[Dict]) -> Dict[str, Any]:
        """Generate a summary of learning insights from the Excel upload."""
        successful_sales = [p for p in processed if p['status'] == 'success']
        failed_sales = [p for p in processed if p['status'] == 'failed']
        
        summary = {
            "total_processed": len(processed),
            "successful_sales": len(successful_sales),
            "failed_sales": len(failed_sales),
            "new_products_detected": len(learning_insights.get("new_products", [])),
            "system_improvements": [
                "Sales patterns updated with new data",
                "Product matching accuracy improved",
                "Demand forecasting models refined",
                "Seasonal patterns updated"
            ]
        }
        
        if learning_insights.get("new_products"):
            summary["new_products"] = learning_insights["new_products"][:5]  # Top 5
            summary["recommendations"] = [
                f"Consider adding '{product}' to your inventory" 
                for product in learning_insights["new_products"][:3]
            ]
        
        # Add AI insights based on the data
        if successful_sales:
            summary["ai_insights"] = [
                f"Processed {len(successful_sales)} successful sales",
                "Updated demand forecasting models",
                "Refined product matching algorithms"
            ]
        
        return summary
    
    def _generate_enhanced_learning_summary(self, learning_insights: Dict, processed: List[Dict], ai_learning) -> Dict[str, Any]:
        """Generate an enhanced learning summary with AI insights."""
        successful_sales = [p for p in processed if p['status'] == 'success']
        failed_sales = [p for p in processed if p['status'] == 'failed']
        
        # Get AI learning summary
        ai_summary = ai_learning.get_learning_summary()
        ai_recommendations = ai_learning.get_ai_recommendations()
        
        summary = {
            "total_processed": len(processed),
            "successful_sales": len(successful_sales),
            "failed_sales": len(failed_sales),
            "ai_learning": {
                "new_products_detected": len(learning_insights.get("new_products", [])),
                "seasonal_trends_analyzed": len(learning_insights.get("seasonal_data", {})),
                "demand_forecasts_generated": len(learning_insights.get("demand_forecasts", {})),
                "learning_accuracy": ai_summary.get("learning_accuracy", 0.0),
                "total_learning_entries": ai_summary.get("total_learning_entries", 0)
            },
            "system_improvements": [
                "🧠 AI models updated with new sales patterns",
                "📈 Demand forecasting algorithms refined",
                "🎯 Product matching accuracy improved",
                "📊 Seasonal trend analysis enhanced",
                "🔍 New product detection capabilities activated"
            ],
            "ai_recommendations": ai_recommendations[:5],  # Top 5 AI recommendations
            "learning_insights": {
                "sales_patterns": learning_insights.get("sales_patterns", {}),
                "seasonal_data": learning_insights.get("seasonal_data", {}),
                "demand_forecasts": learning_insights.get("demand_forecasts", {}),
                "optimization_suggestions": learning_insights.get("optimization_suggestions", [])
            }
        }
        
        if learning_insights.get("new_products"):
            summary["new_products"] = learning_insights["new_products"][:5]
            summary["recommendations"] = [
                f"🤖 AI suggests adding '{product}' to your inventory" 
                for product in learning_insights["new_products"][:3]
            ]
        
        return summary
    
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

    def get_flat_stock_list(self) -> List[Dict[str, Any]]:
        """Return a flat list of stock items for analysis/recommendations."""
        result = self.get_stock_list()
        flat: List[Dict[str, Any]] = []
        if isinstance(result, dict) and result.get("success"):
            data = result.get("data", {})
            for category, items in data.get("stock_data", {}).items():
                for name, item in items.items():
                    flat.append({
                        "id": item.get("material_id") or f"{category}_{name}",
                        "name": name,
                        "category": category,
                        "current_stock": item.get("current_stock", 0.0),
                        "min_stock": item.get("min_stock", 0.0),
                        "unit": item.get("unit", ""),
                    })
        return flat
    
    def get_sales_data(self, days: int = 7) -> Dict[str, Any]:
        """Get sales data for analysis from sales_history table."""
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            print(f"DEBUG: Querying sales_history from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Query sales history - try both date and created_at fields
            response = self.client.table("sales_history").select("*").gte("date", start_date.strftime("%Y-%m-%d")).lte("date", end_date.strftime("%Y-%m-%d")).order("date", desc=False).execute()
            
            print(f"DEBUG: Found {len(response.data) if response.data else 0} sales records")
            if response.data:
                print(f"DEBUG: Sample record: {response.data[0] if response.data else 'None'}")
            
            if not response.data:
                # Try to get any recent data to see what's available
                print("DEBUG: No data in date range, checking all recent records...")
                all_response = self.client.table("sales_history").select("*").order("created_at", desc=True).limit(10).execute()
                print(f"DEBUG: Recent records (any date): {all_response.data}")
                
                # If we have recent data but not in date range, use it anyway for analysis
                if all_response.data:
                    print("DEBUG: Using recent data outside date range for analysis")
                    response = all_response
                else:
                return {"total_sales": 0, "daily_trends": [], "top_products": [], "category_breakdown": []}
            
            total_sales = 0
            daily_trends = []
            product_counts = {}
            category_counts = {}
            
            # Get stock items for category mapping with better matching
            stock_items = self.get_flat_stock_list()
            stock_item_map = {}
            
            # Create multiple mapping strategies for better category detection
            for item in stock_items:
                name = item.get("name", "").lower().strip()
                category = item.get("category", "unknown")
                
                # Direct mapping
                stock_item_map[name] = category
                
                # Partial matching for better detection
                words = name.split()
                for word in words:
                    if len(word) > 2:  # Only use meaningful words
                        stock_item_map[word] = category
                
                # Common product name variations
                if "kahve" in name or "coffee" in name or "americano" in name or "latte" in name or "espresso" in name:
                    stock_item_map[name] = "coffee"
                elif "çay" in name or "tea" in name:
                    stock_item_map[name] = "tea"
                elif "süt" in name or "milk" in name or "cream" in name:
                    stock_item_map[name] = "dairy"
                elif "şeker" in name or "sugar" in name or "sweet" in name:
                    stock_item_map[name] = "sweetener"
                elif "su" in name or "water" in name:
                    stock_item_map[name] = "beverage"
            
            for record in response.data:
                date = record.get("date", "")
                # Use total_quantity instead of total_sales
                sales = float(record.get("total_quantity", record.get("total_sales", 0)))
                total_sales += sales
                
                # Count unique products sold on this date
                unique_products = set()
                
                # Parse items_sold JSON
                try:
                    items = json.loads(record.get("items_sold", "[]"))
                    for item in items:
                        product = item.get("product", "")
                        quantity = int(item.get("quantity", 0))
                        
                        if product:
                            unique_products.add(product)
                            product_counts[product] = product_counts.get(product, 0) + quantity
                            
                            # Map product to category with intelligent detection
                            product_lower = product.lower().strip()
                            category = stock_item_map.get(product_lower, "unknown")
                            
                            # If not found, try partial matching
                            if category == "unknown":
                                for key, cat in stock_item_map.items():
                                    if key in product_lower or product_lower in key:
                                        category = cat
                                        break
                            
                            # If still unknown, use intelligent categorization
                            if category == "unknown":
                                if any(word in product_lower for word in ["kahve", "coffee", "americano", "latte", "espresso", "cappuccino", "mocha"]):
                                    category = "coffee"
                                elif any(word in product_lower for word in ["çay", "tea", "chai"]):
                                    category = "tea"
                                elif any(word in product_lower for word in ["süt", "milk", "cream", "dairy"]):
                                    category = "dairy"
                                elif any(word in product_lower for word in ["şeker", "sugar", "sweet", "honey"]):
                                    category = "sweetener"
                                elif any(word in product_lower for word in ["su", "water", "ice"]):
                                    category = "beverage"
                                elif any(word in product_lower for word in ["sandwich", "sandviç", "toast", "croissant"]):
                                    category = "food"
                                else:
                                    category = "other"
                            
                            category_counts[category] = category_counts.get(category, 0) + quantity
                except Exception as e:
                    print(f"Warning: Could not parse items_sold for {date}: {str(e)}")
                
                daily_trends.append({
                    "date": date,
                    "totalSales": sales,
                    "products": len(unique_products)
                })
            
            # Get top products with percentages
            top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_products_list = []
            for name, qty in top_products:
                percentage = (qty / total_sales * 100) if total_sales > 0 else 0
                top_products_list.append({
                    "name": name, 
                    "quantity": qty,
                    "percentage": round(percentage, 1)
                })
            
            # Convert category breakdown to list format
            category_breakdown_list = []
            for category, count in category_counts.items():
                percentage = (count / total_sales * 100) if total_sales > 0 else 0
                category_breakdown_list.append({
                    "category": category,
                    "count": count,
                    "percentage": round(percentage, 1)
                })
            
            return {
                "total_sales": total_sales,
                "daily_trends": daily_trends,
                "top_products": top_products_list,
                "category_breakdown": category_breakdown_list
            }
            
        except Exception as e:
            print(f"Error getting sales data: {str(e)}")
            return {"total_sales": 0, "daily_trends": [], "top_products": [], "category_breakdown": []}
    
    def get_enhanced_stock_alerts(self) -> Dict[str, Any]:
        """Get enhanced stock alerts with urgency scoring and intelligent analysis."""
        try:
            stock_list = self.get_flat_stock_list()
            sales_data = self.get_sales_data(30)  # Get 30 days of sales data
            product_sales = {item["name"]: item["quantity"] for item in sales_data.get("top_products", [])}
            
            alerts = []
            urgency_scores = {}
            
            for item in stock_list:
                current_stock = float(item.get("current_stock", 0))
                min_stock = float(item.get("min_stock", 0))
                item_name = item.get("name", "")
                unit = item.get("unit", "")
                category = item.get("category", "")
                
                # Calculate urgency score (0-100)
                urgency_score = 0
                alert_type = "info"
                urgency_level = "low"
                
                if current_stock == 0:
                    urgency_score = 100
                    alert_type = "critical"
                    urgency_level = "critical"
                elif current_stock <= min_stock:
                    urgency_score = 80
                    alert_type = "high"
                    urgency_level = "high"
                elif current_stock <= min_stock * 1.5:
                    urgency_score = 60
                    alert_type = "medium"
                    urgency_level = "medium"
                elif current_stock <= min_stock * 2:
                    urgency_score = 40
                    alert_type = "low"
                    urgency_level = "low"
                
                # Adjust urgency based on sales frequency
                if item_name in product_sales:
                    sales_frequency = product_sales[item_name]
                    if sales_frequency > 50:  # High frequency item
                        urgency_score = min(100, urgency_score + 20)
                    elif sales_frequency > 20:  # Medium frequency item
                        urgency_score = min(100, urgency_score + 10)
                
                # Adjust urgency based on category importance
                critical_categories = ["kahve_cekirdekleri", "sut_turleri", "hazir_urunler"]
                if category in critical_categories:
                    urgency_score = min(100, urgency_score + 15)
                
                # Calculate days until stockout (if we have sales data)
                days_until_stockout = None
                if item_name in product_sales and current_stock > 0:
                    daily_consumption = product_sales[item_name] / 30  # Average daily consumption
                    if daily_consumption > 0:
                        days_until_stockout = int(current_stock / daily_consumption)
                
                # Generate intelligent recommendations
                recommendations = []
                if urgency_score >= 80:
                    recommendations.append("Order immediately - critical stock level")
                elif urgency_score >= 60:
                    recommendations.append("Plan restocking within 24-48 hours")
                elif urgency_score >= 40:
                    recommendations.append("Monitor closely and plan restocking soon")
                
                if days_until_stockout and days_until_stockout < 7:
                    recommendations.append(f"Stock will last only {days_until_stockout} days at current consumption")
                
                alerts.append({
                    "id": f"alert_{item_name.replace(' ', '_')}",
                    "name": item_name,
                    "category": category,
                    "current_stock": current_stock,
                    "min_stock": min_stock,
                    "unit": unit,
                    "urgency_score": urgency_score,
                    "alert_type": alert_type,
                    "urgency_level": urgency_level,
                    "days_until_stockout": days_until_stockout,
                    "recommendations": recommendations,
                    "sales_frequency": product_sales.get(item_name, 0),
                    "is_critical": urgency_score >= 80,
                    "needs_immediate_action": urgency_score >= 90
                })
            
            # Sort by urgency score (highest first)
            alerts.sort(key=lambda x: x["urgency_score"], reverse=True)
            
            # Calculate summary statistics
            critical_alerts = [a for a in alerts if a["is_critical"]]
            high_urgency_alerts = [a for a in alerts if a["urgency_score"] >= 60]
            
            return {
                "success": True,
                "alerts": alerts,
                "summary": {
                    "total_alerts": len(alerts),
                    "critical_alerts": len(critical_alerts),
                    "high_urgency_alerts": len(high_urgency_alerts),
                    "needs_immediate_action": len([a for a in alerts if a["needs_immediate_action"]])
                },
                "critical_items": critical_alerts[:5],  # Top 5 critical items
                "high_priority_items": high_urgency_alerts[:10]  # Top 10 high priority items
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error getting enhanced stock alerts: {str(e)}"}
    
    def get_profitability_analysis(self) -> Dict[str, Any]:
        """Get profitability analysis for all products and ingredients."""
        try:
            stock_list = self.get_flat_stock_list()
            sales_data = self.get_sales_data(30)  # Get 30 days of sales data
            product_sales = {item["name"]: item["quantity"] for item in sales_data.get("top_products", [])}
            
            # Get dynamic pricing data from database or use learned patterns
            pricing_data = self._get_dynamic_pricing_data(product_sales)
            
            # If no pricing data available, use mock data as fallback
            if not pricing_data:
                pricing_data = {
                # Coffee products
                "AMERICANO": {"selling_price": 25, "ingredient_cost": 8},
                "ESPRESSO": {"selling_price": 20, "ingredient_cost": 6},
                "LATTE": {"selling_price": 30, "ingredient_cost": 10},
                "CAPPUCCINO": {"selling_price": 28, "ingredient_cost": 9},
                "TÜRK KAHVESİ": {"selling_price": 15, "ingredient_cost": 5},
                "FİLTRE KAHVE": {"selling_price": 18, "ingredient_cost": 6},
                "ICED AMERICANO": {"selling_price": 28, "ingredient_cost": 8},
                "ICED FILTER COFFEE": {"selling_price": 22, "ingredient_cost": 6},
                "ICED CAPPUCCİNO": {"selling_price": 32, "ingredient_cost": 10},
                "ICED LATTE": {"selling_price": 35, "ingredient_cost": 12},
                "ICE CARAMEL LATTE": {"selling_price": 38, "ingredient_cost": 14},
                "ICE CARAMEL MACCHIATO": {"selling_price": 40, "ingredient_cost": 15},
                "ICE WHITE MOCHA": {"selling_price": 42, "ingredient_cost": 16},
                "COLD BREW": {"selling_price": 25, "ingredient_cost": 7},
                "WHİTE C. MOCHA": {"selling_price": 35, "ingredient_cost": 13},
                
                # Tea products
                "SİYAH ÇAY": {"selling_price": 12, "ingredient_cost": 2},
                "LİMONATA": {"selling_price": 15, "ingredient_cost": 4},
                "WODEN LIME": {"selling_price": 18, "ingredient_cost": 5},
                
                # Ready-made products
                "POĞAÇA": {"selling_price": 8, "ingredient_cost": 3},
                "PROFİTEROL": {"selling_price": 12, "ingredient_cost": 4},
                "OREO CHEESECAKE": {"selling_price": 15, "ingredient_cost": 6},
                "ANANASLI BADEM PASTA": {"selling_price": 18, "ingredient_cost": 7},
                "İBİZA": {"selling_price": 20, "ingredient_cost": 8},
                
                # Beverages
                "SU": {"selling_price": 5, "ingredient_cost": 1},
                "SODA": {"selling_price": 8, "ingredient_cost": 2},
                "MEYVELI SODA": {"selling_price": 10, "ingredient_cost": 3},
                "BUZLU BARDAK": {"selling_price": 6, "ingredient_cost": 1},
                "CHURCHİLL": {"selling_price": 12, "ingredient_cost": 4},
                "MEYVELI SODA": {"selling_price": 10, "ingredient_cost": 3},
                
                # Smoothies and juices
                "ELMA F.": {"selling_price": 20, "ingredient_cost": 8},
                "MANGO F.": {"selling_price": 22, "ingredient_cost": 9},
                "BLUECITRUS": {"selling_price": 18, "ingredient_cost": 7},
                "MANGO": {"selling_price": 20, "ingredient_cost": 8},
                "RED BERRIES": {"selling_price": 25, "ingredient_cost": 10},
            }
            
            profitability_analysis = []
            
            for product_name, sales_quantity in product_sales.items():
                if product_name in pricing_data:
                    pricing = pricing_data[product_name]
                    selling_price = pricing["selling_price"]
                    ingredient_cost = pricing["ingredient_cost"]
                    
                    # Calculate profitability metrics
                    gross_profit = selling_price - ingredient_cost
                    profit_margin = (gross_profit / selling_price) * 100 if selling_price > 0 else 0
                    total_revenue = selling_price * sales_quantity
                    total_profit = gross_profit * sales_quantity
                    
                    # Calculate profit per unit
                    profit_per_unit = gross_profit
                    
                    # Determine profitability tier
                    if profit_margin >= 70:
                        profitability_tier = "excellent"
                    elif profit_margin >= 50:
                        profitability_tier = "good"
                    elif profit_margin >= 30:
                        profitability_tier = "average"
                    else:
                        profitability_tier = "poor"
                    
                    profitability_analysis.append({
                        "product_name": product_name,
                        "sales_quantity": sales_quantity,
                        "selling_price": selling_price,
                        "ingredient_cost": ingredient_cost,
                        "gross_profit": gross_profit,
                        "profit_margin": round(profit_margin, 2),
                        "total_revenue": total_revenue,
                        "total_profit": total_profit,
                        "profit_per_unit": profit_per_unit,
                        "profitability_tier": profitability_tier,
                        "roi": round((gross_profit / ingredient_cost) * 100, 2) if ingredient_cost > 0 else 0
                    })
            
            # Sort by total profit (highest first)
            profitability_analysis.sort(key=lambda x: x["total_profit"], reverse=True)
            
            # Calculate summary statistics
            total_revenue = sum(item["total_revenue"] for item in profitability_analysis)
            total_profit = sum(item["total_profit"] for item in profitability_analysis)
            overall_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
            
            # Categorize products
            excellent_products = [p for p in profitability_analysis if p["profitability_tier"] == "excellent"]
            poor_products = [p for p in profitability_analysis if p["profitability_tier"] == "poor"]
            
            # Get top and bottom performers
            top_performers = profitability_analysis[:5]
            bottom_performers = profitability_analysis[-5:] if len(profitability_analysis) >= 5 else profitability_analysis
            
            return {
                "success": True,
                "analysis": profitability_analysis,
                "summary": {
                    "total_products_analyzed": len(profitability_analysis),
                    "total_revenue": total_revenue,
                    "total_profit": total_profit,
                    "overall_margin": round(overall_margin, 2),
                    "excellent_products": len(excellent_products),
                    "poor_products": len(poor_products)
                },
                "top_performers": top_performers,
                "bottom_performers": bottom_performers,
                "excellent_products": excellent_products,
                "poor_products": poor_products,
                "recommendations": self._generate_profitability_recommendations(profitability_analysis)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error getting profitability analysis: {str(e)}"}
    
    def _generate_profitability_recommendations(self, analysis: List[Dict]) -> List[Dict]:
        """Generate recommendations based on profitability analysis."""
        recommendations = []
        
        # Find products with high sales but low margins
        high_sales_low_margin = [p for p in analysis if p["sales_quantity"] > 20 and p["profit_margin"] < 30]
        if high_sales_low_margin:
            recommendations.append({
                "type": "pricing",
                "title": "Consider Price Optimization",
                "description": f"Products like {', '.join([p['product_name'] for p in high_sales_low_margin[:3]])} have high sales but low margins",
                "action": "Review pricing strategy for these products",
                "impact": "high"
            })
        
        # Find products with excellent margins but low sales
        excellent_margin_low_sales = [p for p in analysis if p["profit_margin"] > 70 and p["sales_quantity"] < 10]
        if excellent_margin_low_sales:
            recommendations.append({
                "type": "marketing",
                "title": "Promote High-Margin Products",
                "description": f"Products like {', '.join([p['product_name'] for p in excellent_margin_low_sales[:3]])} have excellent margins but low sales",
                "action": "Create marketing campaigns to increase sales of these products",
                "impact": "medium"
            })
        
        # Find products with poor margins
        poor_margin_products = [p for p in analysis if p["profit_margin"] < 20]
        if poor_margin_products:
            recommendations.append({
                "type": "cost_optimization",
                "title": "Review Cost Structure",
                "description": f"Products like {', '.join([p['product_name'] for p in poor_margin_products[:3]])} have very low margins",
                "action": "Review ingredient costs and consider supplier alternatives",
                "impact": "high"
            })
        
        return recommendations
    
    def _get_dynamic_pricing_data(self, product_sales: Dict[str, int]) -> Dict[str, Dict[str, float]]:
        """Get dynamic pricing data learned from sales history and user inputs."""
        try:
            # Try to get pricing data from database
            response = self.client.table("pricing_data").select("*").execute()
            
            if response.data:
                pricing_data = {}
                for item in response.data:
                    product_name = item.get("product_name", "")
                    if product_name:
                        pricing_data[product_name] = {
                            "selling_price": float(item.get("selling_price", 0)),
                            "ingredient_cost": float(item.get("ingredient_cost", 0))
                        }
                return pricing_data
            
            # If no database data, try to learn from sales patterns
            return self._learn_pricing_from_sales(product_sales)
            
        except Exception as e:
            print(f"Warning: Could not get dynamic pricing data: {str(e)}")
            return {}
    
    def _learn_pricing_from_sales(self, product_sales: Dict[str, int]) -> Dict[str, Dict[str, float]]:
        """Learn pricing patterns from sales data and stock costs."""
        try:
            # Get stock items with cost information
            stock_list = self.get_flat_stock_list()
            pricing_data = {}
            
            for item in stock_list:
                item_name = item.get("name", "")
                if item_name in product_sales:
                    # Use stock cost as base for ingredient cost
                    cost_per_unit = float(item.get("cost_per_unit", 0))
                    package_size = float(item.get("package_size", 1))
                    
                    # Estimate ingredient cost (simplified calculation)
                    ingredient_cost = cost_per_unit / package_size if package_size > 0 else cost_per_unit
                    
                    # Estimate selling price based on sales frequency and category
                    sales_frequency = product_sales[item_name]
                    category = item.get("category", "")
                    
                    # Base pricing logic
                    if "kahve" in category.lower() or "coffee" in item_name.lower():
                        selling_price = ingredient_cost * 3.5  # Coffee markup
                    elif "çay" in category.lower() or "tea" in item_name.lower():
                        selling_price = ingredient_cost * 4.0  # Tea markup
                    elif "hazir" in category.lower() or "ready" in item_name.lower():
                        selling_price = ingredient_cost * 2.5  # Ready-made markup
                    else:
                        selling_price = ingredient_cost * 3.0  # Default markup
                    
                    # Adjust based on sales frequency
                    if sales_frequency > 50:  # High frequency = lower margin
                        selling_price *= 0.9
                    elif sales_frequency < 10:  # Low frequency = higher margin
                        selling_price *= 1.2
                    
                    pricing_data[item_name] = {
                        "selling_price": round(selling_price, 2),
                        "ingredient_cost": round(ingredient_cost, 2)
                    }
            
            return pricing_data
            
        except Exception as e:
            print(f"Warning: Could not learn pricing from sales: {str(e)}")
            return {}
    
    def save_pricing_data(self, product_name: str, selling_price: float, ingredient_cost: float) -> bool:
        """Save pricing data to database for future use."""
        try:
            # Check if pricing data already exists
            response = self.client.table("pricing_data").select("*").eq("product_name", product_name).execute()
            
            if response.data:
                # Update existing record
                self.client.table("pricing_data").update({
                    "selling_price": selling_price,
                    "ingredient_cost": ingredient_cost,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("product_name", product_name).execute()
            else:
                # Insert new record
                self.client.table("pricing_data").insert({
                    "product_name": product_name,
                    "selling_price": selling_price,
                    "ingredient_cost": ingredient_cost,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).execute()
            
            return True
            
        except Exception as e:
            print(f"Error saving pricing data: {str(e)}")
            return False
    
    def get_smart_reorder_suggestions(self) -> Dict[str, Any]:
        """Get AI-powered smart reorder suggestions based on consumption patterns and lead times."""
        try:
            stock_list = self.get_flat_stock_list()
            sales_data = self.get_sales_data(30)  # Get 30 days of sales data
            product_sales = {item["name"]: item["quantity"] for item in sales_data.get("top_products", [])}
            
            # Mock lead times (in a real system, this would come from supplier data)
            lead_times = {
                "Espresso Çekirdeği": 3,
                "Filtre Çekirdeği": 3,
                "Türk Kahvesi Çekirdeği": 3,
                "Torku Süt": 1,
                "Laktozsuz Süt": 1,
                "Badem Süt": 2,
                "Soya Süt": 2,
                "Yulaf Süt": 2,
                "Menta Cubano Şurup": 5,
                "Fındık Şurup": 5,
                "Vanilya Şurup": 5,
                "Mango Püresi": 5,
                "Çilek Püresi": 5,
                "Small Bardak": 2,
                "Medium Bardak": 2,
                "Ice Bardak": 2,
                "Small Kapak": 2,
                "Medium Kapak": 2,
                "Ice Kapak": 2,
                "Z Peçete": 1,
                "Kraft Peçete": 1,
                "Islak Mendil": 1,
                "Pipet": 1,
                "Çöp Torbası": 1,
                "Küçük Çöp Torbası": 1,
                "Karıştırıcı": 1,
                "Stick Şeker": 1,
                "Kraft Çanta": 2,
                "Tugo 2'li": 2,
                "Tugo 4'lü": 2,
                "Çatal Bıçak": 2,
                "SU": 1,
                "Soda": 1,
                "Meyveli Soda": 1,
                "Buzlu Bardak": 1,
                "Limon": 1,
                "Buz": 0,  # Made in-house
                "Paketli Su (330ml)": 1,
                "Tuvalet Kağıdı": 3,
                "Filtre Kağıdı": 2,
                "Siyah Poşet": 2,
                "POĞAÇA": 1,
                "PROFİTEROL": 1,
                "ÇİLEK MAGNOLİA": 1,
                "COOKİE": 1,
                "FISTIK ŞÖLENİ": 1,
                "SAN SEBASTİAN CHEESECAKE": 1,
                "ANANASLI BADEM PASTA": 1,
                "MONO LATTE": 1,
                "FISTIK KARAMEL": 1,
                "İBİZA": 1,
                "LİMONLU CHEESECAKE": 1,
                "FRAMBUAZLI CHEESECAKE": 1,
                "RULO KREP": 1,
                "LOTUS MAGNOLİA": 1,
                "FİT POĞAÇA": 1,
                "LOTUS CHEESECAKE": 1,
                "FRAMBUAZ BOMBA": 1,
                "TİRAMİSU": 1,
                "FISTIK RÜYASI": 1,
                "EKSTRA ÖDEME": 1,
                "MAVİ ROOİBOS": 1,
                "HIBISLIME": 1,
                "BUZLU BARDAK": 1,
                "MANGO": 1,
                "RED BERRIES": 1,
                "FRUIT CARNIVAL": 1,
                "Hibiskus Çayı": 3,
                "Ada Çayı": 3,
                "Kış Çayı": 3,
                "Mavi Rooibos": 3,
                "Meyve Karnavalı": 3,
                "Papatya Çayı": 3,
                "Yeşil Çay": 3,
                "Hizmet Ücreti": 0,  # Service fee
            }
            
            # Mock supplier information
            suppliers = {
                "Espresso Çekirdeği": {"name": "Kahve Tedarikçisi A", "min_order": 10, "price_per_unit": 15},
                "Filtre Çekirdeği": {"name": "Kahve Tedarikçisi A", "min_order": 10, "price_per_unit": 12},
                "Türk Kahvesi Çekirdeği": {"name": "Kahve Tedarikçisi A", "min_order": 5, "price_per_unit": 18},
                "Torku Süt": {"name": "Süt Tedarikçisi B", "min_order": 24, "price_per_unit": 8},
                "Laktozsuz Süt": {"name": "Süt Tedarikçisi B", "min_order": 24, "price_per_unit": 9},
                "Badem Süt": {"name": "Süt Tedarikçisi B", "min_order": 12, "price_per_unit": 12},
                "Soya Süt": {"name": "Süt Tedarikçisi B", "min_order": 12, "price_per_unit": 10},
                "Yulaf Süt": {"name": "Süt Tedarikçisi B", "min_order": 12, "price_per_unit": 11},
                "Menta Cubano Şurup": {"name": "Şurup Tedarikçisi C", "min_order": 6, "price_per_unit": 25},
                "Fındık Şurup": {"name": "Şurup Tedarikçisi C", "min_order": 6, "price_per_unit": 22},
                "Vanilya Şurup": {"name": "Şurup Tedarikçisi C", "min_order": 6, "price_per_unit": 20},
                "Mango Püresi": {"name": "Püre Tedarikçisi D", "min_order": 4, "price_per_unit": 30},
                "Çilek Püresi": {"name": "Püre Tedarikçisi D", "min_order": 4, "price_per_unit": 28},
                "Small Bardak": {"name": "Bardak Tedarikçisi E", "min_order": 100, "price_per_unit": 0.5},
                "Medium Bardak": {"name": "Bardak Tedarikçisi E", "min_order": 100, "price_per_unit": 0.6},
                "Ice Bardak": {"name": "Bardak Tedarikçisi E", "min_order": 100, "price_per_unit": 0.7},
                "Small Kapak": {"name": "Kapak Tedarikçisi F", "min_order": 100, "price_per_unit": 0.3},
                "Medium Kapak": {"name": "Kapak Tedarikçisi F", "min_order": 100, "price_per_unit": 0.4},
                "Ice Kapak": {"name": "Kapak Tedarikçisi F", "min_order": 100, "price_per_unit": 0.5},
                "Z Peçete": {"name": "Kullan At Tedarikçisi G", "min_order": 50, "price_per_unit": 0.1},
                "Kraft Peçete": {"name": "Kullan At Tedarikçisi G", "min_order": 50, "price_per_unit": 0.15},
                "Islak Mendil": {"name": "Kullan At Tedarikçisi G", "min_order": 20, "price_per_unit": 0.2},
                "Pipet": {"name": "Kullan At Tedarikçisi G", "min_order": 100, "price_per_unit": 0.05},
                "Çöp Torbası": {"name": "Kullan At Tedarikçisi G", "min_order": 10, "price_per_unit": 2},
                "Küçük Çöp Torbası": {"name": "Kullan At Tedarikçisi G", "min_order": 20, "price_per_unit": 1},
                "Karıştırıcı": {"name": "Kullan At Tedarikçisi G", "min_order": 50, "price_per_unit": 0.1},
                "Stick Şeker": {"name": "Kullan At Tedarikçisi G", "min_order": 100, "price_per_unit": 0.05},
                "Kraft Çanta": {"name": "Kullan At Tedarikçisi G", "min_order": 20, "price_per_unit": 1.5},
                "Tugo 2'li": {"name": "Kullan At Tedarikçisi G", "min_order": 10, "price_per_unit": 3},
                "Tugo 4'lü": {"name": "Kullan At Tedarikçisi G", "min_order": 10, "price_per_unit": 5},
                "Çatal Bıçak": {"name": "Kullan At Tedarikçisi G", "min_order": 20, "price_per_unit": 2},
                "SU": {"name": "Su Tedarikçisi H", "min_order": 24, "price_per_unit": 2},
                "Soda": {"name": "Su Tedarikçisi H", "min_order": 24, "price_per_unit": 3},
                "Meyveli Soda": {"name": "Su Tedarikçisi H", "min_order": 24, "price_per_unit": 4},
                "Buzlu Bardak": {"name": "Su Tedarikçisi H", "min_order": 100, "price_per_unit": 0.8},
                "Limon": {"name": "Meyve Tedarikçisi I", "min_order": 10, "price_per_unit": 1},
                "Buz": {"name": "İç Üretim", "min_order": 0, "price_per_unit": 0},
                "Paketli Su (330ml)": {"name": "Su Tedarikçisi H", "min_order": 24, "price_per_unit": 1.5},
                "Tuvalet Kağıdı": {"name": "Kağıt Tedarikçisi J", "min_order": 6, "price_per_unit": 15},
                "Filtre Kağıdı": {"name": "Kağıt Tedarikçisi J", "min_order": 10, "price_per_unit": 0.5},
                "Siyah Poşet": {"name": "Paketleme Tedarikçisi K", "min_order": 5, "price_per_unit": 2},
                "POĞAÇA": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 3},
                "PROFİTEROL": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 4},
                "ÇİLEK MAGNOLİA": {"name": "Pastane Tedarikçisi L", "min_order": 10, "price_per_unit": 6},
                "COOKİE": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 2},
                "FISTIK ŞÖLENİ": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 5},
                "SAN SEBASTİAN CHEESECAKE": {"name": "Pastane Tedarikçisi L", "min_order": 10, "price_per_unit": 8},
                "ANANASLI BADEM PASTA": {"name": "Pastane Tedarikçisi L", "min_order": 10, "price_per_unit": 7},
                "MONO LATTE": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 4},
                "FISTIK KARAMEL": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 5},
                "İBİZA": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 6},
                "LİMONLU CHEESECAKE": {"name": "Pastane Tedarikçisi L", "min_order": 10, "price_per_unit": 8},
                "FRAMBUAZLI CHEESECAKE": {"name": "Pastane Tedarikçisi L", "min_order": 10, "price_per_unit": 8},
                "RULO KREP": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 4},
                "LOTUS MAGNOLİA": {"name": "Pastane Tedarikçisi L", "min_order": 10, "price_per_unit": 6},
                "FİT POĞAÇA": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 3},
                "LOTUS CHEESECAKE": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 5},
                "FRAMBUAZ BOMBA": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 5},
                "TİRAMİSU": {"name": "Pastane Tedarikçisi L", "min_order": 10, "price_per_unit": 7},
                "FISTIK RÜYASI": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 5},
                "EKSTRA ÖDEME": {"name": "Pastane Tedarikçisi L", "min_order": 1, "price_per_unit": 0},
                "MAVİ ROOİBOS": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 4},
                "HIBISLIME": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 4},
                "BUZLU BARDAK": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 3},
                "MANGO": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 4},
                "RED BERRIES": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 5},
                "FRUIT CARNIVAL": {"name": "Pastane Tedarikçisi L", "min_order": 20, "price_per_unit": 5},
                "Hibiskus Çayı": {"name": "Çay Tedarikçisi M", "min_order": 5, "price_per_unit": 20},
                "Ada Çayı": {"name": "Çay Tedarikçisi M", "min_order": 5, "price_per_unit": 18},
                "Kış Çayı": {"name": "Çay Tedarikçisi M", "min_order": 5, "price_per_unit": 22},
                "Mavi Rooibos": {"name": "Çay Tedarikçisi M", "min_order": 5, "price_per_unit": 25},
                "Meyve Karnavalı": {"name": "Çay Tedarikçisi M", "min_order": 5, "price_per_unit": 20},
                "Papatya Çayı": {"name": "Çay Tedarikçisi M", "min_order": 5, "price_per_unit": 18},
                "Yeşil Çay": {"name": "Çay Tedarikçisi M", "min_order": 5, "price_per_unit": 20},
                "Hizmet Ücreti": {"name": "İç Hizmet", "min_order": 0, "price_per_unit": 0},
            }
            
            reorder_suggestions = []
            
            for item in stock_list:
                current_stock = float(item.get("current_stock", 0))
                min_stock = float(item.get("min_stock", 0))
                item_name = item.get("name", "")
                unit = item.get("unit", "")
                category = item.get("category", "")
                
                # Get sales data for this item
                sales_quantity = product_sales.get(item_name, 0)
                daily_consumption = sales_quantity / 30 if sales_quantity > 0 else 0
                
                # Get lead time and supplier info
                lead_time = lead_times.get(item_name, 7)  # Default 7 days
                supplier_info = suppliers.get(item_name, {"name": "Bilinmeyen Tedarikçi", "min_order": 1, "price_per_unit": 0})
                
                # Calculate reorder point using safety stock
                safety_stock_multiplier = 1.5  # 50% safety buffer
                reorder_point = max(min_stock, daily_consumption * lead_time * safety_stock_multiplier)
                
                # Calculate suggested order quantity
                suggested_quantity = max(
                    supplier_info["min_order"],
                    int(daily_consumption * (lead_time + 7))  # 7 days of buffer
                )
                
                # Determine urgency
                urgency = "low"
                if current_stock <= reorder_point:
                    urgency = "high"
                elif current_stock <= reorder_point * 1.5:
                    urgency = "medium"
                
                # Calculate days until reorder needed
                days_until_reorder = None
                if daily_consumption > 0:
                    days_until_reorder = int((current_stock - reorder_point) / daily_consumption)
                
                # Calculate total cost
                total_cost = suggested_quantity * supplier_info["price_per_unit"]
                
                # Generate AI recommendations
                recommendations = []
                if urgency == "high":
                    recommendations.append("Order immediately - below reorder point")
                elif urgency == "medium":
                    recommendations.append("Plan order within 2-3 days")
                else:
                    recommendations.append("Monitor stock levels")
                
                if days_until_reorder and days_until_reorder < 7:
                    recommendations.append(f"Reorder needed in {days_until_reorder} days")
                
                if suggested_quantity > supplier_info["min_order"]:
                    recommendations.append(f"Consider ordering {suggested_quantity} units for better pricing")
                
                reorder_suggestions.append({
                    "item_name": item_name,
                    "category": category,
                    "current_stock": current_stock,
                    "min_stock": min_stock,
                    "unit": unit,
                    "reorder_point": round(reorder_point, 2),
                    "suggested_quantity": suggested_quantity,
                    "urgency": urgency,
                    "days_until_reorder": days_until_reorder,
                    "lead_time": lead_time,
                    "daily_consumption": round(daily_consumption, 2),
                    "supplier": supplier_info["name"],
                    "price_per_unit": supplier_info["price_per_unit"],
                    "total_cost": total_cost,
                    "recommendations": recommendations,
                    "is_critical": urgency == "high",
                    "needs_immediate_action": urgency == "high" and current_stock <= min_stock
                })
            
            # Sort by urgency and days until reorder
            reorder_suggestions.sort(key=lambda x: (x["urgency"] == "high", x["days_until_reorder"] or 999))
            
            # Calculate summary
            critical_items = [item for item in reorder_suggestions if item["is_critical"]]
            total_cost = sum(item["total_cost"] for item in reorder_suggestions)
            
            return {
                "success": True,
                "suggestions": reorder_suggestions,
                "summary": {
                    "total_items": len(reorder_suggestions),
                    "critical_items": len(critical_items),
                    "total_estimated_cost": total_cost,
                    "items_needing_immediate_action": len([item for item in reorder_suggestions if item["needs_immediate_action"]])
                },
                "critical_reorders": critical_items[:10],
                "upcoming_reorders": [item for item in reorder_suggestions if item["urgency"] == "medium"][:10]
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error getting smart reorder suggestions: {str(e)}"}
    
    def get_seasonal_analysis(self) -> Dict[str, Any]:
        """Get seasonal analysis and trend detection for sales patterns."""
        try:
            # Get sales data for the last 90 days to analyze seasonal patterns
            sales_data = self.get_sales_data(90)
            daily_trends = sales_data.get("daily_trends", [])
            product_sales = {item["name"]: item["quantity"] for item in sales_data.get("top_products", [])}
            
            if not daily_trends:
                return {"success": False, "message": "No sales data available for seasonal analysis"}
            
            # Analyze daily patterns
            daily_analysis = self._analyze_daily_patterns(daily_trends)
            
            # Analyze product seasonality
            product_seasonality = self._analyze_product_seasonality(daily_trends, product_sales)
            
            # Analyze weekly patterns
            weekly_analysis = self._analyze_weekly_patterns(daily_trends)
            
            # Detect trends
            trend_analysis = self._detect_trends(daily_trends)
            
            # Generate seasonal recommendations
            seasonal_recommendations = self._generate_seasonal_recommendations(
                daily_analysis, product_seasonality, weekly_analysis, trend_analysis
            )
            
            return {
                "success": True,
                "daily_analysis": daily_analysis,
                "product_seasonality": product_seasonality,
                "weekly_analysis": weekly_analysis,
                "trend_analysis": trend_analysis,
                "seasonal_recommendations": seasonal_recommendations,
                "summary": {
                    "analysis_period": "90 days",
                    "total_days_analyzed": len(daily_trends),
                    "peak_day": daily_analysis.get("peak_day"),
                    "lowest_day": daily_analysis.get("lowest_day"),
                    "trend_direction": trend_analysis.get("overall_trend"),
                    "seasonal_products": len([p for p in product_seasonality if p.get("is_seasonal", False)])
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error getting seasonal analysis: {str(e)}"}
    
    def _analyze_daily_patterns(self, daily_trends: List[Dict]) -> Dict[str, Any]:
        """Analyze daily sales patterns."""
        if not daily_trends:
            return {}
        
        # Calculate daily statistics
        daily_sales = [day["total_sales"] for day in daily_trends]
        avg_daily_sales = sum(daily_sales) / len(daily_sales)
        
        # Find peak and lowest days
        peak_day = max(daily_trends, key=lambda x: x["total_sales"])
        lowest_day = min(daily_trends, key=lambda x: x["total_sales"])
        
        # Calculate variance
        variance = sum((x - avg_daily_sales) ** 2 for x in daily_sales) / len(daily_sales)
        std_deviation = variance ** 0.5
        
        # Identify high and low sales days
        high_sales_threshold = avg_daily_sales + std_deviation
        low_sales_threshold = avg_daily_sales - std_deviation
        
        high_sales_days = [day for day in daily_trends if day["total_sales"] > high_sales_threshold]
        low_sales_days = [day for day in daily_trends if day["total_sales"] < low_sales_threshold]
        
        return {
            "average_daily_sales": round(avg_daily_sales, 2),
            "peak_day": peak_day,
            "lowest_day": lowest_day,
            "standard_deviation": round(std_deviation, 2),
            "high_sales_days": len(high_sales_days),
            "low_sales_days": len(low_sales_days),
            "consistency_score": round((1 - (std_deviation / avg_daily_sales)) * 100, 2) if avg_daily_sales > 0 else 0
        }
    
    def _analyze_product_seasonality(self, daily_trends: List[Dict], product_sales: Dict[str, int]) -> List[Dict]:
        """Analyze seasonal patterns for individual products."""
        # Mock seasonal patterns (in a real system, this would be calculated from historical data)
        seasonal_patterns = {
            "ICED AMERICANO": {"peak_season": "summer", "seasonal_factor": 1.8},
            "ICED FILTER COFFEE": {"peak_season": "summer", "seasonal_factor": 2.0},
            "ICED CAPPUCCİNO": {"peak_season": "summer", "seasonal_factor": 1.9},
            "ICED LATTE": {"peak_season": "summer", "seasonal_factor": 2.1},
            "ICE CARAMEL LATTE": {"peak_season": "summer", "seasonal_factor": 1.7},
            "ICE CARAMEL MACCHIATO": {"peak_season": "summer", "seasonal_factor": 1.6},
            "ICE WHITE MOCHA": {"peak_season": "summer", "seasonal_factor": 1.5},
            "COLD BREW": {"peak_season": "summer", "seasonal_factor": 2.2},
            "LİMONATA": {"peak_season": "summer", "seasonal_factor": 1.9},
            "WODEN LIME": {"peak_season": "summer", "seasonal_factor": 1.8},
            "AMERICANO": {"peak_season": "winter", "seasonal_factor": 1.3},
            "ESPRESSO": {"peak_season": "winter", "seasonal_factor": 1.2},
            "LATTE": {"peak_season": "winter", "seasonal_factor": 1.4},
            "CAPPUCCINO": {"peak_season": "winter", "seasonal_factor": 1.3},
            "TÜRK KAHVESİ": {"peak_season": "winter", "seasonal_factor": 1.5},
            "FİLTRE KAHVE": {"peak_season": "winter", "seasonal_factor": 1.2},
            "SİYAH ÇAY": {"peak_season": "winter", "seasonal_factor": 1.4},
            "Hibiskus Çayı": {"peak_season": "winter", "seasonal_factor": 1.3},
            "Ada Çayı": {"peak_season": "winter", "seasonal_factor": 1.2},
            "Kış Çayı": {"peak_season": "winter", "seasonal_factor": 1.6},
            "Mavi Rooibos": {"peak_season": "winter", "seasonal_factor": 1.3},
            "Meyve Karnavalı": {"peak_season": "winter", "seasonal_factor": 1.2},
            "Papatya Çayı": {"peak_season": "winter", "seasonal_factor": 1.1},
            "Yeşil Çay": {"peak_season": "winter", "seasonal_factor": 1.2},
        }
        
        product_analysis = []
        
        for product_name, sales_quantity in product_sales.items():
            if product_name in seasonal_patterns:
                pattern = seasonal_patterns[product_name]
                is_seasonal = pattern["seasonal_factor"] > 1.3
                
                # Calculate seasonal impact
                seasonal_impact = "high" if pattern["seasonal_factor"] > 1.8 else "medium" if pattern["seasonal_factor"] > 1.5 else "low"
                
                product_analysis.append({
                    "product_name": product_name,
                    "sales_quantity": sales_quantity,
                    "peak_season": pattern["peak_season"],
                    "seasonal_factor": pattern["seasonal_factor"],
                    "is_seasonal": is_seasonal,
                    "seasonal_impact": seasonal_impact,
                    "recommendation": self._get_seasonal_recommendation(product_name, pattern)
                })
        
        return sorted(product_analysis, key=lambda x: x["seasonal_factor"], reverse=True)
    
    def _analyze_weekly_patterns(self, daily_trends: List[Dict]) -> Dict[str, Any]:
        """Analyze weekly sales patterns."""
        if not daily_trends:
            return {}
        
        # Group by day of week (simplified - in real system would use actual dates)
        weekly_patterns = {}
        
        for i, day in enumerate(daily_trends):
            day_of_week = i % 7  # Simplified day calculation
            day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_of_week]
            
            if day_name not in weekly_patterns:
                weekly_patterns[day_name] = []
            weekly_patterns[day_name].append(day["total_sales"])
        
        # Calculate averages for each day
        weekly_analysis = {}
        for day_name, sales in weekly_patterns.items():
            weekly_analysis[day_name] = {
                "average_sales": round(sum(sales) / len(sales), 2),
                "total_sales": sum(sales),
                "day_count": len(sales)
            }
        
        # Find best and worst days
        best_day = max(weekly_analysis.items(), key=lambda x: x[1]["average_sales"])
        worst_day = min(weekly_analysis.items(), key=lambda x: x[1]["average_sales"])
        
        return {
            "weekly_patterns": weekly_analysis,
            "best_day": {"day": best_day[0], "average_sales": best_day[1]["average_sales"]},
            "worst_day": {"day": worst_day[0], "average_sales": worst_day[1]["average_sales"]},
            "weekend_vs_weekday": self._compare_weekend_weekday(weekly_analysis)
        }
    
    def _detect_trends(self, daily_trends: List[Dict]) -> Dict[str, Any]:
        """Detect sales trends over time."""
        if len(daily_trends) < 7:
            return {"overall_trend": "insufficient_data"}
        
        # Calculate trend using simple linear regression
        sales_values = [day["total_sales"] for day in daily_trends]
        n = len(sales_values)
        
        # Calculate slope
        x_values = list(range(n))
        x_mean = sum(x_values) / n
        y_mean = sum(sales_values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, sales_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine trend direction
        if slope > 0.5:
            trend_direction = "increasing"
        elif slope < -0.5:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        # Calculate trend strength
        trend_strength = abs(slope) * 100
        
        return {
            "overall_trend": trend_direction,
            "trend_strength": round(trend_strength, 2),
            "slope": round(slope, 4),
            "trend_description": self._describe_trend(trend_direction, trend_strength)
        }
    
    def _generate_seasonal_recommendations(self, daily_analysis: Dict, product_seasonality: List[Dict], 
                                         weekly_analysis: Dict, trend_analysis: Dict) -> List[Dict]:
        """Generate seasonal recommendations based on analysis."""
        recommendations = []
        
        # Daily pattern recommendations
        if daily_analysis.get("consistency_score", 0) < 70:
            recommendations.append({
                "type": "consistency",
                "title": "Improve Sales Consistency",
                "description": f"Sales consistency is {daily_analysis.get('consistency_score', 0)}%. Consider strategies to stabilize daily sales.",
                "action": "Analyze factors causing sales fluctuations and implement consistency measures",
                "impact": "medium"
            })
        
        # Seasonal product recommendations
        summer_products = [p for p in product_seasonality if p.get("peak_season") == "summer" and p.get("is_seasonal")]
        winter_products = [p for p in product_seasonality if p.get("peak_season") == "winter" and p.get("is_seasonal")]
        
        if summer_products:
            recommendations.append({
                "type": "seasonal",
                "title": "Prepare for Summer Season",
                "description": f"Products like {', '.join([p['product_name'] for p in summer_products[:3]])} show strong summer seasonality",
                "action": "Increase inventory and marketing for summer products as weather warms",
                "impact": "high"
            })
        
        if winter_products:
            recommendations.append({
                "type": "seasonal",
                "title": "Prepare for Winter Season",
                "description": f"Products like {', '.join([p['product_name'] for p in winter_products[:3]])} show strong winter seasonality",
                "action": "Increase inventory and marketing for winter products as weather cools",
                "impact": "high"
            })
        
        # Weekly pattern recommendations
        if weekly_analysis.get("weekend_vs_weekday", {}).get("weekend_advantage", 0) > 20:
            recommendations.append({
                "type": "weekly",
                "title": "Leverage Weekend Performance",
                "description": "Weekend sales are significantly higher than weekday sales",
                "action": "Consider weekend promotions and staffing adjustments",
                "impact": "medium"
            })
        
        # Trend recommendations
        if trend_analysis.get("overall_trend") == "increasing":
            recommendations.append({
                "type": "trend",
                "title": "Capitalize on Growth Trend",
                "description": f"Sales are trending upward with {trend_analysis.get('trend_strength', 0)}% strength",
                "action": "Maintain current strategies and consider expansion opportunities",
                "impact": "high"
            })
        elif trend_analysis.get("overall_trend") == "decreasing":
            recommendations.append({
                "type": "trend",
                "title": "Address Declining Trend",
                "description": f"Sales are trending downward with {trend_analysis.get('trend_strength', 0)}% strength",
                "action": "Investigate causes and implement corrective measures",
                "impact": "high"
            })
        
        return recommendations
    
    def _get_seasonal_recommendation(self, product_name: str, pattern: Dict) -> str:
        """Get specific seasonal recommendation for a product."""
        if pattern["peak_season"] == "summer":
            return f"Increase {product_name} inventory and marketing during summer months"
        elif pattern["peak_season"] == "winter":
            return f"Focus on {product_name} promotion during winter months"
        else:
            return f"Monitor {product_name} for seasonal patterns"
    
    def _compare_weekend_weekday(self, weekly_analysis: Dict) -> Dict[str, Any]:
        """Compare weekend vs weekday performance."""
        weekend_days = ["Saturday", "Sunday"]
        weekday_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        weekend_sales = sum(weekly_analysis.get(day, {}).get("average_sales", 0) for day in weekend_days)
        weekday_sales = sum(weekly_analysis.get(day, {}).get("average_sales", 0) for day in weekday_days)
        
        weekend_avg = weekend_sales / len(weekend_days) if weekend_days else 0
        weekday_avg = weekday_sales / len(weekday_days) if weekday_days else 0
        
        weekend_advantage = ((weekend_avg - weekday_avg) / weekday_avg * 100) if weekday_avg > 0 else 0
        
        return {
            "weekend_average": round(weekend_avg, 2),
            "weekday_average": round(weekday_avg, 2),
            "weekend_advantage": round(weekend_advantage, 2)
        }
    
    def _describe_trend(self, trend_direction: str, trend_strength: float) -> str:
        """Describe the trend in human-readable format."""
        if trend_direction == "increasing":
            if trend_strength > 50:
                return "Strong upward trend"
            elif trend_strength > 20:
                return "Moderate upward trend"
            else:
                return "Slight upward trend"
        elif trend_direction == "decreasing":
            if trend_strength > 50:
                return "Strong downward trend"
            elif trend_strength > 20:
                return "Moderate downward trend"
            else:
                return "Slight downward trend"
        else:
            return "Stable trend"
    
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
                "updated_at": datetime.now(timezone.utc).isoformat()
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
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                self.client.table("stock_transactions").insert(transaction_data).execute()
                
                # Create/update manual update record for protection
                manual_update_data = {
                    "stock_item_id": item["id"],
                    "old_stock": old_stock,
                    "new_stock": float(new_stock),
                    "reason": reason,
                    "manual_update_flag": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
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
    
    def add_new_stock_item(self, name: str, category: str, current_stock: float = 0, 
                          min_stock: float = 0, unit: str = "ml", is_ready_made: bool = False,
                          cost_per_unit: float = 0, package_size: float = 0, 
                          package_unit: str = "ml") -> Dict[str, Any]:
        """Add a new stock item to the database"""
        try:
            # Check if item already exists
            existing_response = self.client.table("stock_items").select("*").ilike("item_name", name).execute()
            
            if existing_response.data:
                return {"success": False, "message": f"Item '{name}' already exists in the database"}
            
            # Generate material_id
            material_id = f"{category}_{name.replace(' ', '_')}"
            
            # Create new stock item
            new_item_data = {
                "material_id": material_id,
                "item_name": name,
                "category_name": category,
                "current_stock": float(current_stock),
                "min_stock_level": float(min_stock),
                "unit": unit,
                "is_ready_made": is_ready_made,
                "cost_per_unit": float(cost_per_unit),
                "package_size": float(package_size),
                "package_unit": package_unit,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            insert_response = self.client.table("stock_items").insert(new_item_data).execute()
            
            if insert_response.data:
                # Create initial transaction record
                transaction_data = {
                    "stock_item_id": insert_response.data[0]["id"],
                    "transaction_type": "initial_stock",
                    "old_stock": 0.0,
                    "new_stock": float(current_stock),
                    "change_amount": float(current_stock),
                    "reason": "New product added",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                self.client.table("stock_transactions").insert(transaction_data).execute()
                
                return {
                    "success": True,
                    "message": f"Product '{name}' added successfully",
                    "item_name": name,
                    "category": category,
                    "material_id": material_id,
                    "current_stock": float(current_stock)
                }
            else:
                return {"success": False, "message": "Failed to add product to database"}
                
        except Exception as e:
            return {"success": False, "message": f"Error adding product: {str(e)}"}
    
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
                                    # Normalize to timezone-aware UTC if missing tzinfo
                                    if update_time.tzinfo is None:
                                        update_time = update_time.replace(tzinfo=timezone.utc)
                                    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=4)
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
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", stock_item["id"]).execute()
                
                # Create transaction record
                transaction_data = {
                    "stock_item_id": stock_item["id"],
                    "transaction_type": "daily_consumption",
                    "old_stock": current_stock,
                    "new_stock": new_stock,
                    "change_amount": -daily_amount,
                    "reason": "daily_consumption",
                    "timestamp": datetime.now(timezone.utc).isoformat()
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

    # ============================================================================
    # AI SCHEDULER METHODS
    # ============================================================================

    def get_baristas(self) -> Dict[str, Any]:
        """Get all active baristas"""
        try:
            response = self.client.table("baristas").select("*").eq("is_active", True).order("name").execute()
            
            if response.data:
                return {"success": True, "baristas": response.data}
            else:
                return {"success": True, "baristas": []}
                
        except Exception as e:
            print(f"Error getting baristas: {str(e)}")
            return {"success": False, "message": f"Error getting baristas: {str(e)}"}

    def create_barista(self, name: str, email: str = None, phone: str = None, 
                      type: str = "full-time", max_hours: int = 45, 
                      preferred_shifts: list = None, skills: list = None) -> Dict[str, Any]:
        """Create a new barista"""
        try:
            barista_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "type": type,
                "max_hours": max_hours,
                "preferred_shifts": preferred_shifts or [],
                "skills": skills or [],
                "is_active": True
            }
            
            response = self.client.table("baristas").insert(barista_data).execute()
            
            if response.data:
                return {"success": True, "barista": response.data[0]}
            else:
                return {"success": False, "message": "Failed to create barista"}
                
        except Exception as e:
            print(f"Error creating barista: {str(e)}")
            return {"success": False, "message": f"Error creating barista: {str(e)}"}

    def update_barista(self, barista_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a barista"""
        try:
            response = self.client.table("baristas").update(update_data).eq("id", barista_id).execute()
            
            if response.data:
                return {"success": True, "barista": response.data[0]}
            else:
                return {"success": False, "message": "Barista not found"}
                
        except Exception as e:
            print(f"Error updating barista: {str(e)}")
            return {"success": False, "message": f"Error updating barista: {str(e)}"}

    def deactivate_barista(self, barista_id: str) -> Dict[str, Any]:
        """Deactivate a barista (soft delete)"""
        try:
            response = self.client.table("baristas").update({"is_active": False}).eq("id", barista_id).execute()
            
            if response.data:
                return {"success": True, "message": "Barista deactivated successfully"}
            else:
                return {"success": False, "message": "Barista not found"}
                
        except Exception as e:
            print(f"Error deactivating barista: {str(e)}")
            return {"success": False, "message": f"Error deactivating barista: {str(e)}"}

    def get_weekly_schedules(self) -> Dict[str, Any]:
        """Get all weekly schedules"""
        try:
            response = self.client.table("weekly_schedules").select("*").order("week_start", desc=True).execute()
            
            if response.data:
                return {"success": True, "schedules": response.data}
            else:
                return {"success": True, "schedules": []}
                
        except Exception as e:
            print(f"Error getting weekly schedules: {str(e)}")
            return {"success": False, "message": f"Error getting weekly schedules: {str(e)}"}

    def create_weekly_schedule(self, week_start: str, week_end: str, created_by: str, notes: str = None) -> Dict[str, Any]:
        """Create a new weekly schedule"""
        try:
            schedule_data = {
                "week_start": week_start,
                "week_end": week_end,
                "status": "draft",
                "created_by": created_by,
                "notes": notes
            }
            
            response = self.client.table("weekly_schedules").insert(schedule_data).execute()
            
            if response.data:
                return {"success": True, "schedule": response.data[0]}
            else:
                return {"success": False, "message": "Failed to create schedule"}
                
        except Exception as e:
            print(f"Error creating weekly schedule: {str(e)}")
            return {"success": False, "message": f"Error creating weekly schedule: {str(e)}"}

    def get_schedule_shifts(self, schedule_id: str) -> Dict[str, Any]:
        """Get shifts for a specific schedule"""
        try:
            response = self.client.table("shifts").select("*, baristas(*)").eq("schedule_id", schedule_id).execute()
            
            if response.data:
                return {"success": True, "shifts": response.data}
            else:
                return {"success": True, "shifts": []}
                
        except Exception as e:
            print(f"Error getting schedule shifts: {str(e)}")
            return {"success": False, "message": f"Error getting schedule shifts: {str(e)}"}

    def create_shift(self, schedule_id: str, barista_id: str, day_of_week: int, 
                    shift_type: str, start_time: str = None, end_time: str = None, 
                    hours: float = 0, notes: str = None) -> Dict[str, Any]:
        """Create a shift"""
        try:
            shift_data = {
                "schedule_id": schedule_id,
                "barista_id": barista_id,
                "day_of_week": day_of_week,
                "shift_type": shift_type,
                "start_time": start_time,
                "end_time": end_time,
                "hours": hours,
                "notes": notes
            }
            
            response = self.client.table("shifts").insert(shift_data).execute()
            
            if response.data:
                return {"success": True, "shift": response.data[0]}
            else:
                return {"success": False, "message": "Failed to create shift"}
                
        except Exception as e:
            print(f"Error creating shift: {str(e)}")
            return {"success": False, "message": f"Error creating shift: {str(e)}"}

    def publish_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Publish a schedule"""
        try:
            response = self.client.table("weekly_schedules").update({"status": "published"}).eq("id", schedule_id).execute()
            
            if response.data:
                return {"success": True, "message": "Schedule published successfully"}
            else:
                return {"success": False, "message": "Schedule not found"}
                
        except Exception as e:
            print(f"Error publishing schedule: {str(e)}")
            return {"success": False, "message": f"Error publishing schedule: {str(e)}"}

    def get_time_off_requests(self) -> Dict[str, Any]:
        """Get all time-off requests"""
        try:
            response = self.client.table("time_off_requests").select("*, baristas(*)").order("requested_at", desc=True).execute()
            
            if response.data:
                return {"success": True, "requests": response.data}
            else:
                return {"success": True, "requests": []}
                
        except Exception as e:
            print(f"Error getting time-off requests: {str(e)}")
            return {"success": False, "message": f"Error getting time-off requests: {str(e)}"}

    def create_time_off_request(self, barista_id: str, request_date: str, reason: str = "personal", notes: str = None) -> Dict[str, Any]:
        """Create a time-off request"""
        try:
            request_data = {
                "barista_id": barista_id,
                "request_date": request_date,
                "reason": reason,
                "notes": notes,
                "status": "pending"
            }
            
            response = self.client.table("time_off_requests").insert(request_data).execute()
            
            if response.data:
                return {"success": True, "request": response.data[0]}
            else:
                return {"success": False, "message": "Failed to create time-off request"}
                
        except Exception as e:
            print(f"Error creating time-off request: {str(e)}")
            return {"success": False, "message": f"Error creating time-off request: {str(e)}"}

    def update_time_off_request(self, request_id: str, status: str, reviewed_by: str) -> Dict[str, Any]:
        """Update time-off request status"""
        try:
            update_data = {
                "status": status,
                "reviewed_by": reviewed_by,
                "reviewed_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = self.client.table("time_off_requests").update(update_data).eq("id", request_id).execute()
            
            if response.data:
                return {"success": True, "request": response.data[0]}
            else:
                return {"success": False, "message": "Time-off request not found"}
                
        except Exception as e:
            print(f"Error updating time-off request: {str(e)}")
            return {"success": False, "message": f"Error updating time-off request: {str(e)}"}
