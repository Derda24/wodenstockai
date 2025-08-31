from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Base Stock Schema (keeping existing for backward compatibility)
class StockBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    current_price: float = Field(..., gt=0, description="Current stock price")
    previous_close: Optional[float] = Field(None, ge=0, description="Previous closing price")
    change: Optional[float] = Field(None, description="Price change from previous close")
    change_percent: Optional[float] = Field(None, description="Percentage change from previous close")
    market_cap: Optional[float] = Field(None, ge=0, description="Market capitalization")
    volume: Optional[int] = Field(None, ge=0, description="Trading volume")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    dividend_yield: Optional[float] = Field(None, ge=0, description="Dividend yield percentage")
    sector: Optional[str] = Field(None, max_length=100, description="Company sector")
    industry: Optional[str] = Field(None, max_length=100, description="Company industry")
    description: Optional[str] = Field(None, description="Company description")

# Create Stock Schema
class StockCreate(StockBase):
    pass

# Update Stock Schema
class StockUpdate(BaseModel):
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    current_price: Optional[float] = Field(None, gt=0)
    previous_close: Optional[float] = Field(None, ge=0)
    change: Optional[float] = None
    change_percent: Optional[float] = None
    market_cap: Optional[float] = Field(None, ge=0)
    volume: Optional[int] = Field(None, ge=0)
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = Field(None, ge=0)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

# Stock Response Schema
class Stock(StockBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Stock List Response Schema
class StockList(BaseModel):
    stocks: list[Stock]
    total: int
    page: int
    size: int

# Health Check Schema
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    database: str
    version: str

# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=50)
    product_type: str = Field(..., description="recipe_based, ready_made, or consumable")
    current_stock: int = Field(0, ge=0)
    min_stock_level: int = Field(0, ge=0)
    unit_price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    product_type: Optional[str] = None
    current_stock: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    unit_price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Ingredient Schemas
class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=50)
    current_stock: int = Field(0, ge=0)
    min_stock_level: int = Field(0, ge=0)
    unit: str = Field(..., max_length=50)
    unit_cost: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    current_stock: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    unit_cost: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class Ingredient(IngredientBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Recipe Schemas
class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=50)
    notes: Optional[str] = None

class RecipeIngredientCreate(RecipeIngredientBase):
    pass

class RecipeIngredient(RecipeIngredientBase):
    id: int
    ingredient_name: Optional[str] = None
    ingredient_sku: Optional[str] = None

    class Config:
        from_attributes = True

class RecipeBase(BaseModel):
    product_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    yield_quantity: int = Field(1, gt=0)
    yield_unit: str = Field(..., max_length=50)
    instructions: Optional[str] = None
    ingredients: List[RecipeIngredientCreate]

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    yield_quantity: Optional[int] = Field(None, gt=0)
    yield_unit: Optional[str] = Field(None, max_length=50)
    instructions: Optional[str] = None
    ingredients: Optional[List[RecipeIngredientCreate]] = None

class Recipe(RecipeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    ingredients: List[RecipeIngredient]

    class Config:
        from_attributes = True

# Sale Schemas
class SaleItemBase(BaseModel):
    product_sku: str = Field(..., description="Product SKU to identify the product")
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    notes: Optional[str] = None

class SaleItemCreate(SaleItemBase):
    pass

class SaleItem(SaleItemBase):
    id: int
    sale_id: int
    product_id: int
    total_price: float
    product_name: Optional[str] = None

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    sale_date: datetime
    invoice_number: Optional[str] = Field(None, max_length=100)
    customer_name: Optional[str] = Field(None, max_length=255)
    payment_method: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    items: List[SaleItemCreate]

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    total_amount: float
    created_at: datetime
    items: List[SaleItem]

    class Config:
        from_attributes = True

# Stock Transaction Schema
class StockTransaction(BaseModel):
    id: int
    transaction_date: datetime
    entity_type: str
    entity_id: int
    transaction_type: str
    quantity: int
    previous_stock: int
    new_stock: int
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# Daily Consumable Schemas
class DailyConsumableBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=50)
    daily_consumption: int = Field(0, ge=0)
    current_stock: int = Field(0, ge=0)
    min_stock_level: int = Field(0, ge=0)
    unit: str = Field(..., max_length=50)
    unit_cost: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class DailyConsumableCreate(DailyConsumableBase):
    pass

class DailyConsumableUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    daily_consumption: Optional[int] = Field(None, ge=0)
    current_stock: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    unit_cost: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class DailyConsumable(DailyConsumableBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Excel Upload Response Schema
class ExcelUploadResponse(BaseModel):
    message: str
    sales_processed: int
    stock_updated: bool
    errors: List[str] = []
    warnings: List[str] = []

# Stock Summary Schema
class StockSummary(BaseModel):
    products: List[Product]
    ingredients: List[Ingredient]
    daily_consumables: List[DailyConsumable]
    low_stock_alerts: List[str] = []
