from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
import shutil
from datetime import datetime
from app.stock_manager import StockManager

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
        # Add any other domains you might use in the future
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize stock manager
stock_manager = StockManager()

@app.get("/")
async def root():
    return {"message": "Woden AI Stock Management System API", "version": "2.0.0"}

@app.get("/api")
async def api_info():
    return {
        "name": "Woden AI Stock Management System",
        "version": "2.0.0",
        "endpoints": {
            "stock": "/api/stock",
            "stock_update": "/api/stock/update",
            "sales_upload": "/api/sales/upload",
            "analysis": "/api/analysis",
            "recommendations": "/api/recommendations",
            "alerts": "/api/alerts",
            "summary": "/api/summary"
        }
    }

@app.get("/api/stock")
async def get_stock():
    """Get current stock list"""
    try:
        stock_list = stock_manager.get_stock_list()
        return {"stock_data": stock_list, "total_items": len(stock_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stock: {str(e)}")

@app.post("/api/stock/update")
async def update_stock(material_id: str = Form(...), new_stock: float = Form(...), reason: str = Form("manual_update")):
    """Update stock for a specific material"""
    try:
        result = stock_manager.update_stock_manually(material_id, new_stock, reason)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating stock: {str(e)}")

@app.post("/api/sales/upload")
async def upload_sales_excel(file: UploadFile = File(...)):
    """Upload and process daily sales Excel file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")
        
        # Save uploaded file temporarily
        temp_file_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Process the Excel file
            result = stock_manager.process_sales_excel(temp_file_path)
            
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["message"])
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sales file: {str(e)}")

@app.post("/api/daily-consumption/apply")
async def apply_daily_consumption():
    """Apply daily consumption for raw materials based on daily_usage_config.json"""
    try:
        result = stock_manager.apply_daily_consumption()
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying daily consumption: {str(e)}")

@app.get("/api/analysis")
async def get_analysis(period: str = "7d"):
    """Get stock analysis data"""
    try:
        # Get current stock data for analysis
        stock_list = stock_manager.get_stock_list()
        alerts = stock_manager.get_stock_alerts()
        
        # Get real sales analytics from SalesTracker
        sales_analytics = stock_manager.sales_tracker.get_sales_analytics(period)
        
        # Get low stock alerts (real data from stock)
        low_stock_alerts = []
        for alert in alerts:
            if alert["alert_type"] in ["low_stock", "out_of_stock"]:
                low_stock_alerts.append({
                    "name": alert["material_name"],
                    "current": alert["current_stock"],
                    "min": alert["min_stock"],
                    "unit": alert.get("unit", "")
                })
        
        # Combine real sales analytics with real stock alerts
        return {
            "totalSales": sales_analytics["totalSales"],
            "topProducts": sales_analytics["topProducts"],
            "lowStockAlerts": low_stock_alerts,
            "dailyTrends": sales_analytics["dailyTrends"],
            "categoryBreakdown": sales_analytics["categoryBreakdown"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

@app.get("/api/recommendations")
async def get_recommendations():
    """Get stock recommendations based on current levels"""
    try:
        alerts = stock_manager.get_stock_alerts()
        recommendations = []
        
        for alert in alerts:
            if alert["alert_type"] == "out_of_stock":
                recommendations.append({
                    "id": f"rec_{len(recommendations) + 1}",
                    "type": "stock",
                    "title": f"Urgent Restock: {alert['material_name']}",
                    "description": f"Urgent: {alert['material_name']} is out of stock and needs immediate restocking",
                    "impact": "high",
                    "implementation": f"Order {alert['material_name']} immediately from suppliers",
                    "expectedResult": "Prevent business disruption and maintain customer satisfaction",
                    "priority": 1
                })
            elif alert["alert_type"] == "low_stock":
                recommendations.append({
                    "id": f"rec_{len(recommendations) + 1}",
                    "type": "stock",
                    "title": f"Low Stock Alert: {alert['material_name']}",
                    "description": f"Low stock alert: {alert['material_name']} is below minimum level ({alert['current_stock']} {alert.get('unit', 'units')} remaining)",
                    "impact": "medium",
                    "implementation": f"Plan restocking for {alert['material_name']} within the next few days",
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
        alerts = stock_manager.get_stock_alerts()
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "low_stock_count": len([a for a in alerts if a["alert_type"] == "low_stock"]),
            "out_of_stock_count": len([a for a in alerts if a["alert_type"] == "out_of_stock"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")

@app.get("/api/summary")
async def get_summary():
    """Get stock summary statistics"""
    try:
        summary = stock_manager.get_stock_summary()
        return summary
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
        sales_tracker = stock_manager.sales_tracker
        return {
            "total_sales_records": sales_tracker.get_total_sales_count(),
            "sales_data": sales_tracker.sales_data,
            "sample_analytics": sales_tracker.get_sales_analytics("7d")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sales debug info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# backend/main.py sonuna ekleyin
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)