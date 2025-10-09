"""
Database models for the application.
This file re-exports models from database.py for backwards compatibility.
"""

from app.database import (
    Base,
    StockItem,
    StockTransaction,
    ManualUpdate,
    DailyUsageConfig,
    Recipe,
    SalesHistory
)

# Placeholder models for Adisyo format (not fully implemented yet)
# These are imported by sales.py but the Adisyo format is not currently used
# The DARA format uses Supabase directly and doesn't require these models

class Sale:
    """Placeholder for Sale model - not implemented"""
    pass

class SaleItem:
    """Placeholder for SaleItem model - not implemented"""
    pass

class Product:
    """Placeholder for Product model - not implemented"""
    pass

class Ingredient:
    """Placeholder for Ingredient model - not implemented"""
    pass

class RecipeIngredient:
    """Placeholder for RecipeIngredient model - not implemented"""
    pass

class Stock:
    """Alias for StockItem"""
    pass

__all__ = [
    'Base',
    'StockItem',
    'StockTransaction',
    'ManualUpdate',
    'DailyUsageConfig',
    'Recipe',
    'SalesHistory',
    'Sale',
    'SaleItem',
    'Product',
    'Ingredient',
    'RecipeIngredient',
    'Stock'
]

