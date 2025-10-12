from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import os
import shutil
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from app.services.supabase_service import SupabaseService
from app.services.notification_service import NotificationService
from pydantic import BaseModel
from typing import Optional, Dict, Any

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

# Initialize services
supabase_service = SupabaseService()
notification_service = NotificationService()

# Authentication models
class LoginRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    password_hash: str

class AddProductRequest(BaseModel):
    name: str
    category: str
    current_stock: float = 0
    min_stock: float = 0
    unit: str = "ml"
    is_ready_made: bool = False
    cost_per_unit: float = 0
    package_size: float = 0
    package_unit: str = "ml"

# Security functions
def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

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
            username="caner0119",
            password_hash=hash_password("stock2025")
        ))
        # Add additional admin user for development
        admin_users.append(User(
            username="derda2412",
            password_hash=hash_password("woden2025")
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

# Cloud sync endpoints removed - using Excel upload instead

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
            "cloud_sync_test": "/api/cloud/test-connection",
            "cloud_sync_now": "/api/cloud/sync",
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
    product_data: AddProductRequest,
    username: str = Depends(verify_token)
):
    """Add a new product to the stock list"""
    try:
        result = supabase_service.add_new_stock_item(
            name=product_data.name,
            category=product_data.category,
            current_stock=product_data.current_stock,
            min_stock=product_data.min_stock,
            unit=product_data.unit,
            is_ready_made=product_data.is_ready_made,
            cost_per_unit=product_data.cost_per_unit,
            package_size=product_data.package_size,
            package_unit=product_data.package_unit
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

            # DARA Excel dosyası mı kontrol et
            print(f"DEBUG: Processing file: {file.filename}")
            if file.filename and ("dara" in file.filename.lower() or file.filename.endswith((".xls", ".xlsx"))):
                print("DEBUG: Using DARA Excel processor")
                # DARA Excel processor kullan
                try:
                    from app.services.dara_excel_processor import DaraExcelProcessor
                    dara_processor = DaraExcelProcessor(supabase_service)
                    result = dara_processor.process_dara_excel(temp_file_path)
                    print(f"DEBUG: DARA processor result: {result}")
                except Exception as e:
                    print(f"DEBUG: DARA processor error: {str(e)}")
                    # Fallback to standard processing
                    result = supabase_service.process_sales_excel(temp_file_path)
                
                # DARA formatından standart formata dönüştür
                if result.get("success"):
                    processed_sales = []
                    if result.get("saved_count", 0) > 0:
                        processed_sales.append({
                            "date": result.get("date"),
                            "total_sales": 0,  # Will be filled from Supabase
                            "items_processed": result.get("processed_count", 0)
                        })
                    
                    result = {
                        "success": True,
                        "message": f"DARA Excel processed. {result.get('processed_count', 0)} rows handled, {result.get('saved_count', 0)} succeeded.",
                        "processed_sales": processed_sales,
                        "errors": result.get("errors", []),
                        "total_sales": 0,  # Will be calculated from actual data
                        "learning_insights": {
                            "total_processed": result.get("processed_count", 0),
                            "successful_sales": result.get("saved_count", 0),
                            "failed_sales": len(result.get("errors", [])),
                            "ai_learning": {
                                "source": "dara_excel_import",
                                "processing_method": "dara_excel_processor_v1"
                            },
                            "system_improvements": [
                                "DARA Excel format otomatik tespit edildi",
                                "Satış verileri başarıyla işlendi",
                                "AI Analytics için hazır"
                            ]
                        }
                    }
            else:
                print("DEBUG: Using standard Excel processor")
                # Standart Excel işleme
                result = supabase_service.process_sales_excel(temp_file_path)

            # After processing, attempt to email low-stock alerts
            try:
                alerts_resp = await get_alerts()
                alerts = alerts_resp.get("alerts", []) if isinstance(alerts_resp, dict) else []
                if alerts:
                    # Critical: items with min_stock > 0 and current <= min
                    critical = [a for a in alerts if float(a.get('min_stock', 0) or 0) > 0 and float(a.get('current_stock', 0) or 0) <= float(a.get('min_stock', 0) or 0)]
                    # Sort by percent below min (lowest current/min first)
                    def pct(a):
                        cur = float(a.get('current_stock', 0) or 0)
                        mn = float(a.get('min_stock', 0) or 0)
                        return 999 if mn == 0 else max(0.0, (mn - cur) / mn * 100.0)
                    critical.sort(key=pct, reverse=True)

                    lines = ["Low Stock Alerts\nItems that need immediate attention\n"]
                    for a in critical:
                        cur = float(a.get('current_stock', 0) or 0)
                        mn = float(a.get('min_stock', 0) or 0)
                        perc = 0 if mn == 0 else int(round((mn - cur) / mn * 100))
                        lines.append(f"Critical\n{a['material_name']}\nCurrent: {int(cur) if cur.is_integer() else cur} {''}\u007C Min: {int(mn) if mn.is_integer() else mn} {''}")
                        lines.append(f"-{perc}% below minimum\n")

                    # Fallback: if no critical (e.g., all min=0), include all alerts without percent
                    if not critical:
                        for a in alerts:
                            lines.append(f"{a['material_name']} — Current: {a['current_stock']} | Min: {a['min_stock']} ({a['alert_type']})")

                    subject = f"WODEN: Low Stock Alerts — {len(critical) or len(alerts)} items"
                    body = "\n".join(lines)
                    notification_service.send_email(subject, body)
            except Exception:
                pass

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
        
        print(f"DEBUG: Getting analysis data for {days} days")
        
        # Get sales data from Supabase
        sales_data = supabase_service.get_sales_data(days)
        print(f"DEBUG: Sales data: {sales_data}")
        
        # Check if we have any sales data at all
        if not sales_data or sales_data.get("total_sales", 0) == 0:
            print("DEBUG: No sales data found, checking sales_history table directly...")
            # Direct query to see what's in the table
            try:
                response = supabase_service.client.table("sales_history").select("*").order("created_at", desc=True).limit(5).execute()
                print(f"DEBUG: Recent sales_history records: {response.data}")
            except Exception as e:
                print(f"DEBUG: Error querying sales_history: {str(e)}")
        
        # Get stock data for low stock alerts
        stock_list = supabase_service.get_flat_stock_list()
        print(f"DEBUG: Stock list count: {len(stock_list)}")
        
        # Low stock alerts
        low_stock_alerts = []
        for item in stock_list:
            current_stock = float(item.get("current_stock", 0))
            min_stock = float(item.get("min_stock", 0))
            
            # Handle case where min_stock is 0 (avoid division by zero)
            if min_stock == 0:
                if current_stock == 0:
                    # Both are 0, consider it critical
                    low_stock_alerts.append({
                        "name": item.get("name", ""),
                        "current": current_stock,
                        "min": min_stock,
                        "unit": item.get("unit", ""),
                        "percentage": "NaN% below minimum"
                    })
                else:
                    # Current > 0 but min = 0, this is actually fine
                    continue
            elif current_stock <= min_stock:
                percentage = ((current_stock - min_stock) / min_stock) * 100
                low_stock_alerts.append({
                    "name": item.get("name", ""),
                    "current": current_stock,
                    "min": min_stock,
                    "unit": item.get("unit", ""),
                    "percentage": f"{percentage:.0f}% below minimum"
                })
        
        # Get Excel sales report analysis data (if available)
        excel_analysis = get_excel_analysis_data(days)
        
        # Merge Excel analysis data with existing sales data
        enhanced_top_products = sales_data.get("top_products", [])
        if excel_analysis.get("top_products"):
            # Excel'den gelen ürün verilerini mevcut verilerle birleştir
            excel_products = excel_analysis["top_products"]
            for excel_product in excel_products:
                # Aynı ürün var mı kontrol et
                existing_product = next((p for p in enhanced_top_products if p["name"].upper() == excel_product["product_name"].upper()), None)
                if existing_product:
                    # Mevcut veriyi güncelle
                    existing_product["quantity"] += excel_product["quantity"]
                    existing_product["revenue"] = existing_product.get("revenue", 0) + excel_product["amount"]
                else:
                    # Yeni ürün ekle
                    enhanced_top_products.append({
                        "name": excel_product["product_name"],
                        "quantity": excel_product["quantity"],
                        "revenue": excel_product["amount"],
                        "percentage": 0  # Will be calculated below
                    })
            
            # Yüzdelik hesapla
            total_sales = sum(p.get("quantity", 0) for p in enhanced_top_products)
            for product in enhanced_top_products:
                product["percentage"] = (product.get("quantity", 0) / total_sales * 100) if total_sales > 0 else 0
            
            # Gelir bazında sırala
            enhanced_top_products.sort(key=lambda x: x.get("revenue", 0), reverse=True)
        
        # Excel demografik verilerini ekle
        demographics = {}
        if excel_analysis.get("demographics"):
            demographics = excel_analysis["demographics"]
        
        # Excel kategori analizini ekle
        excel_categories = excel_analysis.get("category_breakdown", {})
        enhanced_category_breakdown = sales_data.get("category_breakdown", [])
        
        # Ensure we have proper data structure with Excel enhancements
        result = {
            "totalSales": sales_data.get("total_sales", 0),
            "totalRevenue": excel_analysis.get("sales_summary", {}).get("total_amount", 0),
            "topProducts": enhanced_top_products[:10],  # Top 10
            "lowStockAlerts": low_stock_alerts,
            "dailyTrends": sales_data.get("daily_trends", []),
            "categoryBreakdown": enhanced_category_breakdown,
            "demographics": demographics,  # Excel'den gelen demografik veriler
            "excelAnalysis": {  # Excel'den çıkarılan ek analiz verileri
                "company": excel_analysis.get("sales_summary", {}).get("company", ""),
                "dateRange": excel_analysis.get("sales_summary", {}).get("date_range", ""),
                "totalQuantity": excel_analysis.get("sales_summary", {}).get("total_quantity", 0),
                "categoryStats": excel_categories
            }
        }
        
        print(f"DEBUG: Enhanced analysis result with Excel data: {result}")
        return result
        
    except Exception as e:
        print(f"ERROR: Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

def get_excel_analysis_data(days: int = 7) -> Dict[str, Any]:
    """Get Excel sales report analysis data from recent uploads"""
    try:
        # Get recent sales history that includes Excel analysis data
        result = supabase_service.get_recent_excel_analysis(days)
        if result["success"]:
            return result["data"]
        else:
            print(f"WARNING: Excel analysis data not available: {result.get('error', 'Unknown error')}")
            return {}
    except Exception as e:
        print(f"WARNING: Could not get Excel analysis data: {str(e)}")
        return {}

@app.post("/api/test/sales-data")
async def create_test_sales_data():
    """Create test sales data for debugging AI Analytics integration"""
    try:
        import json
        from datetime import datetime, timezone, timedelta
        
        # Create test sales data for the last 7 days
        test_data = []
        for i in range(7):
            date = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            test_data.append({
                "date": date,
                "total_quantity": 50 + (i * 10),  # Increasing sales
                "total_sales": 50 + (i * 10),
                "items_sold": json.dumps([
                    {"product": "ESPRESSO", "quantity": 20 + (i * 2)},
                    {"product": "AMERICANO", "quantity": 15 + (i * 3)},
                    {"product": "LATTE", "quantity": 10 + (i * 2)},
                    {"product": "CAPPUCCINO", "quantity": 5 + i}
                ]),
                "learning_data": json.dumps({"test": True}),
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        
        # Insert test data
        for data in test_data:
            try:
                result = supabase_service.client.table("sales_history").upsert(data).execute()
                print(f"DEBUG: Test data inserted for {data['date']}: {result.data}")
            except Exception as e:
                print(f"ERROR: Failed to insert test data for {data['date']}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Created {len(test_data)} test sales records",
            "data": test_data
        }
        
    except Exception as e:
        print(f"ERROR: Failed to create test sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating test data: {str(e)}")

@app.post("/api/refresh-data")
async def refresh_analysis_data():
    """Force refresh of analysis and recommendations data"""
    try:
        # This endpoint can be called after Excel uploads to refresh the analysis
        # The frontend can call this to ensure data is up-to-date
        
        # Get fresh data
        sales_data = supabase_service.get_sales_data(30)
        stock_list = supabase_service.get_flat_stock_list()
        
        # Generate fresh recommendations
        recommendations = []
        stock_recommendations = generate_stock_recommendations(stock_list)
        recommendations.extend(stock_recommendations)
        
        sales_recommendations = generate_sales_recommendations(sales_data)
        recommendations.extend(sales_recommendations)
        
        business_recommendations = generate_business_recommendations(stock_list, sales_data)
        recommendations.extend(business_recommendations)
        
        seasonal_recommendations = generate_seasonal_recommendations()
        recommendations.extend(seasonal_recommendations)
        
        ai_recommendations = generate_ai_learning_recommendations(sales_data)
        recommendations.extend(ai_recommendations)
        
        return {
            "success": True,
            "message": "Data refreshed successfully",
            "sales_data": sales_data,
            "recommendations_count": len(recommendations),
            "stock_items_count": len(stock_list)
        }
        
    except Exception as e:
        print(f"ERROR: Failed to refresh data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")

@app.get("/api/recommendations")
async def get_recommendations():
    """Get AI-powered recommendations based on sales data and stock levels"""
    try:
        # Get current data
        stock_list = supabase_service.get_flat_stock_list()
        sales_data = supabase_service.get_sales_data(30)  # Last 30 days
        
        print(f"DEBUG: Generating recommendations with {len(stock_list)} stock items and {sales_data.get('total_sales', 0)} total sales")
        
        recommendations = []
        
        # 1. Stock-based recommendations
        stock_recommendations = generate_stock_recommendations(stock_list)
        recommendations.extend(stock_recommendations)
        
        # 2. Sales-based recommendations
        sales_recommendations = generate_sales_recommendations(sales_data)
        recommendations.extend(sales_recommendations)
        
        # 3. Business optimization recommendations
        business_recommendations = generate_business_recommendations(stock_list, sales_data)
        recommendations.extend(business_recommendations)
        
        # 4. Seasonal recommendations
        seasonal_recommendations = generate_seasonal_recommendations()
        recommendations.extend(seasonal_recommendations)
        
        # 5. AI Learning-based recommendations
        ai_recommendations = generate_ai_learning_recommendations(sales_data)
        recommendations.extend(ai_recommendations)
        
        # Sort by priority and impact
        recommendations.sort(key=lambda x: (x.get('priority', 3), x.get('impact', 'low') == 'high'), reverse=True)
        
        print(f"DEBUG: Generated {len(recommendations)} total recommendations")
        return {"recommendations": recommendations}
        
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        # Return fallback recommendations
        return {"recommendations": get_fallback_recommendations()}

def generate_stock_recommendations(stock_list):
    """Generate stock-based recommendations"""
    recommendations = []
    
    for item in stock_list:
        current_stock = float(item.get("current_stock", 0))
        min_stock = float(item.get("min_stock", 0))
        name = item.get("name", "")
        unit = item.get("unit", "units")
        
        if current_stock == 0:
                recommendations.append({
                "id": f"stock_urgent_{len(recommendations) + 1}",
                    "type": "stock",
                "title": f"🚨 Acil Stok: {name}",
                "description": f"{name} tamamen tükendi ve acil yeniden stoklanması gerekiyor",
                    "impact": "high",
                "implementation": f"{name} için hemen tedarikçilerden sipariş verin",
                "expectedResult": "İş kesintisini önleyin ve müşteri memnuniyetini koruyun",
                "priority": 1,
                "category": "stok",
                "urgency": "critical"
            })
        elif current_stock <= min_stock * 0.5:
                recommendations.append({
                "id": f"stock_critical_{len(recommendations) + 1}",
                    "type": "stock",
                "title": f"⚠️ Kritik Stok: {name}",
                "description": f"{name} minimum seviyenin %50'sinin altında ({current_stock} {unit} kaldı)",
                "impact": "high",
                "implementation": f"{name} için acil sipariş planlayın",
                "expectedResult": "Stok tükenmesini önleyin",
                "priority": 1,
                "category": "stok",
                "urgency": "high"
            })
        elif current_stock <= min_stock:
            recommendations.append({
                "id": f"stock_low_{len(recommendations) + 1}",
                "type": "stock",
                "title": f"📉 Düşük Stok: {name}",
                "description": f"{name} minimum seviyenin altında ({current_stock} {unit} kaldı)",
                    "impact": "medium",
                "implementation": f"{name} için yakın zamanda yeniden stoklama planlayın",
                "expectedResult": "Optimal stok seviyelerini koruyun",
                "priority": 2,
                "category": "stok",
                "urgency": "medium"
            })
    
    return recommendations

def generate_sales_recommendations(sales_data):
    """Generate sales-based recommendations enhanced with Excel data"""
    recommendations = []
    
    if not sales_data or not sales_data.get("top_products"):
        return recommendations
    
    # Get Excel analysis data for enhanced recommendations
    excel_analysis = get_excel_analysis_data(7)
    
    top_products = sales_data["top_products"][:5]
    total_sales = sales_data.get("total_sales", 0)
    
    # High-performing product recommendations with Excel data
    for i, product in enumerate(top_products):
        if product["percentage"] > 15:  # High market share
            
            # Excel'den gelen veri ile karşılaştır
            excel_top_products = excel_analysis.get("top_products", [])
            excel_product_match = next((p for p in excel_top_products if p["product_name"].upper() == product["name"].upper()), None)
            
            description = f"{product['name']} toplam satışların %{product['percentage']:.1f}'ini oluşturuyor. Bu ürünü daha da büyütmek için özel kampanyalar düşünün"
            
            if excel_product_match:
                unit_price = excel_product_match.get("unit_price", 0)
                revenue = excel_product_match.get("amount", 0)
                description += f" Excel raporuna göre {revenue:.0f} TL gelir, birim fiyatı: {unit_price:.2f} TL."
            
            recommendations.append({
                "id": f"sales_high_{len(recommendations) + 1}",
                "type": "campaign",
                "title": f"🎯 {product['name']} - Yıldız Ürün",
                "description": description,
                "impact": "high",
                "implementation": f"{product['name']} için özel promosyonlar, sosyal medya kampanyaları ve müşteri sadakat programları oluşturun",
                "expectedResult": f"Bu ürünün satışlarında %20-30 daha artış bekleniyor",
                "priority": 1,
                "category": "pazarlama",
                "urgency": "medium"
            })
    
    # Excel demografik verilerine dayalı öneriler
    demographics = excel_analysis.get("demographics", {})
    if demographics:
        total_people = demographics.get("total_people", 0)
        total_tables = demographics.get("total_tables", 0)
        male_count = demographics.get("male_count", 0)
        female_count = demographics.get("female_count", 0)
        
        if total_people > 0 and total_tables > 0:
            avg_people_per_table = total_people / total_tables
            
            if avg_people_per_table > 3:
                recommendations.append({
                    "id": f"demographic_group_{len(recommendations) + 1}",
                    "type": "campaign",
                    "title": "👥 Grup Müşterileri İçin Özel Kampanya",
                    "description": f"Ortalama masa başına {avg_people_per_table:.1f} kişi düşüyor. Grup müşterilerine özel kampanyalar düşünün.",
                    "impact": "high",
                    "implementation": "Grup indirimleri, kombo menüler ve grup rezervasyon sistemi oluşturun.",
                    "expectedResult": "Grup müşteri sayısında artış ve ortalama sipariş değerinde yükselme",
                    "priority": 2,
                    "category": "demographics",
                    "urgency": "medium"
                })
        
        # Cinsiyet dağılımına göre öneriler
        if male_count > female_count * 2:
            recommendations.append({
                "id": f"demographic_male_{len(recommendations) + 1}",
                "type": "campaign",
                "title": "👨 Erkek Müşterilere Yönelik Kampanya",
                "description": f"Müşterilerinizin %{male_count/(male_count+female_count)*100:.0f}'i erkek. Erkek müşterilere yönelik özel kampanyalar düşünün.",
                "impact": "medium",
                "implementation": "Erkek müşterilerin tercih ettiği ürünlere odaklanan kampanyalar ve promosyonlar.",
                "expectedResult": "Erkek müşteri sadakati ve sipariş frekansında artış",
                "priority": 3,
                "category": "demographics",
                "urgency": "low"
            })
    
    # Excel kategori analizine dayalı öneriler
    category_stats = excel_analysis.get("category_breakdown", {})
    if category_stats:
        # En başarılı kategori
        best_category = max(category_stats.items(), key=lambda x: x[1]["total_amount"])
        category_name, category_data = best_category
        
        category_names = {
            "coffee": "Kahve",
            "tea": "Çay", 
            "pastry": "Pastane Ürünleri",
            "beverage": "İçecek",
            "other": "Diğer"
        }
        
        recommendations.append({
            "id": f"category_best_{len(recommendations) + 1}",
            "type": "campaign",
            "title": f"🏆 {category_names.get(category_name, category_name.title())} Kategorisi - En Başarılı",
            "description": f"{category_names.get(category_name, category_name.title())} kategorisi {category_data['total_amount']:.0f} TL ile en yüksek geliri sağlıyor.",
            "impact": "high",
            "implementation": "Bu kategoriye odaklanan yeni ürünler ve kampanyalar geliştirin.",
            "expectedResult": "Kategori gelirinde daha da artış",
            "priority": 2,
            "category": "category_analysis",
            "urgency": "medium"
        })
    
    # Low-performing product recommendations
    if len(top_products) > 3:
        low_performers = top_products[-2:]  # Last 2 products
        for product in low_performers:
            if product["percentage"] < 5:  # Low market share
                recommendations.append({
                    "id": f"sales_low_{len(recommendations) + 1}",
                    "type": "product",
                    "title": f"📈 {product['name']} - Geliştirme Fırsatı",
                    "description": f"{product['name']} düşük performans gösteriyor (%{product['percentage']:.1f}). Bu ürünü iyileştirmek veya değiştirmek için stratejiler geliştirin",
                    "impact": "medium",
                    "implementation": f"{product['name']} için fiyat optimizasyonu, ürün iyileştirmesi veya alternatif ürün değerlendirmesi yapın",
                    "expectedResult": "Ürün performansını artırın veya daha karlı alternatifler bulun",
                    "priority": 3,
                    "category": "ürün",
                    "urgency": "low"
                })
    
    return recommendations

def generate_business_recommendations(stock_list, sales_data):
    """Generate business optimization recommendations"""
    recommendations = []
    
    # Inventory optimization
    total_items = len(stock_list)
    zero_stock_items = len([item for item in stock_list if float(item.get("current_stock", 0)) == 0])
    low_stock_items = len([item for item in stock_list if float(item.get("current_stock", 0)) <= float(item.get("min_stock", 0))])
    
    if zero_stock_items > total_items * 0.1:  # More than 10% out of stock
        recommendations.append({
            "id": f"business_inventory_{len(recommendations) + 1}",
            "type": "stock",
            "title": "📊 Stok Yönetimi Optimizasyonu",
            "description": f"Toplam ürünlerin %{(zero_stock_items/total_items)*100:.1f}'i stokta yok. Stok yönetimi stratejinizi gözden geçirin",
            "impact": "high",
            "implementation": "Otomatik yeniden sipariş sistemleri kurun, minimum stok seviyelerini gözden geçirin ve tedarikçi ilişkilerini güçlendirin",
            "expectedResult": "Stok tükenmelerini %50 azaltın ve operasyonel verimliliği artırın",
            "priority": 1,
            "category": "operasyon",
            "urgency": "high"
        })
    
    # Sales trend analysis
    if sales_data and sales_data.get("daily_trends"):
        daily_trends = sales_data["daily_trends"]
        if len(daily_trends) > 1:
            recent_sales = daily_trends[-1]["totalSales"]
            avg_sales = sum(day["totalSales"] for day in daily_trends) / len(daily_trends)
            
            if recent_sales > avg_sales * 1.2:  # 20% above average
                recommendations.append({
                    "id": f"business_trend_up_{len(recommendations) + 1}",
                    "type": "campaign",
                    "title": "📈 Büyüme Momentumu",
                    "description": f"Son satışlar ortalamadan %{((recent_sales/avg_sales)-1)*100:.1f} daha yüksek. Bu momentumu sürdürmek için stratejiler geliştirin",
                    "impact": "high",
                    "implementation": "Mevcut başarılı stratejileri analiz edin, müşteri geri bildirimlerini toplayın ve büyüme planları oluşturun",
                    "expectedResult": "Büyüme trendini sürdürün ve yeni müşteri segmentlerine ulaşın",
                    "priority": 1,
                    "category": "strateji",
                    "urgency": "medium"
                })
    
    return recommendations

def generate_seasonal_recommendations():
    """Generate seasonal recommendations based on current date"""
    from datetime import datetime
    current_month = datetime.now().month
    
    recommendations = []
    
    # Summer recommendations (June-August)
    if current_month in [6, 7, 8]:
        recommendations.append({
            "id": f"seasonal_summer_{len(recommendations) + 1}",
            "type": "campaign",
            "title": "☀️ Yaz Kampanyası",
            "description": "Sıcak aylarda soğuk içecek satışlarını artırmak için özel kampanyalar başlatın",
            "impact": "high",
            "implementation": "Soğuk kahve, smoothie ve buzlu çay çeşitlerini öne çıkarın, teras ve dış mekan servisi geliştirin",
            "expectedResult": "Yaz aylarında soğuk içecek satışlarında %40 artış",
            "priority": 1,
            "category": "sezon",
            "urgency": "high"
        })
    
    # Winter recommendations (December-February)
    elif current_month in [12, 1, 2]:
        recommendations.append({
            "id": f"seasonal_winter_{len(recommendations) + 1}",
            "type": "campaign",
            "title": "❄️ Kış Kampanyası",
            "description": "Soğuk aylarda sıcak içecek ve atıştırmalık satışlarını artırmak için kampanyalar düzenleyin",
            "impact": "high",
            "implementation": "Sıcak çikolata, sıcak kahve çeşitleri ve sıcak atıştırmalıkları öne çıkarın",
            "expectedResult": "Kış aylarında sıcak içecek satışlarında %35 artış",
            "priority": 1,
            "category": "sezon",
            "urgency": "high"
        })
    
    # Holiday recommendations
    if current_month in [11, 12]:
        recommendations.append({
            "id": f"seasonal_holiday_{len(recommendations) + 1}",
            "type": "campaign",
            "title": "🎄 Tatil Kampanyası",
            "description": "Yıl sonu tatillerinde özel paketler ve hediyelik ürünler sunun",
            "impact": "medium",
            "implementation": "Hediye paketleri, özel tatil menüleri ve müşteri sadakat programları oluşturun",
            "expectedResult": "Tatil sezonunda ortalama sipariş değerinde %25 artış",
            "priority": 2,
            "category": "sezon",
            "urgency": "medium"
        })
    
    return recommendations

def generate_ai_learning_recommendations(sales_data):
    """Generate AI-powered recommendations based on learning data"""
    recommendations = []
    
    # Analyze top products for targeted recommendations
    top_products = sales_data.get("top_products", [])
    if top_products:
        # Get the top product
        top_product = top_products[0]
        product_name = top_product.get("name", "")
        percentage = top_product.get("percentage", 0)
        
        if percentage > 15:  # If top product has >15% market share
            recommendations.append({
                "id": f"ai_learning_{len(recommendations) + 1}",
                "type": "product",
                "title": f"📈 {product_name} - Yıldız Ürün Optimizasyonu",
                "description": f"{product_name} toplam satışların %{percentage:.1f}'ini oluşturuyor. Bu ürünü daha da büyütmek için özel stratejiler geliştirin",
                "impact": "high",
                "implementation": f"{product_name} için özel promosyonlar, sosyal medya kampanyaları ve müşteri sadakat programları oluşturun",
                "expectedResult": f"Bu ürünün satışlarında %20-30 daha artış bekleniyor",
                "priority": 1,
                "category": "pazarlama",
                "urgency": "medium"
            })
    
    # Analyze category breakdown for category-specific recommendations
    category_breakdown = sales_data.get("category_breakdown", [])
    if category_breakdown:
        # Find the dominant category
        dominant_category = max(category_breakdown, key=lambda x: x.get("percentage", 0))
        category_name = dominant_category.get("category", "").replace("_", " ").title()
        category_percentage = dominant_category.get("percentage", 0)
        
        if category_percentage > 50:  # If one category dominates
            recommendations.append({
                "id": f"ai_learning_{len(recommendations) + 1}",
                "type": "strategy",
                "title": f"🎯 {category_name} Kategorisi Odaklı Strateji",
                "description": f"{category_name} kategorisi toplam satışların %{category_percentage:.1f}'ini oluşturuyor. Bu kategoride çeşitliliği artırın",
                "impact": "medium",
                "implementation": f"{category_name} kategorisinde yeni ürünler ekleyin, mevcut ürünleri optimize edin",
                "expectedResult": f"Kategori çeşitliliğinde artış ve genel satışlarda %15-25 büyüme",
                "priority": 2,
                "category": "strateji",
                "urgency": "low"
            })
    
    # Analyze daily trends for operational recommendations
    daily_trends = sales_data.get("daily_trends", [])
    if len(daily_trends) >= 3:
        # Calculate trend direction
        recent_sales = [day.get("totalSales", 0) for day in daily_trends[-3:]]
        if len(recent_sales) >= 2:
            trend = recent_sales[-1] - recent_sales[0]
            if trend < 0:  # Declining trend
                recommendations.append({
                    "id": f"ai_learning_{len(recommendations) + 1}",
                    "type": "campaign",
                    "title": "📉 Satış Düşüşü Tespit Edildi",
                    "description": "Son 3 günde satışlarda düşüş trendi tespit edildi. Acil müdahale gerekli",
                    "impact": "high",
                    "implementation": "Hızlı promosyonlar, müşteri geri kazanma kampanyaları, fiyat optimizasyonu",
                    "expectedResult": "Satış trendini tersine çevirme ve %10-20 artış",
                    "priority": 1,
                    "category": "operasyon",
                    "urgency": "critical"
                })
            elif trend > 0:  # Growing trend
                recommendations.append({
                    "id": f"ai_learning_{len(recommendations) + 1}",
                    "type": "strategy",
                    "title": "📈 Pozitif Trend Devam Ettirme",
                    "description": "Son 3 günde pozitif satış trendi tespit edildi. Bu momentumu koruyun",
                    "impact": "medium",
                    "implementation": "Mevcut stratejileri sürdürün, başarılı kampanyaları genişletin",
                    "expectedResult": "Mevcut pozitif trendi sürdürme ve istikrarlı büyüme",
                    "priority": 3,
                    "category": "strateji",
                    "urgency": "low"
                })
    
    return recommendations

def get_fallback_recommendations():
    """Fallback recommendations when data is not available"""
    return [
        {
            "id": "fallback_1",
            "type": "stock",
            "title": "📊 Stok Analizi Yapın",
            "description": "Mevcut stok seviyelerinizi analiz edin ve minimum stok seviyelerini belirleyin",
                "impact": "medium",
            "implementation": "Excel dosyalarınızı yükleyerek stok analizi yapın",
            "expectedResult": "Daha iyi stok yönetimi ve maliyet optimizasyonu",
            "priority": 2,
            "category": "genel",
            "urgency": "medium"
        },
        {
            "id": "fallback_2",
            "type": "campaign",
            "title": "📈 Satış Verilerini İnceleyin",
            "description": "Satış verilerinizi analiz ederek en popüler ürünleri belirleyin",
            "impact": "high",
            "implementation": "Satış raporlarınızı inceleyin ve trend analizi yapın",
            "expectedResult": "Daha iyi ürün stratejileri ve pazarlama kampanyaları",
            "priority": 1,
            "category": "genel",
            "urgency": "high"
        }
    ]

@app.get("/api/campaigns")
async def get_campaigns():
    """Get AI-generated campaign suggestions"""
    try:
        # Get current sales data for campaign insights
        sales_data = supabase_service.get_sales_data(30)
        stock_list = supabase_service.get_flat_stock_list()
        
        campaigns = []
        
        # Generate campaigns based on top products
        if sales_data and sales_data.get("top_products"):
            top_products = sales_data["top_products"][:3]
            
            for i, product in enumerate(top_products):
                if product["percentage"] > 10:  # High-performing products
                    campaigns.append({
                        "id": f"campaign_{i+1}",
                        "name": f"{product['name']} Yıldız Kampanyası",
                        "description": f"{product['name']} ürününün başarısını sürdürmek için özel promosyonlar ve pazarlama kampanyaları",
                        "targetProducts": [product['name']],
                        "duration": "4 hafta",
                        "expectedIncrease": f"{product['name']} satışlarında %25-40 artış",
                        "cost": "Orta - Sosyal medya ve in-store promosyonlar",
                        "status": "suggested",
                        "priority": "high",
                        "category": "pazarlama"
                    })
        
        # Generate seasonal campaigns
        from datetime import datetime
        current_month = datetime.now().month
        
        if current_month in [6, 7, 8]:  # Summer
            campaigns.append({
                "id": "campaign_summer",
                "name": "☀️ Yaz Serinleme Kampanyası",
                "description": "Sıcak aylarda soğuk içecek satışlarını artırmak için özel yaz kampanyası",
                "targetProducts": ["ICED AMERICANO", "ICED FILTER COFFEE", "COLD BREW", "ICED LATTE"],
                "duration": "3 ay (Haziran-Ağustos)",
                "expectedIncrease": "Soğuk içecek satışlarında %40 artış",
                "cost": "Düşük - Sosyal medya ve in-store promosyonlar",
                "status": "suggested",
                "priority": "high",
                "category": "sezon"
            })
        elif current_month in [12, 1, 2]:  # Winter
            campaigns.append({
                "id": "campaign_winter",
                "name": "❄️ Kış Sıcaklık Kampanyası",
                "description": "Soğuk aylarda sıcak içecek ve atıştırmalık satışlarını artırmak için kış kampanyası",
                "targetProducts": ["TÜRK KAHVESİ", "FİLTRE KAHVE", "LATTE", "CAPPUCCINO"],
                "duration": "3 ay (Aralık-Şubat)",
                "expectedIncrease": "Sıcak içecek satışlarında %35 artış",
                "cost": "Düşük - Menü güncellemeleri ve promosyonlar",
                "status": "suggested",
                "priority": "high",
                "category": "sezon"
            })
        
        # Generate low-stock product campaigns
        low_stock_products = [item for item in stock_list if float(item.get("current_stock", 0)) <= float(item.get("min_stock", 0))]
        if low_stock_products:
            campaigns.append({
                "id": "campaign_inventory",
                "name": "📦 Stok Optimizasyon Kampanyası",
                "description": "Düşük stoklu ürünlerin satışını artırmak ve stok döngüsünü hızlandırmak için kampanya",
                "targetProducts": [item["name"] for item in low_stock_products[:5]],
                "duration": "2 hafta",
                "expectedIncrease": "Düşük stoklu ürünlerde %30 satış artışı",
                "cost": "Düşük - Fiyat indirimleri ve promosyonlar",
                "status": "suggested",
                "priority": "medium",
                "category": "stok"
            })
        
        # Generate bundle campaigns
        if sales_data and sales_data.get("top_products"):
            top_3 = sales_data["top_products"][:3]
            if len(top_3) >= 2:
                campaigns.append({
                    "id": "campaign_bundle",
                    "name": "🎁 Kombo Paket Kampanyası",
                    "description": "En popüler ürünleri birleştirerek kombo paketler oluşturma kampanyası",
                    "targetProducts": [product["name"] for product in top_3],
                    "duration": "Sürekli",
                    "expectedIncrease": "Ortalama sipariş değerinde %20 artış",
                    "cost": "Düşük - Menü düzenlemesi ve fiyatlandırma",
                    "status": "suggested",
                    "priority": "medium",
                    "category": "pazarlama"
                })
        
        return {"campaigns": campaigns}
        
    except Exception as e:
        print(f"Error generating campaigns: {str(e)}")
        # Return fallback campaigns
        return {"campaigns": [
            {
                "id": "campaign_fallback",
                "name": "📊 Veri Analizi Kampanyası",
                "description": "Mevcut satış verilerinizi analiz ederek kampanya stratejileri geliştirin",
                "targetProducts": ["Tüm Ürünler"],
                "duration": "1 hafta",
                "expectedIncrease": "Daha iyi kampanya stratejileri",
                "cost": "Düşük - Veri analizi ve planlama",
                "status": "suggested",
                "priority": "high",
                "category": "genel"
            }
        ]}

@app.get("/api/alerts")
async def get_alerts():
    """Get current stock alerts"""
    try:
        stock_list = supabase_service.get_stock_list()
        # Fallback to flat list if needed
        if not isinstance(stock_list, list):
            try:
                stock_list = supabase_service.get_flat_stock_list()
            except Exception:
                stock_list = []

        alerts = []
        for item in stock_list or []:
            if not isinstance(item, dict):
                continue
            current_stock = float(item.get("current_stock", 0) or 0)
            min_stock = float(item.get("min_stock", 0) or 0)
            if current_stock <= min_stock:
                alert_type = "out_of_stock" if current_stock == 0 else "low_stock"
                alerts.append({
                    "material_id": item.get("id") or item.get("material_id"),
                    "material_name": item.get("name") or item.get("material_name"),
                    "current_stock": current_stock,
                    "min_stock": min_stock,
                    "alert_type": alert_type,
                    "message": f"{(item.get('name') or 'Item')} is {'out of stock' if current_stock == 0 else 'below minimum level'}",
                    "category": item.get("category", "")
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

@app.api_route("/api/alerts/send-email-test", methods=["GET", "POST"])
async def send_alerts_email_test():
    """Manually send low stock alerts email to verify email configuration."""
    try:
        alerts_resp = await get_alerts()
        alerts = alerts_resp.get("alerts", []) if isinstance(alerts_resp, dict) else []

        # Build critical list and message (same formatting as upload flow)
        critical = [
            a for a in alerts
            if float(a.get('min_stock', 0) or 0) > 0 and float(a.get('current_stock', 0) or 0) <= float(a.get('min_stock', 0) or 0)
        ]

        def pct(a):
            cur = float(a.get('current_stock', 0) or 0)
            mn = float(a.get('min_stock', 0) or 0)
            return 999 if mn == 0 else max(0.0, (mn - cur) / mn * 100.0)

        critical.sort(key=pct, reverse=True)

        lines = ["Low Stock Alerts\nItems that need immediate attention\n"]
        for a in critical:
            cur = float(a.get('current_stock', 0) or 0)
            mn = float(a.get('min_stock', 0) or 0)
            perc = 0 if mn == 0 else int(round((mn - cur) / mn * 100))
            lines.append(f"Critical\n{a['material_name']}\nCurrent: {int(cur) if cur.is_integer() else cur} | Min: {int(mn) if mn.is_integer() else mn}")
            lines.append(f"-{perc}% below minimum\n")

        if not critical:
            for a in alerts:
                lines.append(f"{a['material_name']} — Current: {a['current_stock']} | Min: {a['min_stock']} ({a['alert_type']})")

        subject = f"WODEN: Low Stock Alerts — {len(critical) or len(alerts)} items"
        body = "\n".join(lines)

        # Build HTML version
        def row(name, cur, mn, perc):
            return f"<tr><td style='padding:8px 12px;border-bottom:1px solid #eee;'>Critical</td><td style='padding:8px 12px;border-bottom:1px solid #eee;'><strong>{name}</strong><div style='color:#666;font-size:12px;'>Current: {cur} | Min: {mn}</div></td><td style='padding:8px 12px;border-bottom:1px solid #eee;color:#b91c1c;'>-{perc}%</td></tr>"

        if critical:
            rows = []
            for a in critical:
                cur = float(a.get('current_stock', 0) or 0)
                mn = float(a.get('min_stock', 0) or 0)
                perc = 0 if mn == 0 else int(round((mn - cur) / mn * 100))
                rows.append(row(a['material_name'], int(cur) if cur.is_integer() else cur, int(mn) if mn.is_integer() else mn, perc))
            table = """
            <table cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse;">
              <thead>
                <tr>
                  <th align="left" style="padding:8px 12px;border-bottom:2px solid #111;">Severity</th>
                  <th align="left" style="padding:8px 12px;border-bottom:2px solid #111;">Item</th>
                  <th align="left" style="padding:8px 12px;border-bottom:2px solid #111;">Below Min</th>
                </tr>
              </thead>
              <tbody>
            """ + "".join(rows) + """
              </tbody>
            </table>
            """
        else:
            table = "<p>No critical items at the moment.</p>"

        html = f"""
        <div style='font-family:Inter,Arial,sans-serif;line-height:1.5;color:#111;'>
          <h2 style='margin:0 0 8px;'>Low Stock Alerts</h2>
          <div style='color:#444;margin-bottom:16px;'>Items that need immediate attention</div>
          {table}
          <div style='color:#888;font-size:12px;margin-top:16px;'>This message was generated by WODEN Stock AI.</div>
        </div>
        """

        using = "resend" if notification_service.resend_api_key and notification_service.resend_from else ("smtp" if notification_service.smtp_user and notification_service.smtp_pass else "none")
        has_to = bool(notification_service.default_to)
        has_from = bool(notification_service.resend_from or notification_service.default_from)
        has_key = bool(notification_service.resend_api_key)
        if not has_to:
            return {"sent": False, "using": using, "alerts": len(alerts), "critical": len(critical), "error": "No recipient configured (ALERT_EMAIL_TO)", "last_error": notification_service.last_error, "has_to": has_to, "has_from": has_from, "has_key": has_key}
        sent = notification_service.send_email(subject, body, html_body=html)
        return {"sent": sent, "using": using, "alerts": len(alerts), "critical": len(critical), "error": notification_service.last_error, "has_to": has_to, "has_from": has_from, "has_key": has_key, "resend_from": notification_service.resend_from, "smtp_from": notification_service.default_from, "to": notification_service.default_to}
    except Exception as e:
        # Return diagnostics instead of 500 to ease debugging
        using = "resend" if notification_service.resend_api_key and notification_service.resend_from else ("smtp" if notification_service.smtp_user and notification_service.smtp_pass else "none")
        return {"sent": False, "using": using, "alerts": 0, "critical": 0, "error": str(e), "last_error": notification_service.last_error}

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

# ============================================================================
# AI SCHEDULER ENDPOINTS
# ============================================================================

@app.get("/api/baristas")
async def get_baristas():
    """Get all active baristas"""
    try:
        result = supabase_service.get_baristas()
        if result["success"]:
            return result["baristas"]
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving baristas: {str(e)}")

@app.post("/api/baristas")
async def create_barista(
    name: str = Form(...),
    email: str = Form(None),
    phone: str = Form(None),
    type: str = Form("full-time"),
    max_hours: int = Form(45),
    preferred_shifts: str = Form("[]"),  # JSON string
    skills: str = Form("[]"),  # JSON string
    username: str = Depends(verify_token)
):
    """Create a new barista"""
    try:
        import json
        preferred_shifts_list = json.loads(preferred_shifts) if preferred_shifts else []
        skills_list = json.loads(skills) if skills else []
        
        result = supabase_service.create_barista(
            name=name,
            email=email,
            phone=phone,
            type=type,
            max_hours=max_hours,
            preferred_shifts=preferred_shifts_list,
            skills=skills_list
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating barista: {str(e)}")

@app.put("/api/baristas/{barista_id}")
async def update_barista(
    barista_id: str,
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    type: str = Form(None),
    max_hours: int = Form(None),
    preferred_shifts: str = Form(None),
    skills: str = Form(None),
    is_active: bool = Form(None),
    username: str = Depends(verify_token)
):
    """Update a barista"""
    try:
        import json
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if type is not None:
            update_data["type"] = type
        if max_hours is not None:
            update_data["max_hours"] = max_hours
        if preferred_shifts is not None:
            update_data["preferred_shifts"] = json.loads(preferred_shifts)
        if skills is not None:
            update_data["skills"] = json.loads(skills)
        if is_active is not None:
            update_data["is_active"] = is_active
        
        result = supabase_service.update_barista(barista_id, update_data)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating barista: {str(e)}")

@app.delete("/api/baristas/{barista_id}")
async def delete_barista(barista_id: str, username: str = Depends(verify_token)):
    """Deactivate a barista (soft delete)"""
    try:
        result = supabase_service.deactivate_barista(barista_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating barista: {str(e)}")

@app.get("/api/schedules")
async def get_schedules():
    """Get all weekly schedules"""
    try:
        result = supabase_service.get_weekly_schedules()
        if result["success"]:
            return result["schedules"]
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving schedules: {str(e)}")

@app.post("/api/schedules/generate")
async def generate_ai_schedule(
    week_start: str = Form(...),
    preferences: str = Form(None)
):
    """Generate AI-powered weekly schedule with barista preferences"""
    try:
        from datetime import datetime, timedelta
        import json
        import sys
        import os
        
        # Add backend directory to path to import ai_scheduler
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        from ai_scheduler import AIScheduler
        
        # Parse week start date
        week_start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
        
        # Parse preferences if provided
        # Format from frontend: {barista_id: {dayOff: 0, preferredOpening: [0,1], preferredClosing: [2,3]}}
        # Convert to backend format: {barista_name: {preferred_day_off: 0, preferred_opening_days: [0,1], preferred_closing_days: [2,3]}}
        preferences_data = {}
        if preferences:
            try:
                frontend_prefs = json.loads(preferences)
                
                # Get baristas to map IDs to names
                baristas_result = supabase_service.get_baristas()
                if baristas_result["success"]:
                    baristas = baristas_result["baristas"]
                    barista_map = {b["id"]: b["name"] for b in baristas}
                    
                    # Convert preferences format
                    for barista_id, prefs in frontend_prefs.items():
                        barista_name = barista_map.get(barista_id)
                        if barista_name:
                            preferences_data[barista_name] = {
                                "preferred_day_off": prefs.get("dayOff") if prefs.get("dayOff", -1) >= 0 else None,
                                "preferred_opening_days": prefs.get("preferredOpening", []),
                                "preferred_closing_days": prefs.get("preferredClosing", [])
                            }
                    
                    print(f"✅ Converted preferences for {len(preferences_data)} baristas")
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid preferences JSON: {e}, using defaults")
        
        # Initialize AI Scheduler
        scheduler = AIScheduler()
        
        # Set preferences if provided
        if preferences_data:
            scheduler.set_barista_preferences(preferences_data)
        
        # Generate schedule
        schedule_result = scheduler.generate_weekly_schedule(week_start_date)
        
        # TODO: Save to Supabase
        # For now, return the generated schedule
        
        # Get baristas for ID mapping
        baristas_result = supabase_service.get_baristas()
        name_to_id_map = {}
        if baristas_result["success"]:
            name_to_id_map = {b["name"]: b["id"] for b in baristas_result["baristas"]}
        
        # Convert schedule result to frontend format
        shifts = []
        # AI Scheduler returns "schedule" not "weekly_schedule"
        weekly_schedule = schedule_result.get("schedule", {})
        if weekly_schedule:
            for date_str, day_schedule in weekly_schedule.items():
                # Convert date string to day index (0=Monday, 6=Sunday)
                from datetime import datetime
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                day_index = date_obj.weekday()  # 0=Monday, 6=Sunday
                
                # Add opening shifts
                openings_data = day_schedule.get("openings", [])
                if isinstance(openings_data, str):
                    # If it's a string like "Ahmet, Boran", split it
                    employee_names = [name.strip() for name in openings_data.split(',')]
                    openings_data = [{"employee": name} for name in employee_names]
                
                for shift in openings_data:
                    employee_name = shift["employee"]
                    barista_id = name_to_id_map.get(employee_name, employee_name)  # Fallback to name if ID not found
                    shifts.append({
                        "id": f"shift_{day_index}_{barista_id}_opening",
                        "barista_id": barista_id,
                        "day_of_week": day_index,
                        "shift_type": "morning",
                        "start_time": "07:30",
                        "end_time": "15:30",
                        "hours": 8,
                        "notes": shift.get("notes", "")
                    })
                
                # Add closing shifts
                closings_data = day_schedule.get("closings", [])
                if isinstance(closings_data, str):
                    # If it's a string like "Sultan, Ahmet, İlker, Boran", split it
                    employee_names = [name.strip() for name in closings_data.split(',')]
                    closings_data = [{"employee": name} for name in employee_names]
                
                for shift in closings_data:
                    employee_name = shift["employee"]
                    barista_id = name_to_id_map.get(employee_name, employee_name)  # Fallback to name if ID not found
                    shifts.append({
                        "id": f"shift_{day_index}_{barista_id}_closing",
                        "barista_id": barista_id,
                        "day_of_week": day_index,
                        "shift_type": "evening",
                        "start_time": "15:30",
                        "end_time": "00:30",
                        "hours": 9,
                        "notes": shift.get("notes", "")
                    })
        
        # Generate a unique schedule ID
        schedule_id = f"schedule_{week_start}_{int(datetime.now().timestamp())}"
        
        print(f"🔍 DEBUG: Created {len(shifts)} shifts")
        if shifts:
            print(f"🔍 DEBUG: First shift: {shifts[0]}")
        
        return {
            "success": True,
            "message": "Schedule generated successfully",
            "schedule_id": schedule_id,
            "week_start": week_start,
            "week_end": (week_start_date + timedelta(days=6)).strftime("%Y-%m-%d"),
            "shifts": shifts,
            "schedule": schedule_result  # Keep original for debugging
        }
        
    except Exception as e:
        import traceback
        print(f"Error generating schedule: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating schedule: {str(e)}")

@app.get("/api/schedules/{schedule_id}/shifts")
async def get_schedule_shifts(schedule_id: str):
    """Get shifts for a specific schedule"""
    try:
        result = supabase_service.get_schedule_shifts(schedule_id)
        if result["success"]:
            return result["shifts"]
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving shifts: {str(e)}")

@app.post("/api/schedules/{schedule_id}/publish")
async def publish_schedule(schedule_id: str, username: str = Depends(verify_token)):
    """Publish a schedule"""
    try:
        result = supabase_service.publish_schedule(schedule_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing schedule: {str(e)}")

@app.get("/api/time-off-requests")
async def get_time_off_requests():
    """Get all time-off requests"""
    try:
        result = supabase_service.get_time_off_requests()
        if result["success"]:
            return result["requests"]
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving time-off requests: {str(e)}")

@app.post("/api/time-off-requests")
async def create_time_off_request(
    barista_id: str = Form(...),
    request_date: str = Form(...),
    reason: str = Form("personal"),
    notes: str = Form(None)
):
    """Create a time-off request"""
    try:
        from datetime import datetime
        request_date_obj = datetime.strptime(request_date, "%Y-%m-%d").date()
        
        result = supabase_service.create_time_off_request(
            barista_id=barista_id,
            request_date=request_date_obj,
            reason=reason,
            notes=notes
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating time-off request: {str(e)}")

@app.put("/api/time-off-requests/{request_id}")
async def update_time_off_request(
    request_id: str,
    status: str = Form(...),
    reviewed_by: str = Form(...),
    username: str = Depends(verify_token)
):
    """Update time-off request status (approve/reject)"""
    try:
        result = supabase_service.update_time_off_request(request_id, status, reviewed_by)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating time-off request: {str(e)}")

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
    """Get comprehensive AI learning insights from Excel uploads"""
    try:
        from ai_learning_system import AILearningSystem
        
        # Initialize AI Learning System
        ai_learning = AILearningSystem(supabase_service)
        
        # Get AI learning summary
        ai_summary = ai_learning.get_learning_summary()
        ai_recommendations = ai_learning.get_ai_recommendations()
        
        # Get recent sales history with learning data
        response = supabase_service.client.table("sales_history").select("*").order("created_at", desc=True).limit(10).execute()
        
        learning_insights = {
            "recent_uploads": len(response.data),
            "total_learning_data": 0,
            "ai_learning_summary": ai_summary,
            "ai_recommendations": ai_recommendations,
            "system_improvements": [],
            "new_products_detected": [],
            "recommendations": [],
            "learning_accuracy": ai_summary.get("learning_accuracy", 0.0),
            "last_updated": ai_summary.get("last_updated")
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
                f"🤖 AI suggests adding '{product}' to your inventory" 
                for product in learning_insights["new_products_detected"][:3]
            ]
        
        return learning_insights
        
    except Exception as e:
        print(f"Error retrieving learning insights: {str(e)}")
        # Return fallback data
        return {
            "recent_uploads": 0,
            "total_learning_data": 0,
            "ai_learning_summary": {"learning_accuracy": 0.0},
            "ai_recommendations": [],
            "system_improvements": ["AI learning system initializing..."],
            "new_products_detected": [],
            "recommendations": [],
            "learning_accuracy": 0.0,
            "last_updated": None
        }

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