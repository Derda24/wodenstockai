from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.services.stock_manager import StockManager
from app.schemas import StockSummary

router = APIRouter()

@router.get("/stock/summary", response_model=StockSummary)
async def get_stock_summary(db: Session = Depends(get_db)):
    """
    Get a comprehensive summary of all stock levels with low stock alerts.
    """
    try:
        stock_manager = StockManager(db)
        summary = stock_manager.get_stock_summary()
        
        return StockSummary(
            products=summary['products'],
            ingredients=summary['ingredients'],
            daily_consumables=summary['daily_consumables'],
            low_stock_alerts=summary['low_stock_alerts']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stock summary: {str(e)}"
        )

@router.get("/stock/low-stock-alerts")
async def get_low_stock_alerts(db: Session = Depends(get_db)):
    """
    Get only the low stock alerts for products, ingredients, and daily consumables.
    """
    try:
        stock_manager = StockManager(db)
        summary = stock_manager.get_stock_summary()
        
        return {
            "low_stock_alerts": summary['low_stock_alerts'],
            "total_alerts": len(summary['low_stock_alerts'])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving low stock alerts: {str(e)}"
        )

@router.get("/stock/products")
async def get_products_stock(db: Session = Depends(get_db)):
    """
    Get stock information for all products.
    """
    try:
        stock_manager = StockManager(db)
        summary = stock_manager.get_stock_summary()
        
        products_data = []
        for product in summary['products']:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'product_type': product.product_type,
                'current_stock': product.current_stock,
                'min_stock_level': product.min_stock_level,
                'unit_price': product.unit_price,
                'category': product.category,
                'is_low_stock': product.current_stock <= product.min_stock_level,
                'stock_status': 'Low Stock' if product.current_stock <= product.min_stock_level else 'OK'
            })
        
        return {
            "products": products_data,
            "total_products": len(products_data),
            "low_stock_count": len([p for p in products_data if p['is_low_stock']])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving products stock: {str(e)}"
        )

@router.get("/stock/ingredients")
async def get_ingredients_stock(db: Session = Depends(get_db)):
    """
    Get stock information for all ingredients.
    """
    try:
        stock_manager = StockManager(db)
        summary = stock_manager.get_stock_summary()
        
        ingredients_data = []
        for ingredient in summary['ingredients']:
            ingredients_data.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'sku': ingredient.sku,
                'current_stock': ingredient.current_stock,
                'min_stock_level': ingredient.min_stock_level,
                'unit': ingredient.unit,
                'unit_cost': ingredient.unit_cost,
                'category': ingredient.category,
                'is_low_stock': ingredient.current_stock <= ingredient.min_stock_level,
                'stock_status': 'Low Stock' if ingredient.current_stock <= ingredient.min_stock_level else 'OK',
                'total_value': ingredient.current_stock * ingredient.unit_cost
            })
        
        return {
            "ingredients": ingredients_data,
            "total_ingredients": len(ingredients_data),
            "low_stock_count": len([i for i in ingredients_data if i['is_low_stock']]),
            "total_inventory_value": sum([i['total_value'] for i in ingredients_data])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving ingredients stock: {str(e)}"
        )

@router.get("/stock/daily-consumables")
async def get_daily_consumables_stock(db: Session = Depends(get_db)):
    """
    Get stock information for all daily consumables.
    """
    try:
        stock_manager = StockManager(db)
        summary = stock_manager.get_stock_summary()
        
        consumables_data = []
        for consumable in summary['daily_consumables']:
            consumables_data.append({
                'id': consumable.id,
                'name': consumable.name,
                'sku': consumable.sku,
                'current_stock': consumable.current_stock,
                'min_stock_level': consumable.min_stock_level,
                'daily_consumption': consumable.daily_consumption,
                'unit': consumable.unit,
                'unit_cost': consumable.unit_cost,
                'category': consumable.category,
                'is_low_stock': consumable.current_stock <= consumable.min_stock_level,
                'stock_status': 'Low Stock' if consumable.current_stock <= consumable.min_stock_level else 'OK',
                'days_remaining': consumable.current_stock / consumable.daily_consumption if consumable.daily_consumption > 0 else float('inf'),
                'total_value': consumable.current_stock * consumable.unit_cost
            })
        
        return {
            "daily_consumables": consumables_data,
            "total_consumables": len(consumables_data),
            "low_stock_count": len([c for c in consumables_data if c['is_low_stock']]),
            "total_inventory_value": sum([c['total_value'] for c in consumables_data])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving daily consumables stock: {str(e)}"
        )

@router.get("/stock/overview")
async def get_stock_overview(db: Session = Depends(get_db)):
    """
    Get a high-level overview of stock status.
    """
    try:
        stock_manager = StockManager(db)
        summary = stock_manager.get_stock_summary()
        
        # Calculate totals
        total_products = len(summary['products'])
        total_ingredients = len(summary['ingredients'])
        total_consumables = len(summary['daily_consumables'])
        
        # Calculate low stock counts
        low_stock_products = len([p for p in summary['products'] if p.current_stock <= p.min_stock_level])
        low_stock_ingredients = len([i for i in summary['ingredients'] if i.current_stock <= i.min_stock_level])
        low_stock_consumables = len([c for c in summary['daily_consumables'] if c.current_stock <= c.min_stock_level])
        
        # Calculate inventory values
        total_product_value = sum([p.current_stock * p.unit_price for p in summary['products']])
        total_ingredient_value = sum([i.current_stock * i.unit_cost for i in summary['ingredients']])
        total_consumable_value = sum([c.current_stock * c.unit_cost for c in summary['daily_consumables']])
        
        return {
            "summary": {
                "total_items": total_products + total_ingredients + total_consumables,
                "total_products": total_products,
                "total_ingredients": total_ingredients,
                "total_consumables": total_consumables
            },
            "low_stock": {
                "total_low_stock": low_stock_products + low_stock_ingredients + low_stock_consumables,
                "low_stock_products": low_stock_products,
                "low_stock_ingredients": low_stock_ingredients,
                "low_stock_consumables": low_stock_consumables
            },
            "inventory_value": {
                "total_value": total_product_value + total_ingredient_value + total_consumable_value,
                "products_value": total_product_value,
                "ingredients_value": total_ingredient_value,
                "consumables_value": total_consumable_value
            },
            "stock_status": {
                "products_ok": total_products - low_stock_products,
                "ingredients_ok": total_ingredients - low_stock_ingredients,
                "consumables_ok": total_consumables - low_stock_consumables
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stock overview: {str(e)}"
        )
