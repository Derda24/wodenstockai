from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Stock
from app.schemas import StockCreate, StockUpdate, Stock as StockSchema, StockList

router = APIRouter()

@router.get("/stocks", response_model=StockList)
async def get_stocks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    symbol: Optional[str] = Query(None, description="Filter by stock symbol"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db)
):
    """
    Get list of stocks with optional filtering and pagination
    """
    query = db.query(Stock).filter(Stock.is_active == True)
    
    if symbol:
        query = query.filter(Stock.symbol.ilike(f"%{symbol}%"))
    if sector:
        query = query.filter(Stock.sector.ilike(f"%{sector}%"))
    
    total = query.count()
    stocks = query.offset(skip).limit(limit).all()
    
    return StockList(
        stocks=stocks,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/stocks/{stock_id}", response_model=StockSchema)
async def get_stock(stock_id: int, db: Session = Depends(get_db)):
    """
    Get a specific stock by ID
    """
    stock = db.query(Stock).filter(Stock.id == stock_id, Stock.is_active == True).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.get("/stocks/symbol/{symbol}", response_model=StockSchema)
async def get_stock_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """
    Get a specific stock by symbol
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper(), Stock.is_active == True).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.post("/stocks", response_model=StockSchema, status_code=201)
async def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    """
    Create a new stock
    """
    # Check if stock with same symbol already exists
    existing_stock = db.query(Stock).filter(Stock.symbol == stock.symbol.upper()).first()
    if existing_stock:
        raise HTTPException(status_code=400, detail="Stock with this symbol already exists")
    
    db_stock = Stock(**stock.dict())
    db_stock.symbol = stock.symbol.upper()  # Ensure uppercase symbol
    
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.put("/stocks/{stock_id}", response_model=StockSchema)
async def update_stock(
    stock_id: int, 
    stock_update: StockUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing stock
    """
    db_stock = db.query(Stock).filter(Stock.id == stock_id, Stock.is_active == True).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Update only provided fields
    update_data = stock_update.dict(exclude_unset=True)
    if "symbol" in update_data:
        update_data["symbol"] = update_data["symbol"].upper()
    
    for field, value in update_data.items():
        setattr(db_stock, field, value)
    
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.delete("/stocks/{stock_id}")
async def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a stock (mark as inactive)
    """
    db_stock = db.query(Stock).filter(Stock.id == stock_id, Stock.is_active == True).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    db_stock.is_active = False
    db.commit()
    
    return {"message": "Stock deleted successfully"}
