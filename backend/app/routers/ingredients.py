from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Ingredient
from app.schemas import IngredientCreate, IngredientUpdate, Ingredient as IngredientSchema

router = APIRouter()

@router.get("/ingredients", response_model=List[IngredientSchema])
async def get_ingredients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    low_stock: Optional[bool] = Query(None, description="Filter by low stock items"),
    db: Session = Depends(get_db)
):
    """
    Get list of ingredients with optional filtering and pagination.
    """
    try:
        query = db.query(Ingredient).filter(Ingredient.is_active == True)
        
        if category:
            query = query.filter(Ingredient.category.ilike(f"%{category}%"))
        if low_stock is not None:
            if low_stock:
                query = query.filter(Ingredient.current_stock <= Ingredient.min_stock_level)
            else:
                query = query.filter(Ingredient.current_stock > Ingredient.min_stock_level)
        
        ingredients = query.offset(skip).limit(limit).all()
        return ingredients
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving ingredients: {str(e)}"
        )

@router.get("/ingredients/{ingredient_id}", response_model=IngredientSchema)
async def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """
    Get a specific ingredient by ID.
    """
    try:
        ingredient = db.query(Ingredient).filter(
            Ingredient.id == ingredient_id, 
            Ingredient.is_active == True
        ).first()
        
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        return ingredient
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving ingredient: {str(e)}"
        )

@router.get("/ingredients/sku/{sku}", response_model=IngredientSchema)
async def get_ingredient_by_sku(sku: str, db: Session = Depends(get_db)):
    """
    Get a specific ingredient by SKU.
    """
    try:
        ingredient = db.query(Ingredient).filter(
            Ingredient.sku == sku.upper(), 
            Ingredient.is_active == True
        ).first()
        
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        return ingredient
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving ingredient: {str(e)}"
        )

@router.post("/ingredients", response_model=IngredientSchema, status_code=201)
async def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    """
    Create a new ingredient.
    """
    try:
        # Check if ingredient with same SKU already exists
        existing_ingredient = db.query(Ingredient).filter(Ingredient.sku == ingredient.sku.upper()).first()
        if existing_ingredient:
            raise HTTPException(
                status_code=400, 
                detail="Ingredient with this SKU already exists"
            )
        
        db_ingredient = Ingredient(**ingredient.dict())
        db_ingredient.sku = ingredient.sku.upper()  # Ensure uppercase SKU
        
        db.add(db_ingredient)
        db.commit()
        db.refresh(db_ingredient)
        
        return db_ingredient
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating ingredient: {str(e)}"
        )

@router.put("/ingredients/{ingredient_id}", response_model=IngredientSchema)
async def update_ingredient(
    ingredient_id: int, 
    ingredient_update: IngredientUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing ingredient.
    """
    try:
        db_ingredient = db.query(Ingredient).filter(
            Ingredient.id == ingredient_id, 
            Ingredient.is_active == True
        ).first()
        
        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        # Update only provided fields
        update_data = ingredient_update.dict(exclude_unset=True)
        if "sku" in update_data:
            update_data["sku"] = update_data["sku"].upper()
        
        for field, value in update_data.items():
            setattr(db_ingredient, field, value)
        
        db.commit()
        db.refresh(db_ingredient)
        
        return db_ingredient
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating ingredient: {str(e)}"
        )

@router.delete("/ingredients/{ingredient_id}")
async def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """
    Soft delete an ingredient (mark as inactive).
    """
    try:
        db_ingredient = db.query(Ingredient).filter(
            Ingredient.id == ingredient_id, 
            Ingredient.is_active == True
        ).first()
        
        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        db_ingredient.is_active = False
        db.commit()
        
        return {"message": "Ingredient deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting ingredient: {str(e)}"
        )

@router.post("/ingredients/{ingredient_id}/adjust-stock")
async def adjust_ingredient_stock(
    ingredient_id: int,
    adjustment: float = Query(..., description="Stock adjustment amount (positive for addition, negative for reduction)"),
    reason: str = Query(..., description="Reason for stock adjustment"),
    db: Session = Depends(get_db)
):
    """
    Adjust ingredient stock levels manually.
    """
    try:
        db_ingredient = db.query(Ingredient).filter(
            Ingredient.id == ingredient_id, 
            Ingredient.is_active == True
        ).first()
        
        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        previous_stock = db_ingredient.current_stock
        new_stock = max(0, db_ingredient.current_stock + adjustment)
        
        db_ingredient.current_stock = new_stock
        
        db.commit()
        
        return {
            "message": "Stock adjusted successfully",
            "ingredient_id": ingredient_id,
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

@router.post("/ingredients/{ingredient_id}/purchase")
async def record_ingredient_purchase(
    ingredient_id: int,
    quantity: float = Query(..., description="Quantity purchased"),
    unit_cost: Optional[float] = Query(None, description="Unit cost for this purchase"),
    supplier: Optional[str] = Query(None, description="Supplier name"),
    notes: Optional[str] = Query(None, description="Purchase notes"),
    db: Session = Depends(get_db)
):
    """
    Record an ingredient purchase and update stock levels.
    """
    try:
        db_ingredient = db.query(Ingredient).filter(
            Ingredient.id == ingredient_id, 
            Ingredient.is_active == True
        ).first()
        
        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Purchase quantity must be greater than 0")
        
        previous_stock = db_ingredient.current_stock
        new_stock = db_ingredient.current_stock + quantity
        
        # Update stock
        db_ingredient.current_stock = new_stock
        
        # Update unit cost if provided
        if unit_cost and unit_cost > 0:
            db_ingredient.unit_cost = unit_cost
        
        db.commit()
        
        return {
            "message": "Purchase recorded successfully",
            "ingredient_id": ingredient_id,
            "ingredient_name": db_ingredient.name,
            "quantity_purchased": quantity,
            "previous_stock": previous_stock,
            "new_stock": new_stock,
            "unit_cost": unit_cost or db_ingredient.unit_cost,
            "supplier": supplier,
            "notes": notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error recording purchase: {str(e)}"
        )
