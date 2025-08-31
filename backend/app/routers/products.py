from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate, Product as ProductSchema

router = APIRouter()

@router.get("/products", response_model=List[ProductSchema])
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    low_stock: Optional[bool] = Query(None, description="Filter by low stock items"),
    db: Session = Depends(get_db)
):
    """
    Get list of products with optional filtering and pagination.
    """
    try:
        query = db.query(Product).filter(Product.is_active == True)
        
        if product_type:
            query = query.filter(Product.product_type == product_type)
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        if low_stock is not None:
            if low_stock:
                query = query.filter(Product.current_stock <= Product.min_stock_level)
            else:
                query = query.filter(Product.current_stock > Product.min_stock_level)
        
        products = query.offset(skip).limit(limit).all()
        return products
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving products: {str(e)}"
        )

@router.get("/products/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    """
    try:
        product = db.query(Product).filter(
            Product.id == product_id, 
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving product: {str(e)}"
        )

@router.get("/products/sku/{sku}", response_model=ProductSchema)
async def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """
    Get a specific product by SKU.
    """
    try:
        product = db.query(Product).filter(
            Product.sku == sku.upper(), 
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving product: {str(e)}"
        )

@router.post("/products", response_model=ProductSchema, status_code=201)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    """
    try:
        # Check if product with same SKU already exists
        existing_product = db.query(Product).filter(Product.sku == product.sku.upper()).first()
        if existing_product:
            raise HTTPException(
                status_code=400, 
                detail="Product with this SKU already exists"
            )
        
        db_product = Product(**product.dict())
        db_product.sku = product.sku.upper()  # Ensure uppercase SKU
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        return db_product
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating product: {str(e)}"
        )

@router.put("/products/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing product.
    """
    try:
        db_product = db.query(Product).filter(
            Product.id == product_id, 
            Product.is_active == True
        ).first()
        
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update only provided fields
        update_data = product_update.dict(exclude_unset=True)
        if "sku" in update_data:
            update_data["sku"] = update_data["sku"].upper()
        
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        
        return db_product
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating product: {str(e)}"
        )

@router.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a product (mark as inactive).
    """
    try:
        db_product = db.query(Product).filter(
            Product.id == product_id, 
            Product.is_active == True
        ).first()
        
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        db_product.is_active = False
        db.commit()
        
        return {"message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting product: {str(e)}"
        )

@router.post("/products/{product_id}/adjust-stock")
async def adjust_product_stock(
    product_id: int,
    adjustment: int = Query(..., description="Stock adjustment amount (positive for addition, negative for reduction)"),
    reason: str = Query(..., description="Reason for stock adjustment"),
    db: Session = Depends(get_db)
):
    """
    Adjust product stock levels manually.
    """
    try:
        db_product = db.query(Product).filter(
            Product.id == product_id, 
            Product.is_active == True
        ).first()
        
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        previous_stock = db_product.current_stock
        new_stock = max(0, db_product.current_stock + adjustment)
        
        db_product.current_stock = new_stock
        
        db.commit()
        
        return {
            "message": "Stock adjusted successfully",
            "product_id": product_id,
            "previous_stock": previous_stock,
            "adjustment": adjustment,
            "new_stock": new_stock,
            "reason": reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error adjusting stock: {str(e)}"
        )
