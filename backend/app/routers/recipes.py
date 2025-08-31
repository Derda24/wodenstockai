from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Recipe, RecipeIngredient, Product, Ingredient
from app.schemas import RecipeCreate, RecipeUpdate, Recipe as RecipeSchema

router = APIRouter()

@router.get("/recipes", response_model=List[RecipeSchema])
async def get_recipes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get list of recipes with optional filtering and pagination.
    """
    try:
        query = db.query(Recipe)
        
        if product_id is not None:
            query = query.filter(Recipe.product_id == product_id)
        if is_active is not None:
            query = query.filter(Recipe.is_active == is_active)
        
        recipes = query.offset(skip).limit(limit).all()
        return recipes
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recipes: {str(e)}"
        )

@router.get("/recipes/{recipe_id}", response_model=RecipeSchema)
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """
    Get a specific recipe by ID.
    """
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recipe: {str(e)}"
        )

@router.get("/recipes/product/{product_id}", response_model=RecipeSchema)
async def get_recipe_by_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get recipe for a specific product.
    """
    try:
        recipe = db.query(Recipe).filter(
            Recipe.product_id == product_id,
            Recipe.is_active == True
        ).first()
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found for this product")
        
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recipe: {str(e)}"
        )

@router.post("/recipes", response_model=RecipeSchema, status_code=201)
async def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    """
    Create a new recipe.
    """
    try:
        # Check if product exists
        product = db.query(Product).filter(
            Product.id == recipe.product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if product already has a recipe
        existing_recipe = db.query(Recipe).filter(
            Recipe.product_id == recipe.product_id,
            Recipe.is_active == True
        ).first()
        
        if existing_recipe:
            raise HTTPException(
                status_code=400, 
                detail="Product already has a recipe"
            )
        
        # Validate ingredients
        for ingredient_data in recipe.ingredients:
            ingredient = db.query(Ingredient).filter(
                Ingredient.id == ingredient_data.ingredient_id,
                Ingredient.is_active == True
            ).first()
            
            if not ingredient:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Ingredient with ID {ingredient_data.ingredient_id} not found"
                )
        
        # Create recipe
        db_recipe = Recipe(
            product_id=recipe.product_id,
            name=recipe.name,
            description=recipe.description,
            yield_quantity=recipe.yield_quantity,
            yield_unit=recipe.yield_unit,
            instructions=recipe.instructions
        )
        
        db.add(db_recipe)
        db.flush()  # Get the recipe ID
        
        # Create recipe ingredients
        for ingredient_data in recipe.ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe_id=db_recipe.id,
                ingredient_id=ingredient_data.ingredient_id,
                quantity=ingredient_data.quantity,
                unit=ingredient_data.unit,
                notes=ingredient_data.notes
            )
            db.add(recipe_ingredient)
        
        db.commit()
        db.refresh(db_recipe)
        
        return db_recipe
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating recipe: {str(e)}"
        )

@router.put("/recipes/{recipe_id}", response_model=RecipeSchema)
async def update_recipe(
    recipe_id: int, 
    recipe_update: RecipeUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing recipe.
    """
    try:
        db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        
        if not db_recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Update basic recipe fields
        update_data = recipe_update.dict(exclude_unset=True, exclude={'ingredients'})
        for field, value in update_data.items():
            setattr(db_recipe, field, value)
        
        # Update ingredients if provided
        if recipe_update.ingredients is not None:
            # Remove existing ingredients
            db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == recipe_id
            ).delete()
            
            # Add new ingredients
            for ingredient_data in recipe_update.ingredients:
                # Validate ingredient exists
                ingredient = db.query(Ingredient).filter(
                    Ingredient.id == ingredient_data.ingredient_id,
                    Ingredient.is_active == True
                ).first()
                
                if not ingredient:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Ingredient with ID {ingredient_data.ingredient_id} not found"
                    )
                
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe_id,
                    ingredient_id=ingredient_data.ingredient_id,
                    quantity=ingredient_data.quantity,
                    unit=ingredient_data.unit,
                    notes=ingredient_data.notes
                )
                db.add(recipe_ingredient)
        
        db.commit()
        db.refresh(db_recipe)
        
        return db_recipe
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating recipe: {str(e)}"
        )

@router.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a recipe (mark as inactive).
    """
    try:
        db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        
        if not db_recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        db_recipe.is_active = False
        db.commit()
        
        return {"message": "Recipe deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting recipe: {str(e)}"
        )

@router.get("/recipes/{recipe_id}/ingredients")
async def get_recipe_ingredients(recipe_id: int, db: Session = Depends(get_db)):
    """
    Get ingredients for a specific recipe.
    """
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        ingredients = []
        for recipe_ingredient in recipe.ingredients:
            ingredient = db.query(Ingredient).filter(
                Ingredient.id == recipe_ingredient.ingredient_id
            ).first()
            
            if ingredient:
                ingredients.append({
                    'id': recipe_ingredient.id,
                    'ingredient_id': ingredient.id,
                    'ingredient_name': ingredient.name,
                    'ingredient_sku': ingredient.sku,
                    'quantity': recipe_ingredient.quantity,
                    'unit': recipe_ingredient.unit,
                    'notes': recipe_ingredient.notes,
                    'current_stock': ingredient.current_stock,
                    'unit_cost': ingredient.unit_cost
                })
        
        return {
            'recipe_id': recipe_id,
            'recipe_name': recipe.name,
            'ingredients': ingredients
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recipe ingredients: {str(e)}"
        )
