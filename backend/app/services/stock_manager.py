from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from app.models import (
    Product, Ingredient, Recipe, RecipeIngredient, 
    Sale, SaleItem, StockTransaction, DailyConsumable
)
from app.schemas import SaleItemCreate
import logging

logger = logging.getLogger(__name__)

class StockManager:
    def __init__(self, db: Session):
        self.db = db

    def process_sale_and_update_stock(self, sale_data: Dict, sale_id: int) -> Tuple[bool, List[str]]:
        """
        Process a sale and update stock levels accordingly.
        Returns (success, list of errors/warnings)
        """
        errors = []
        warnings = []
        
        try:
            # Process each sale item
            for item_data in sale_data.get('items', []):
                success, item_errors, item_warnings = self._process_sale_item(
                    item_data, sale_id
                )
                if not success:
                    errors.extend(item_errors)
                warnings.extend(item_warnings)
            
            # Process daily consumables
            daily_errors, daily_warnings = self._process_daily_consumables()
            errors.extend(daily_errors)
            warnings.extend(daily_warnings)
            
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            logger.error(f"Error processing sale and updating stock: {str(e)}")
            return False, [f"System error: {str(e)}"], warnings

    def _process_sale_item(self, item_data: Dict, sale_id: int) -> Tuple[bool, List[str], List[str]]:
        """
        Process a single sale item and update stock accordingly.
        """
        errors = []
        warnings = []
        
        try:
            # Find the product by SKU
            product = self.db.query(Product).filter(
                Product.sku == item_data['product_sku'],
                Product.is_active == True
            ).first()
            
            if not product:
                errors.append(f"Product with SKU {item_data['product_sku']} not found")
                return False, errors, warnings
            
            quantity = item_data['quantity']
            
            # Check if we have enough stock
            if product.current_stock < quantity:
                warnings.append(f"Insufficient stock for {product.name} (SKU: {product.sku}). "
                             f"Requested: {quantity}, Available: {product.current_stock}")
                # Continue processing but mark as warning
            
            # Update product stock
            previous_stock = product.current_stock
            product.current_stock = max(0, product.current_stock - quantity)
            
            # Record stock transaction
            self._record_stock_transaction(
                entity_type='product',
                entity_id=product.id,
                transaction_type='sale',
                quantity=-quantity,
                previous_stock=previous_stock,
                new_stock=product.current_stock,
                reference_id=sale_id,
                reference_type='sale'
            )
            
            # Handle different product types
            if product.product_type == 'recipe_based':
                success, recipe_errors, recipe_warnings = self._process_recipe_based_sale(
                    product, quantity
                )
                if not success:
                    errors.extend(recipe_errors)
                warnings.extend(recipe_warnings)
            
            elif product.product_type == 'ready_made':
                # Stock already updated above
                pass
            
            elif product.product_type == 'consumable':
                # Stock already updated above
                pass
            
            self.db.commit()
            return True, errors, warnings
            
        except Exception as e:
            logger.error(f"Error processing sale item: {str(e)}")
            self.db.rollback()
            return False, [f"Error processing item: {str(e)}"], warnings

    def _process_recipe_based_sale(self, product: Product, quantity: int) -> Tuple[bool, List[str], List[str]]:
        """
        Process stock updates for recipe-based products.
        Decreases ingredient stock based on recipe requirements.
        """
        errors = []
        warnings = []
        
        try:
            # Get the recipe for this product
            recipe = self.db.query(Recipe).filter(
                Recipe.product_id == product.id,
                Recipe.is_active == True
            ).first()
            
            if not recipe:
                errors.append(f"No recipe found for product {product.name}")
                return False, errors, warnings
            
            # Process each ingredient
            for recipe_ingredient in recipe.ingredients:
                ingredient = recipe_ingredient.ingredient
                
                # Calculate required quantity based on recipe yield
                required_qty = (recipe_ingredient.quantity * quantity) / recipe.yield_quantity
                
                # Check if we have enough ingredient stock
                if ingredient.current_stock < required_qty:
                    warnings.append(f"Insufficient ingredient stock for {ingredient.name} "
                                 f"(SKU: {ingredient.sku}). Required: {required_qty:.2f}, "
                                 f"Available: {ingredient.current_stock}")
                
                # Update ingredient stock
                previous_stock = ingredient.current_stock
                ingredient.current_stock = max(0, ingredient.current_stock - required_qty)
                
                # Record stock transaction
                self._record_stock_transaction(
                    entity_type='ingredient',
                    entity_id=ingredient.id,
                    transaction_type='recipe_consumption',
                    quantity=-required_qty,
                    previous_stock=previous_stock,
                    new_stock=ingredient.current_stock,
                    reference_id=product.id,
                    reference_type='recipe_consumption'
                )
            
            return True, errors, warnings
            
        except Exception as e:
            logger.error(f"Error processing recipe-based sale: {str(e)}")
            return False, [f"Error processing recipe: {str(e)}"], warnings

    def _process_daily_consumables(self) -> Tuple[List[str], List[str]]:
        """
        Process daily consumption for consumable items.
        Decreases stock based on daily consumption rates.
        """
        errors = []
        warnings = []
        
        try:
            daily_consumables = self.db.query(DailyConsumable).filter(
                DailyConsumable.is_active == True
            ).all()
            
            for consumable in daily_consumables:
                if consumable.daily_consumption > 0:
                    previous_stock = consumable.current_stock
                    consumable.current_stock = max(0, consumable.current_stock - consumable.daily_consumption)
                    
                    # Record stock transaction
                    self._record_stock_transaction(
                        entity_type='daily_consumable',
                        entity_id=consumable.id,
                        transaction_type='daily_consumption',
                        quantity=-consumable.daily_consumption,
                        previous_stock=previous_stock,
                        new_stock=consumable.current_stock,
                        reference_type='daily_consumption'
                    )
                    
                    # Check if stock is low
                    if consumable.current_stock <= consumable.min_stock_level:
                        warnings.append(f"Low stock alert: {consumable.name} (SKU: {consumable.sku}) "
                                     f"has {consumable.current_stock} {consumable.unit} remaining")
            
            return errors, warnings
            
        except Exception as e:
            logger.error(f"Error processing daily consumables: {str(e)}")
            return [f"Error processing daily consumables: {str(e)}"], warnings

    def _record_stock_transaction(self, entity_type: str, entity_id: int, 
                                transaction_type: str, quantity: int, 
                                previous_stock: int, new_stock: int,
                                reference_id: int = None, reference_type: str = None,
                                notes: str = None):
        """
        Record a stock transaction for audit purposes.
        """
        try:
            transaction = StockTransaction(
                entity_type=entity_type,
                entity_id=entity_id,
                transaction_type=transaction_type,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                reference_id=reference_id,
                reference_type=reference_type,
                notes=notes
            )
            
            self.db.add(transaction)
            
        except Exception as e:
            logger.error(f"Error recording stock transaction: {str(e)}")

    def get_stock_summary(self) -> Dict:
        """
        Get a summary of all stock levels with low stock alerts.
        """
        try:
            products = self.db.query(Product).filter(Product.is_active == True).all()
            ingredients = self.db.query(Ingredient).filter(Ingredient.is_active == True).all()
            daily_consumables = self.db.query(DailyConsumable).filter(DailyConsumable.is_active == True).all()
            
            low_stock_alerts = []
            
            # Check products
            for product in products:
                if product.current_stock <= product.min_stock_level:
                    low_stock_alerts.append(f"Product: {product.name} (SKU: {product.sku}) - "
                                          f"Stock: {product.current_stock}")
            
            # Check ingredients
            for ingredient in ingredients:
                if ingredient.current_stock <= ingredient.min_stock_level:
                    low_stock_alerts.append(f"Ingredient: {ingredient.name} (SKU: {ingredient.sku}) - "
                                          f"Stock: {ingredient.current_stock} {ingredient.unit}")
            
            # Check daily consumables
            for consumable in daily_consumables:
                if consumable.current_stock <= consumable.min_stock_level:
                    low_stock_alerts.append(f"Daily Consumable: {consumable.name} (SKU: {consumable.sku}) - "
                                          f"Stock: {consumable.current_stock} {consumable.unit}")
            
            return {
                'products': products,
                'ingredients': ingredients,
                'daily_consumables': daily_consumables,
                'low_stock_alerts': low_stock_alerts
            }
            
        except Exception as e:
            logger.error(f"Error getting stock summary: {str(e)}")
            return {
                'products': [],
                'ingredients': [],
                'daily_consumables': [],
                'low_stock_alerts': [f"Error retrieving stock data: {str(e)}"]
            }
