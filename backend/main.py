from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import os
import shutil
import hashlib
import secrets
from datetime import datetime, timedelta
from app.services.supabase_service import SupabaseService
from pydantic import BaseModel

app = FastAPI(
    title="Woden AI Stock Management System",
    description="Complete stock management system with recipe-based inventory control",
    version="2.0.0"
)

# CORS middleware - Allow both local development and production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://wodenstockai.vercel.app",
        "https://wodenstockai.vercel.app/",
        "https://www.wodenstockai.com",
        "https://www.wodenstockai.com/",
        "https://wodenstockai.com",
        "https://wodenstockai.com/",
        # Add any other domains you might use in the future
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Supabase service
supabase_service = SupabaseService()

# Authentication models
class LoginRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    password_hash: str

# Admin users with hashed passwords (use environment variables in production)
def get_admin_users():
    """Get admin users from environment variables or fallback to defaults"""
    admin_users = []
    
    # Try to get from environment variables first
    admin_username_1 = os.getenv("ADMIN_USERNAME_1")
    admin_password_1 = os.getenv("ADMIN_PASSWORD_1")
    admin_username_2 = os.getenv("ADMIN_USERNAME_2")
    admin_password_2 = os.getenv("ADMIN_PASSWORD_2")
    
    if admin_username_1 and admin_password_1:
        admin_users.append(User(
            username=admin_username_1,
            password_hash=hash_password(admin_password_1)
        ))
    else:
        # Fallback to default (for development only)
        admin_users.append(User(
            username="admin",
            password_hash=hash_password("admin123")
        ))
    
    if admin_username_2 and admin_password_2:
        admin_users.append(User(
            username=admin_username_2,
            password_hash=hash_password(admin_password_2)
        ))
    
    return admin_users

ADMIN_USERS = get_admin_users()

# Simple token storage (use Redis or database in production)
active_tokens = {}

# Security
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username: str, password: str) -> bool:
    """Verify user credentials"""
    password_hash = hash_password(password)
    is_valid = any(user.username == username and user.password_hash == password_hash for user in ADMIN_USERS)
    
    # Log authentication attempts (for security monitoring)
    if is_valid:
        print(f"✅ Successful login attempt for user: {username}")
    else:
        print(f"❌ Failed login attempt for user: {username}")
    
    return is_valid

def create_token(username: str) -> str:
    """Create a new authentication token"""
    token = secrets.token_urlsafe(32)
    active_tokens[token] = {
        "username": username,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify authentication token"""
    token = credentials.credentials
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token_data = active_tokens[token]
    if datetime.now() > token_data["expires_at"]:
        del active_tokens[token]
        raise HTTPException(status_code=401, detail="Token expired")
    
    return token_data["username"]

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        }
    )

@app.get("/")
async def root():
    return {"message": "Woden AI Stock Management System API", "version": "2.0.0"}

@app.get("/api")
async def api_info():
    return {
        "name": "Woden AI Stock Management System",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/auth/login",
            "stock": "/api/stock",
            "stock_update": "/api/stock/update",
            "sales_upload": "/api/sales/upload",
            "analysis": "/api/analysis",
            "recommendations": "/api/recommendations",
            "alerts": "/api/alerts",
            "summary": "/api/summary"
        }
    }

@app.post("/api/auth/login")
async def login(login_request: LoginRequest):
    """Authenticate user and return access token"""
    if verify_user(login_request.username, login_request.password):
        token = create_token(login_request.username)
        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "username": login_request.username
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/api/stock")
async def get_stock():
    """Get current stock list"""
    try:
        result = supabase_service.get_stock_list()
        
        # Debug logging
        print(f"DEBUG: Supabase result type: {type(result)}")
        print(f"DEBUG: Supabase result: {result}")
        
        if isinstance(result, dict) and result.get("success"):
            # Transform the data to match frontend expectations
            stock_data = result["data"]
            stock_list = []
            
            for category, items in stock_data.get("stock_data", {}).items():
                for item_name, item_data in items.items():
                    # Use the material_id from the database instead of constructing it
                    material_id = item_data.get("material_id", f"{category}_{item_name}")
                    stock_list.append({
                        "id": material_id,  # Use the actual material_id from database
                        "name": item_name,
                        "category": category,
                        "current_stock": item_data.get("current_stock", 0),
                        "min_stock": item_data.get("min_stock", 0),
                        "unit": item_data.get("unit", ""),
                        "package_size": item_data.get("package_size", 0),
                        "package_unit": item_data.get("package_unit", ""),
                        "cost_per_unit": item_data.get("cost_per_unit", 0.0),
                        "is_ready_made": item_data.get("is_ready_made", False),
                        "usage_per_order": item_data.get("usage_per_order", 0),
                        "usage_per_day": item_data.get("usage_per_day", 0),
                        "usage_type": item_data.get("usage_type", ""),
                        "can_edit": item_data.get("can_edit", True),
                        "edit_reason": item_data.get("edit_reason", ""),
                        "edit_message": item_data.get("edit_message", "")
                    })
            
            print(f"DEBUG: Returning {len(stock_list)} items")
            return {"stock_data": stock_list, "total_items": len(stock_list)}
        else:
            error_msg = result.get("message", "Unknown error") if isinstance(result, dict) else str(result)
            print(f"DEBUG: Supabase error: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        print(f"DEBUG: Exception in get_stock: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving stock: {str(e)}")

@app.post("/api/stock/update")
async def update_stock(
    material_id: str = Form(...), 
    new_stock: float = Form(...), 
    reason: str = Form("manual_update"),
    username: str = Depends(verify_token)
):
    """Update stock for a specific material"""
    try:
        result = supabase_service.update_stock_manually(material_id, new_stock, reason)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating stock: {str(e)}")

@app.post("/api/stock/add-product")
async def add_new_product(
    product_data: dict,
    username: str = Depends(verify_token)
):
    """Add a new product to the stock list"""
    try:
        result = supabase_service.add_new_stock_item(
            name=product_data.get("name"),
            category=product_data.get("category"),
            current_stock=product_data.get("current_stock", 0),
            min_stock=product_data.get("min_stock", 0),
            unit=product_data.get("unit", "ml"),
            is_ready_made=product_data.get("is_ready_made", False),
            cost_per_unit=product_data.get("cost_per_unit", 0),
            package_size=product_data.get("package_size", 0),
            package_unit=product_data.get("package_unit", "ml")
        )
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding product: {str(e)}")

@app.post("/api/stock/remove")
async def remove_stock_item(
    item_name: str = Form(...),
    username: str = Depends(verify_token)
):
    """Remove an item from the stock list"""
    try:
        # TODO: Implement item removal with Supabase
        return {
            "success": False,
            "message": "Item removal not yet implemented with Supabase. Please contact administrator."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing stock item: {str(e)}")

@app.post("/api/sales/upload")
async def upload_sales_excel(
    file: UploadFile = File(...),
    username: str = Depends(verify_token)
):
    """Upload and process daily sales Excel file"""
    try:
        # Validate file type
        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")

        temp_file_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            result = supabase_service.process_sales_excel(temp_file_path)
            if result.get("success"):
                return result
            else:
                raise HTTPException(status_code=400, detail=result.get("message", "Processing failed"))
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sales file: {str(e)}")

@app.post("/api/daily-consumption/apply")
async def apply_daily_consumption(force: bool = False):
    """Apply daily consumption for raw materials based on daily_usage_config.json"""
    try:
        result = supabase_service.apply_daily_consumption(force=force)
        # Debug log
        print(f"DEBUG: Daily consumption apply(force={force}) result: {result}")
        if isinstance(result, dict) and result.get("success"):
            return result
        # If result is a dict but failed, surface its message
        if isinstance(result, dict):
            raise HTTPException(status_code=400, detail=result.get("message", "Unknown error"))
        # Fallback
        raise HTTPException(status_code=400, detail="Unknown error applying daily consumption")
    except HTTPException:
        # Preserve original HTTP errors
        raise
    except Exception as e:
        # Include repr for better diagnostics
        raise HTTPException(status_code=500, detail=f"Error applying daily consumption: {repr(e)}")

@app.post("/api/daily-consumption/force")
async def force_daily_consumption():
    """Force apply daily consumption regardless of recent manual updates"""
    try:
        result = supabase_service.apply_daily_consumption(force=True)
        # Debug log
        print(f"DEBUG: Daily consumption apply(force=True) result: {result}")
        if isinstance(result, dict) and result.get("success"):
            return result
        if isinstance(result, dict):
            raise HTTPException(status_code=400, detail=result.get("message", "Unknown error"))
        raise HTTPException(status_code=400, detail="Unknown error applying daily consumption")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying daily consumption: {repr(e)}")

@app.post("/api/stock/clear-manual-flags")
async def clear_manual_update_flags(username: str = Depends(verify_token)):
    """Clear manual update flags to allow daily consumption"""
    try:
        result = supabase_service.clear_manual_update_flags()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing manual flags: {str(e)}")

@app.get("/api/analysis")
async def get_analysis(period: str = "7d"):
    """Get stock analysis data"""
    try:
        # Parse period (default to 7 days)
        days = 7
        if period.endswith('d'):
            try:
                days = int(period[:-1])
            except:
                days = 7
        
        # Get sales data from Supabase
        sales_data = supabase_service.get_sales_data(days)
        
        # Get stock data for low stock alerts
        stock_list = supabase_service.get_flat_stock_list()
        
        # Low stock alerts
        low_stock_alerts = []
        for item in stock_list:
            if float(item.get("current_stock", 0)) <= float(item.get("min_stock", 0)):
                low_stock_alerts.append({
                    "name": item.get("name", ""),
                    "current": item.get("current_stock", 0),
                    "min": item.get("min_stock", 0),
                    "unit": item.get("unit", "")
                })
        
        return {
            "totalSales": sales_data.get("total_sales", 0),
            "topProducts": sales_data.get("top_products", []),
            "lowStockAlerts": low_stock_alerts,
            "dailyTrends": sales_data.get("daily_trends", []),
            "categoryBreakdown": sales_data.get("category_breakdown", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

@app.get("/api/recommendations")
async def get_recommendations():
    """Get stock recommendations based on current levels"""
    try:
        stock_list = supabase_service.get_flat_stock_list()
        recommendations = []
        
        for item in stock_list:
            if float(item.get("current_stock", 0)) == 0:
                recommendations.append({
                    "id": f"rec_{len(recommendations) + 1}",
                    "type": "stock",
                    "title": f"Urgent Restock: {item.get('name','')}",
                    "description": f"Urgent: {item.get('name','')} is out of stock and needs immediate restocking",
                    "impact": "high",
                    "implementation": f"Order {item.get('name','')} immediately from suppliers",
                    "expectedResult": "Prevent business disruption and maintain customer satisfaction",
                    "priority": 1
                })
            elif float(item.get("current_stock", 0)) <= float(item.get("min_stock", 0)):
                recommendations.append({
                    "id": f"rec_{len(recommendations) + 1}",
                    "type": "stock",
                    "title": f"Low Stock Alert: {item.get('name','')}",
                    "description": f"Low stock alert: {item.get('name','')} is below minimum level ({item.get('current_stock',0)} {item.get('unit', 'units')} remaining)",
                    "impact": "medium",
                    "implementation": f"Plan restocking for {item.get('name','')} within the next few days",
                    "expectedResult": "Maintain optimal stock levels and prevent future stockouts",
                    "priority": 2
                })
        
        # Add some additional business recommendations
        additional_recommendations = [
            {
                "id": f"rec_{len(recommendations) + 1}",
                "type": "campaign",
                "title": "Yaz Kahve Promosyonu",
                "description": "Sıcak aylarda satışları artırmak için dondurulmuş kahve ürünlerine odaklanan yaz temalı bir kampanya başlatın",
                "impact": "high",
                "implementation": "Sosyal medya içeriği oluşturun, dondurulmuş içeceklerde indirim sunun, yeni yaz tatları tanıtın",
                "expectedResult": "Yaz aylarında dondurulmuş kahve satışlarında %25-30 artış bekleniyor",
                "priority": 2
            },
            {
                "id": f"rec_{len(recommendations) + 2}",
                "type": "product",
                "title": "Yeni Çay Çeşitleri Tanıtın",
                "description": "Mevcut çay popülaritesine dayanarak, premium çay seçenekleri ve bitkisel çeşitler eklemeyi düşünün",
                "impact": "medium",
                "implementation": "Tedarikçileri araştırın, yeni tatları test edin, çay kategorisi için pazarlama materyalleri oluşturun",
                "expectedResult": "Müşteri tabanını genişletin ve ortalama sipariş değerini artırın",
                "priority": 3
            },
            {
                "id": f"rec_{len(recommendations) + 3}",
                "type": "pricing",
                "title": "Paket Fiyatlandırma Stratejisi",
                "description": "Kahve + hamur işi kombinasyonları gibi sık sipariş edilen ürünler için combo teklifler oluşturun",
                "impact": "medium",
                "implementation": "Sipariş kalıplarını analiz edin, çekici paketler tasarlayın, promosyon materyalleri oluşturun",
                "expectedResult": "Ortalama sipariş değerini %15-20 artırın",
                "priority": 3
            }
        ]
        
        all_recommendations = recommendations + additional_recommendations
        
        return {
            "recommendations": all_recommendations,
            "total_recommendations": len(all_recommendations),
            "high_priority": len([r for r in all_recommendations if r["priority"] == 1]),
            "medium_priority": len([r for r in all_recommendations if r["priority"] == 2])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recommendations: {str(e)}")

@app.get("/api/alerts")
async def get_alerts():
    """Get current stock alerts"""
    try:
        stock_list = supabase_service.get_stock_list()
        alerts = []
        
        for item in stock_list:
            if item["current_stock"] <= item["min_stock"]:
                alert_type = "out_of_stock" if item["current_stock"] == 0 else "low_stock"
                alerts.append({
                    "material_id": item["id"],
                    "material_name": item["name"],
                    "current_stock": item["current_stock"],
                    "min_stock": item["min_stock"],
                    "alert_type": alert_type,
                    "message": f"{item['name']} is {'out of stock' if item['current_stock'] == 0 else 'below minimum level'}",
                    "category": item["category"]
                })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "low_stock_count": len([a for a in alerts if a["alert_type"] == "low_stock"]),
            "out_of_stock_count": len([a for a in alerts if a["alert_type"] == "out_of_stock"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")

@app.get("/api/enhanced-alerts")
async def get_enhanced_alerts():
    """Get enhanced stock alerts with urgency scoring"""
    try:
        result = supabase_service.get_enhanced_stock_alerts()
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enhanced alerts: {str(e)}")

@app.get("/api/profitability-analysis")
async def get_profitability_analysis():
    """Get profitability analysis for all products"""
    try:
        result = supabase_service.get_profitability_analysis()
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profitability analysis: {str(e)}")

@app.get("/api/smart-reorder")
async def get_smart_reorder_suggestions():
    """Get AI-powered smart reorder suggestions"""
    try:
        result = supabase_service.get_smart_reorder_suggestions()
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving smart reorder suggestions: {str(e)}")

@app.get("/api/seasonal-analysis")
async def get_seasonal_analysis():
    """Get seasonal analysis and trend detection"""
    try:
        result = supabase_service.get_seasonal_analysis()
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving seasonal analysis: {str(e)}")

@app.get("/api/ai-insights")
async def get_ai_insights():
    """Get comprehensive AI insights combining all analysis features"""
    try:
        # Get all analysis data
        enhanced_alerts = supabase_service.get_enhanced_stock_alerts()
        profitability = supabase_service.get_profitability_analysis()
        smart_reorder = supabase_service.get_smart_reorder_suggestions()
        seasonal = supabase_service.get_seasonal_analysis()
        
        # Combine insights
        insights = {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "enhanced_alerts": enhanced_alerts if enhanced_alerts["success"] else None,
            "profitability_analysis": profitability if profitability["success"] else None,
            "smart_reorder_suggestions": smart_reorder if smart_reorder["success"] else None,
            "seasonal_analysis": seasonal if seasonal["success"] else None,
            "summary": {
                "critical_alerts": enhanced_alerts.get("summary", {}).get("critical_alerts", 0) if enhanced_alerts["success"] else 0,
                "total_revenue": profitability.get("summary", {}).get("total_revenue", 0) if profitability["success"] else 0,
                "total_profit": profitability.get("summary", {}).get("total_profit", 0) if profitability["success"] else 0,
                "critical_reorders": smart_reorder.get("summary", {}).get("critical_items", 0) if smart_reorder["success"] else 0,
                "trend_direction": seasonal.get("trend_analysis", {}).get("overall_trend", "unknown") if seasonal["success"] else "unknown"
            }
        }
        
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving AI insights: {str(e)}")

@app.post("/api/pricing-data")
async def save_pricing_data(request: dict):
    """Save pricing data for products to improve profitability analysis"""
    try:
        product_name = request.get("product_name")
        selling_price = request.get("selling_price")
        ingredient_cost = request.get("ingredient_cost")
        
        if not all([product_name, selling_price, ingredient_cost]):
            raise HTTPException(status_code=400, detail="Missing required fields: product_name, selling_price, ingredient_cost")
        
        success = supabase_service.save_pricing_data(product_name, float(selling_price), float(ingredient_cost))
        
        if success:
            return {"success": True, "message": f"Pricing data saved for {product_name}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save pricing data")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving pricing data: {str(e)}")

@app.get("/api/learning-insights")
async def get_learning_insights():
    """Get insights about how the system is learning from Excel uploads"""
    try:
        # Get recent sales history with learning data
        response = supabase_service.client.table("sales_history").select("*").order("created_at", desc=True).limit(10).execute()
        
        learning_insights = {
            "recent_uploads": len(response.data),
            "total_learning_data": 0,
            "system_improvements": [],
            "new_products_detected": [],
            "recommendations": []
        }
        
        for record in response.data:
            learning_data = record.get("learning_data")
            if learning_data:
                try:
                    import json
                    data = json.loads(learning_data)
                    learning_insights["total_learning_data"] += 1
                    
                    if data.get("new_products"):
                        learning_insights["new_products_detected"].extend(data["new_products"])
                    
                    if data.get("system_improvements"):
                        learning_insights["system_improvements"].extend(data["system_improvements"])
                        
                except:
                    pass
        
        # Remove duplicates
        learning_insights["new_products_detected"] = list(set(learning_insights["new_products_detected"]))[:10]
        learning_insights["system_improvements"] = list(set(learning_insights["system_improvements"]))[:5]
        
        # Generate recommendations
        if learning_insights["new_products_detected"]:
            learning_insights["recommendations"] = [
                f"Consider adding '{product}' to your inventory" 
                for product in learning_insights["new_products_detected"][:3]
            ]
        
        return learning_insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving learning insights: {str(e)}")

@app.get("/api/summary")
async def get_summary():
    """Get stock summary statistics"""
    try:
        stock_list = supabase_service.get_stock_list()
        
        total_items = len(stock_list)
        low_stock_items = 0
        out_of_stock_items = 0
        total_value = 0.0
        
        for item in stock_list:
            if item["current_stock"] == 0:
                out_of_stock_items += 1
            elif item["current_stock"] <= item["min_stock"]:
                low_stock_items += 1
            
            # Calculate value if cost_per_unit is available
            cost_per_unit = item.get("cost_per_unit", 0.0)
            total_value += item["current_stock"] * cost_per_unit
        
        return {
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "total_value": total_value,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving summary: {str(e)}")

@app.get("/api/campaigns")
async def get_campaigns():
    """Get marketing campaign suggestions based on stock levels"""
    try:
        # This could be enhanced with AI recommendations later
        return {
            "campaigns": [
                                 {
                     "id": "1",
                     "name": "Stok Temizliği",
                     "description": "Yüksek stok seviyesindeki ürünleri envanter maliyetlerini azaltmak için teşvik edin",
                     "targetProducts": ["ESPRESSO", "LATTE", "AMERİCANO", "POĞAÇA"],
                     "duration": "2 hafta",
                     "expectedIncrease": "Yavaş hareket eden ürünlerde %25 artış",
                     "cost": "Düşük - ağırlıklı olarak promosyon fiyatlandırması",
                     "status": "suggested"
                 },
                 {
                     "id": "2",
                     "name": "Düşük Stok Uyarısı",
                     "description": "Minimum seviyelerin altındaki ürünleri izleyin ve yeniden stok planlaması yapın",
                     "targetProducts": ["TORKU SÜT", "TÜRK KAHVESİ ÇEKİRDEĞİ", "MENTA CUBANO ŞURUP"],
                     "duration": "Devam ediyor",
                     "expectedIncrease": "Stok tükenmesini önleyin",
                     "cost": "Orta - envanter yönetimi",
                     "status": "suggested"
                 },
                 {
                     "id": "3",
                     "name": "Yaz Soğuk Kahve Kampanyası",
                     "description": "Sıcak aylarda soğuk içecek satışlarını artırın",
                     "targetProducts": ["ICED AMERICANO", "ICED FILTER COFFEE", "COLD BREW"],
                     "duration": "3 ay (Haziran-Ağustos)",
                     "expectedIncrease": "Soğuk içecek satışlarında %30 artış",
                     "cost": "Düşük - sosyal medya promosyonu",
                     "status": "suggested"
                 }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving campaigns: {str(e)}")

@app.get("/api/sales/debug")
async def get_sales_debug():
    """Debug endpoint to view current sales data"""
    try:
        # TODO: Implement sales analytics with Supabase
        return {
            "total_sales_records": 0,
            "sales_data": [],
            "sample_analytics": {"message": "Sales analytics not yet implemented with Supabase"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sales debug info: {str(e)}")

@app.get("/api/stock/debug")
async def get_stock_debug():
    """Debug endpoint to view stock data structure"""
    try:
        result = supabase_service.get_stock_list()
        return {
            "supabase_result": result,
            "result_type": type(result).__name__,
            "has_success": "success" in result if isinstance(result, dict) else False,
            "has_data": "data" in result if isinstance(result, dict) else False,
            "result_keys": list(result.keys()) if isinstance(result, dict) else "Not a dict"
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# backend/main.py sonuna ekleyin
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)