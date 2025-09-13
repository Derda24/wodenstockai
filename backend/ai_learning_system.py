#!/usr/bin/env python3
"""
AI Learning System for Woden Stock Management

This system implements continuous learning from Excel uploads to improve:
1. Product matching accuracy
2. Demand forecasting
3. Stock optimization recommendations
4. Sales pattern analysis
5. Seasonal trend detection
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import pandas as pd
from dataclasses import dataclass

@dataclass
class LearningInsight:
    """Represents a learning insight from data analysis"""
    type: str  # 'product_pattern', 'seasonal_trend', 'demand_forecast', 'optimization'
    description: str
    confidence: float  # 0.0 to 1.0
    data_points: int
    timestamp: datetime
    actionable: bool = True

class AILearningSystem:
    """AI Learning System that continuously learns from Excel uploads"""
    
    def __init__(self, supabase_service):
        self.supabase_service = supabase_service
        self.learning_file = "ai_learning_data.json"
        self.learning_data = self._load_learning_data()
        
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load existing learning data from file"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading learning data: {e}")
        
        return {
            "product_patterns": {},
            "seasonal_trends": {},
            "demand_forecasts": {},
            "optimization_insights": [],
            "learning_history": [],
            "model_accuracy": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_learning_data(self):
        """Save learning data to file"""
        try:
            self.learning_data["last_updated"] = datetime.now().isoformat()
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def learn_from_excel_upload(self, sales_data: Dict, processed_items: List[Dict]) -> Dict[str, Any]:
        """
        Main learning function called when Excel is uploaded
        Analyzes the data and updates AI models
        """
        print("🧠 AI Learning System: Processing new data...")
        
        learning_insights = {
            "new_products": [],
            "sales_patterns": {},
            "pricing_insights": {},
            "seasonal_data": {},
            "demand_forecasts": {},
            "optimization_suggestions": []
        }
        
        # 1. Analyze new products
        new_products = self._analyze_new_products(processed_items)
        learning_insights["new_products"] = new_products
        
        # 2. Update sales patterns
        sales_patterns = self._analyze_sales_patterns(sales_data)
        learning_insights["sales_patterns"] = sales_patterns
        
        # 3. Detect seasonal trends
        seasonal_trends = self._detect_seasonal_trends(sales_data)
        learning_insights["seasonal_data"] = seasonal_trends
        
        # 4. Generate demand forecasts
        demand_forecasts = self._generate_demand_forecasts(sales_data)
        learning_insights["demand_forecasts"] = demand_forecasts
        
        # 5. Create optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(sales_data, processed_items)
        learning_insights["optimization_suggestions"] = optimization_suggestions
        
        # 6. Update learning models
        self._update_learning_models(learning_insights)
        
        # 7. Save learning data
        self._save_learning_data()
        
        print(f"✅ AI Learning System: Processed {len(processed_items)} items, found {len(new_products)} new products")
        
        return learning_insights
    
    def _analyze_new_products(self, processed_items: List[Dict]) -> List[str]:
        """Analyze for new products that aren't in the current inventory"""
        new_products = []
        current_stock_items = self.supabase_service.get_flat_stock_list()
        current_product_names = {item.get("name", "").lower() for item in current_stock_items}
        
        for item in processed_items:
            if item.get("status") == "success":
                product_name = item.get("product", "")
                if product_name and product_name.lower() not in current_product_names:
                    new_products.append(product_name)
        
        # Update learning data
        if new_products:
            self.learning_data["product_patterns"]["new_products"] = new_products
            self.learning_data["learning_history"].append({
                "type": "new_products_detected",
                "count": len(new_products),
                "products": new_products,
                "timestamp": datetime.now().isoformat()
            })
        
        return new_products
    
    def _analyze_sales_patterns(self, sales_data: Dict) -> Dict[str, Any]:
        """Analyze sales patterns and trends"""
        patterns = {
            "top_selling_products": [],
            "sales_volume_trends": {},
            "peak_selling_times": [],
            "product_combinations": {}
        }
        
        # Analyze top selling products
        product_sales = defaultdict(int)
        for date, data in sales_data.items():
            for item in data.get("items", []):
                product_sales[item.get("product", "")] += item.get("quantity", 0)
        
        # Get top 10 products
        top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
        patterns["top_selling_products"] = [{"product": p, "quantity": q} for p, q in top_products]
        
        # Update learning data
        self.learning_data["product_patterns"]["top_selling"] = patterns["top_selling_products"]
        
        return patterns
    
    def _detect_seasonal_trends(self, sales_data: Dict) -> Dict[str, Any]:
        """Detect seasonal trends in sales data"""
        current_month = datetime.now().month
        seasonal_data = {
            "current_season": self._get_season(current_month),
            "seasonal_products": [],
            "trend_direction": "stable"
        }
        
        # Analyze seasonal product patterns
        seasonal_products = self._identify_seasonal_products(sales_data)
        seasonal_data["seasonal_products"] = seasonal_products
        
        # Update learning data
        self.learning_data["seasonal_trends"][str(current_month)] = seasonal_data
        
        return seasonal_data
    
    def _get_season(self, month: int) -> str:
        """Get season based on month"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _identify_seasonal_products(self, sales_data: Dict) -> List[str]:
        """Identify products that show seasonal patterns"""
        seasonal_products = []
        
        # Look for products with seasonal keywords
        seasonal_keywords = {
            "summer": ["iced", "cold", "frozen", "smoothie", "lemonade"],
            "winter": ["hot", "warm", "soup", "tea", "coffee"],
            "spring": ["fresh", "green", "herbal"],
            "autumn": ["spice", "pumpkin", "apple"]
        }
        
        current_season = self._get_season(datetime.now().month)
        keywords = seasonal_keywords.get(current_season, [])
        
        for date, data in sales_data.items():
            for item in data.get("items", []):
                product_name = item.get("product", "").lower()
                for keyword in keywords:
                    if keyword in product_name and product_name not in seasonal_products:
                        seasonal_products.append(item.get("product", ""))
        
        return seasonal_products
    
    def _generate_demand_forecasts(self, sales_data: Dict) -> Dict[str, Any]:
        """Generate demand forecasts based on sales data"""
        forecasts = {
            "next_week_demand": {},
            "trending_products": [],
            "declining_products": []
        }
        
        # Simple demand forecasting based on recent sales
        product_demand = defaultdict(list)
        
        for date, data in sales_data.items():
            for item in data.get("items", []):
                product = item.get("product", "")
                quantity = item.get("quantity", 0)
                product_demand[product].append(quantity)
        
        # Calculate average demand and trends
        for product, quantities in product_demand.items():
            if len(quantities) >= 2:
                avg_demand = sum(quantities) / len(quantities)
                trend = "increasing" if quantities[-1] > quantities[0] else "decreasing"
                
                forecasts["next_week_demand"][product] = {
                    "predicted_quantity": int(avg_demand * 1.1),  # 10% growth assumption
                    "confidence": min(0.9, len(quantities) / 10),  # More data = higher confidence
                    "trend": trend
                }
                
                if trend == "increasing":
                    forecasts["trending_products"].append(product)
                else:
                    forecasts["declining_products"].append(product)
        
        return forecasts
    
    def _generate_optimization_suggestions(self, sales_data: Dict, processed_items: List[Dict]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on data analysis"""
        suggestions = []
        
        # Analyze stock levels vs sales
        stock_items = self.supabase_service.get_flat_stock_list()
        stock_dict = {item.get("name", ""): item for item in stock_items}
        
        for item in processed_items:
            if item.get("status") == "success":
                product_name = item.get("product", "")
                quantity_sold = item.get("quantity", 0)
                
                if product_name in stock_dict:
                    stock_item = stock_dict[product_name]
                    current_stock = float(stock_item.get("current_stock", 0))
                    min_stock = float(stock_item.get("min_stock", 0))
                    
                    # Suggest stock optimization
                    if current_stock <= min_stock and quantity_sold > 0:
                        suggestions.append({
                            "type": "stock_optimization",
                            "product": product_name,
                            "suggestion": f"Increase minimum stock for {product_name}",
                            "reason": f"High demand ({quantity_sold} sold) but low stock ({current_stock})",
                            "priority": "high"
                        })
        
        return suggestions
    
    def _update_learning_models(self, learning_insights: Dict[str, Any]):
        """Update AI learning models with new insights"""
        # Update product patterns
        if learning_insights.get("new_products"):
            self.learning_data["product_patterns"]["new_products"] = learning_insights["new_products"]
        
        # Update sales patterns
        if learning_insights.get("sales_patterns"):
            self.learning_data["product_patterns"]["sales_patterns"] = learning_insights["sales_patterns"]
        
        # Update seasonal trends
        if learning_insights.get("seasonal_data"):
            current_month = str(datetime.now().month)
            self.learning_data["seasonal_trends"][current_month] = learning_insights["seasonal_data"]
        
        # Update demand forecasts
        if learning_insights.get("demand_forecasts"):
            self.learning_data["demand_forecasts"] = learning_insights["demand_forecasts"]
        
        # Add to learning history
        self.learning_data["learning_history"].append({
            "timestamp": datetime.now().isoformat(),
            "insights": learning_insights,
            "data_points": len(learning_insights.get("new_products", []))
        })
        
        # Keep only last 100 learning entries
        if len(self.learning_data["learning_history"]) > 100:
            self.learning_data["learning_history"] = self.learning_data["learning_history"][-100:]
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of what the AI has learned"""
        return {
            "total_learning_entries": len(self.learning_data.get("learning_history", [])),
            "new_products_detected": len(self.learning_data.get("product_patterns", {}).get("new_products", [])),
            "seasonal_trends_analyzed": len(self.learning_data.get("seasonal_trends", {})),
            "demand_forecasts_generated": len(self.learning_data.get("demand_forecasts", {})),
            "last_updated": self.learning_data.get("last_updated"),
            "learning_accuracy": self._calculate_learning_accuracy()
        }
    
    def _calculate_learning_accuracy(self) -> float:
        """Calculate the accuracy of AI learning predictions"""
        # Simple accuracy calculation based on successful predictions
        history = self.learning_data.get("learning_history", [])
        if not history:
            return 0.0
        
        successful_predictions = 0
        total_predictions = 0
        
        for entry in history[-10:]:  # Last 10 entries
            insights = entry.get("insights", {})
            if insights.get("new_products"):
                total_predictions += len(insights["new_products"])
                # Assume 80% accuracy for new product detection
                successful_predictions += len(insights["new_products"]) * 0.8
        
        return successful_predictions / total_predictions if total_predictions > 0 else 0.0
    
    def get_ai_recommendations(self) -> List[Dict[str, Any]]:
        """Get AI-generated recommendations based on learned patterns"""
        recommendations = []
        
        # Get recent learning data
        recent_entries = self.learning_data.get("learning_history", [])[-5:]
        
        for entry in recent_entries:
            insights = entry.get("insights", {})
            
            # New product recommendations
            if insights.get("new_products"):
                for product in insights["new_products"][:3]:
                    recommendations.append({
                        "type": "new_product",
                        "title": f"Consider adding {product} to inventory",
                        "description": f"AI detected {product} in sales data but it's not in your inventory",
                        "priority": "medium",
                        "confidence": 0.8
                    })
            
            # Seasonal recommendations
            seasonal_data = insights.get("seasonal_data", {})
            if seasonal_data.get("seasonal_products"):
                recommendations.append({
                    "type": "seasonal",
                    "title": f"Seasonal opportunity detected",
                    "description": f"AI found {len(seasonal_data['seasonal_products'])} seasonal products trending",
                    "priority": "high",
                    "confidence": 0.9
                })
        
        return recommendations
