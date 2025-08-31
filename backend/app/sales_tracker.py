import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class SalesTracker:
    def __init__(self):
        self.sales_file = "sales_history.json"
        self.sales_data = self.load_sales_data()
    
    def load_sales_data(self) -> Dict:
        """Load sales history from JSON file"""
        try:
            if os.path.exists(self.sales_file):
                with open(self.sales_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Initialize with empty structure
                return {
                    "sales_records": [],
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error loading sales data: {e}")
            return {
                "sales_records": [],
                "last_updated": datetime.now().isoformat()
            }
    
    def save_sales_data(self) -> bool:
        """Save sales data to JSON file"""
        try:
            self.sales_data["last_updated"] = datetime.now().isoformat()
            with open(self.sales_file, 'w', encoding='utf-8') as f:
                json.dump(self.sales_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving sales data: {e}")
            return False
    
    def add_sales_record(self, product_name: str, quantity: int, date: str = None) -> bool:
        """Add a new sales record"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        record = {
            "id": f"sales_{len(self.sales_data['sales_records']) + 1}",
            "product_name": product_name,
            "quantity": quantity,
            "date": date,
            "timestamp": datetime.now().isoformat()
        }
        
        self.sales_data["sales_records"].append(record)
        return self.save_sales_data()
    
    def add_bulk_sales(self, sales_records: List[Dict]) -> bool:
        """Add multiple sales records from Excel processing"""
        for record in sales_records:
            if "product_name" in record and "quantity" in record:
                self.add_sales_record(
                    record["product_name"], 
                    record["quantity"], 
                    record.get("date", datetime.now().strftime("%Y-%m-%d"))
                )
        return True
    
    def get_sales_analytics(self, period: str = "7d") -> Dict:
        """Get comprehensive sales analytics for the specified period"""
        try:
            # Calculate date range
            end_date = datetime.now()
            if period == "7d":
                start_date = end_date - timedelta(days=7)
            elif period == "30d":
                start_date = end_date - timedelta(days=30)
            elif period == "90d":
                start_date = end_date - timedelta(days=90)
            else:  # all time
                start_date = datetime.min
            
            # Filter sales records by date
            filtered_sales = []
            for record in self.sales_data["sales_records"]:
                try:
                    record_date = datetime.fromisoformat(record["date"])
                    if start_date <= record_date <= end_date:
                        filtered_sales.append(record)
                except:
                    # If date parsing fails, include the record
                    filtered_sales.append(record)
            
            if not filtered_sales:
                return self._get_empty_analytics()
            
            # Calculate total sales
            total_sales = sum(record["quantity"] for record in filtered_sales)
            
            # Calculate top products
            product_sales = Counter()
            for record in filtered_sales:
                product_sales[record["product_name"]] += record["quantity"]
            
            top_products = []
            for product, quantity in product_sales.most_common(10):
                percentage = (quantity / total_sales) * 100 if total_sales > 0 else 0
                top_products.append({
                    "name": product,
                    "quantity": quantity,
                    "percentage": round(percentage, 1)
                })
            
            # Calculate daily trends
            daily_sales = defaultdict(lambda: {"totalSales": 0, "products": 0, "unique_products": set()})
            for record in filtered_sales:
                date = record["date"]
                daily_sales[date]["totalSales"] += record["quantity"]
                daily_sales[date]["products"] += record["quantity"]
                daily_sales[date]["unique_products"].add(record["product_name"])
            
            # Convert daily sales to list format
            daily_trends = []
            for date, data in sorted(daily_sales.items(), reverse=True):
                daily_trends.append({
                    "date": date,
                    "totalSales": data["totalSales"],
                    "products": data["products"]
                })
            
            # Calculate category breakdown (mock for now - can be enhanced with recipe data)
            category_breakdown = [
                {"category": "coffee", "count": total_sales, "percentage": 100.0}
            ]
            
            return {
                "totalSales": total_sales,
                "topProducts": top_products,
                "dailyTrends": daily_trends,
                "categoryBreakdown": category_breakdown
            }
            
        except Exception as e:
            print(f"Error calculating sales analytics: {e}")
            return self._get_empty_analytics()
    
    def _get_empty_analytics(self) -> Dict:
        """Return empty analytics structure when no data is available"""
        return {
            "totalSales": 0,
            "topProducts": [],
            "dailyTrends": [],
            "categoryBreakdown": []
        }
    
    def get_total_sales_count(self) -> int:
        """Get total number of sales records"""
        return len(self.sales_data["sales_records"])
    
    def clear_sales_data(self) -> bool:
        """Clear all sales data (for testing/reset purposes)"""
        self.sales_data["sales_records"] = []
        return self.save_sales_data()
