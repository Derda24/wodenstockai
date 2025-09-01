from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Stock Items Table
class StockItem(Base):
    __tablename__ = "stock_items"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(String, unique=True, index=True, nullable=False)
    item_name = Column(String, nullable=False)
    category_name = Column(String, nullable=False)
    current_stock = Column(Float, nullable=False, default=0.0)
    min_stock = Column(Float, nullable=False, default=0.0)
    unit = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    transactions = relationship("StockTransaction", back_populates="stock_item")
    manual_updates = relationship("ManualUpdate", back_populates="stock_item")

# Stock Transactions Table (for audit trail)
class StockTransaction(Base):
    __tablename__ = "stock_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_item_id = Column(Integer, ForeignKey("stock_items.id"), nullable=False)
    transaction_type = Column(String, nullable=False)  # 'daily_consumption', 'manual_update', 'sales_upload'
    old_stock = Column(Float, nullable=False)
    new_stock = Column(Float, nullable=False)
    change_amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    stock_item = relationship("StockItem", back_populates="transactions")

# Manual Updates Table (for protection against daily consumption)
class ManualUpdate(Base):
    __tablename__ = "manual_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_item_id = Column(Integer, ForeignKey("stock_items.id"), nullable=False)
    old_stock = Column(Float, nullable=False)
    new_stock = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    manual_update_flag = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    stock_item = relationship("StockItem", back_populates="manual_updates")

# Daily Usage Configuration Table
class DailyUsageConfig(Base):
    __tablename__ = "daily_usage_config"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(String, unique=True, index=True, nullable=False)
    daily_amount = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Recipes Table
class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_name = Column(String, nullable=False)
    ingredients = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Sales History Table
class SalesHistory(Base):
    __tablename__ = "sales_history"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    total_sales = Column(Float, nullable=False, default=0.0)
    items_sold = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=func.now())

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Drop all tables (for development/testing)
def drop_tables():
    Base.metadata.drop_all(bind=engine)
