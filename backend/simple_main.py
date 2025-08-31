from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

app = FastAPI(
    title="Woden AI Stock API - Simple Version",
    description="Simple API for testing frontend connection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for testing
MOCK_STOCK_DATA = {
    "stock_data": {
        "coffee": {
            "ESPRESSO": {
                "name": "ESPRESSO",
                "category": "coffee",
                "current_stock": 50,
                "min_stock_level": 10,
                "unit": "shots",
                "package_size": 1,
                "package_unit": "shot"
            },
            "AMERICANO": {
                "name": "AMERICANO",
                "category": "coffee",
                "current_stock": 30,
                "min_stock_level": 15,
                "unit": "cups",
                "package_size": 1,
                "package_unit": "cup"
            }
        },
        "ingredients": {
            "TORKU SÜT": {
                "name": "TORKU SÜT",
                "category": "ingredients",
                "current_stock": 20,
                "min_stock_level": 5,
                "unit": "liters",
                "package_size": 1,
                "package_unit": "liter"
            }
        }
    }
}

MOCK_ANALYSIS_DATA = {
    "totalSales": 150,
    "topProducts": [
        {"name": "ESPRESSO", "quantity": 45, "percentage": 30.0},
        {"name": "AMERICANO", "quantity": 35, "percentage": 23.3},
        {"name": "LATTE", "quantity": 30, "percentage": 20.0}
    ],
    "lowStockAlerts": [
        {"name": "TORKU SÜT", "current": 20, "min": 5, "unit": "liters"}
    ],
    "dailyTrends": [
        {"date": "2025-08-30", "totalSales": 25, "products": 8},
        {"date": "2025-08-29", "totalSales": 30, "products": 10},
        {"date": "2025-08-28", "totalSales": 28, "products": 9}
    ],
    "categoryBreakdown": [
        {"category": "coffee", "count": 110, "percentage": 73.3},
        {"category": "tea", "count": 25, "percentage": 16.7},
        {"category": "pastry", "count": 15, "percentage": 10.0}
    ]
}

MOCK_RECOMMENDATIONS = {
    "recommendations": [
        {
            "id": "1",
            "type": "campaign",
            "title": "Summer Coffee Promotion",
            "description": "Launch a summer-themed campaign focusing on iced coffee products",
            "impact": "high",
            "implementation": "Create social media content and offer discounts",
            "expectedResult": "Expected 25-30% increase in iced coffee sales",
            "priority": 1
        }
    ]
}

MOCK_CAMPAIGNS = {
    "campaigns": [
        {
            "id": "1",
            "name": "Iced Coffee Summer Blitz",
            "description": "Promote iced coffee products with refreshing summer themes",
            "targetProducts": ["ICED AMERICANO", "ICED FILTER COFFEE"],
            "duration": "3 months (June-August)",
            "expectedIncrease": "30% in cold beverage sales",
            "cost": "Low - mainly social media promotion",
            "status": "suggested"
        }
    ]
}

@app.get("/")
async def root():
    return {"message": "Welcome to Woden AI Stock API - Simple Version"}

@app.get("/api")
async def api_info():
    return {
        "name": "Woden AI Stock API - Simple Version",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/stock")
async def get_stock():
    return MOCK_STOCK_DATA

@app.get("/api/analysis")
async def get_analysis(period: str = "7d"):
    return MOCK_ANALYSIS_DATA

@app.get("/api/recommendations")
async def get_recommendations():
    return MOCK_RECOMMENDATIONS

@app.get("/api/campaigns")
async def get_campaigns():
    return MOCK_CAMPAIGNS

@app.post("/api/sales/upload")
async def upload_sales():
    return {
        "message": "Sales data uploaded successfully",
        "sales_processed": 25,
        "stock_updated": True
    }

@app.post("/api/stock/update")
async def update_stock():
    return {"message": "Stock updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
