from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models import Sale, SaleItem, Product
from app.schemas import SaleCreate, Sale as SaleSchema, ExcelUploadResponse
from app.services.excel_processor import ExcelProcessor
from app.services.stock_manager import StockManager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/sales/upload", response_model=ExcelUploadResponse)
async def upload_sales_excel(
    file: UploadFile = File(..., description="Excel file containing daily sales data"),
    db: Session = Depends(get_db)
):
    """
    Upload a daily sales Excel file and process it to update stock levels.
    
    The Excel file should contain the following columns:
    - product_sku (required): Product SKU identifier
    - quantity (required): Quantity sold
    - unit_price (required): Unit price of the product
    
    Optional columns:
    - customer_name: Name of the customer
    - invoice_number: Invoice number
    - payment_method: Payment method used
    - notes: Additional notes
    - sale_date: Date of the sale
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="File must be an Excel file (.xlsx or .xls)"
            )
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(
                status_code=400, 
                detail="File is empty"
            )
        
        # Process Excel file
        excel_processor = ExcelProcessor()
        success, sale_data, errors = excel_processor.process_excel_file(file_content, file.filename)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail=f"Error processing Excel file: {'; '.join(errors)}"
            )
        
        # Process sales and update stock
        stock_manager = StockManager(db)
        sales_processed = 0
        stock_updated = False
        warnings = []
        
        try:
            # Create sale record
            sale = Sale(
                sale_date=sale_data['sale_date'],
                invoice_number=sale_data.get('invoice_number'),
                customer_name=sale_data.get('customer_name'),
                payment_method=sale_data.get('payment_method'),
                notes=sale_data.get('notes'),
                total_amount=0  # Will be calculated
            )
            
            db.add(sale)
            db.flush()  # Get the sale ID
            
            # Process sale items and calculate total
            total_amount = 0
            for item_data in sale_data['items']:
                # Find product by SKU
                product = db.query(Product).filter(
                    Product.sku == item_data['product_sku'],
                    Product.is_active == True
                ).first()
                
                if not product:
                    warnings.append(f"Product with SKU {item_data['product_sku']} not found")
                    continue
                
                # Create sale item
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['quantity'] * item_data['unit_price'],
                    notes=item_data.get('notes')
                )
                
                db.add(sale_item)
                total_amount += sale_item.total_price
                sales_processed += 1
            
            # Update sale total amount
            sale.total_amount = total_amount
            
            # Process stock updates
            stock_success, stock_errors, stock_warnings = stock_manager.process_sale_and_update_stock(
                sale_data, sale.id
            )
            
            if stock_success:
                stock_updated = True
            else:
                warnings.extend(stock_errors)
            
            warnings.extend(stock_warnings)
            
            # Commit all changes
            db.commit()
            
            logger.info(f"Successfully processed {sales_processed} sales from Excel file")
            
            return ExcelUploadResponse(
                message=f"Successfully processed {sales_processed} sales from Excel file",
                sales_processed=sales_processed,
                stock_updated=stock_updated,
                errors=[],
                warnings=warnings
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing sales data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing sales data: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_sales_excel: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get("/sales", response_model=List[SaleSchema])
async def get_sales(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    customer_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of sales with optional filtering and pagination.
    """
    try:
        query = db.query(Sale)
        
        # Apply filters
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Sale.sale_date >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Sale.sale_date <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")
        
        if customer_name:
            query = query.filter(Sale.customer_name.ilike(f"%{customer_name}%"))
        
        # Apply pagination
        total = query.count()
        sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
        
        return sales
        
    except Exception as e:
        logger.error(f"Error retrieving sales: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sales: {str(e)}"
        )

@router.get("/sales/{sale_id}", response_model=SaleSchema)
async def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """
    Get a specific sale by ID.
    """
    try:
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        
        return sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving sale {sale_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sale: {str(e)}"
        )

@router.get("/sales/excel-format")
async def get_excel_format():
    """
    Get the required Excel format for sales uploads.
    """
    excel_processor = ExcelProcessor()
    return excel_processor.get_sample_excel_format()
