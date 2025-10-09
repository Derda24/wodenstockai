import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class ExcelProcessor:
    def __init__(self):
        # Updated for Adisyo Excel format
        self.required_columns = ['product_name', 'quantity']
        self.optional_columns = ['customer_name', 'invoice_number', 'payment_method', 'notes', 'sale_date']

    def process_excel_file(self, file_content: bytes, filename: str) -> Tuple[bool, Dict, List[str]]:
        """
        Process an Adisyo Excel file containing daily sales data.
        Returns (success, sale_data, errors)
        """
        try:
            # Read the Excel file from the "data" sheet
            df = self._read_excel_file(file_content, filename)
            if df is None:
                return False, {}, ["Failed to read Excel file"]

            # Validate the data
            validation_result = self._validate_excel_data(df)
            if not validation_result['is_valid']:
                return False, {}, validation_result['errors']

            # Convert to sale data format
            sale_data = self._convert_to_sale_data(df)
            
            return True, sale_data, []

        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            return False, {}, [f"Error processing Excel file: {str(e)}"]

    def _read_excel_file(self, file_content: bytes, filename: str) -> Optional[pd.DataFrame]:
        """
        Read Excel file content from the "data" sheet or first available sheet and return a pandas DataFrame.
        """
        try:
            # Determine the engine based on file extension
            if filename.endswith('.xlsx'):
                engine = 'openpyxl'
            elif filename.endswith('.xls'):
                engine = 'xlrd'
            else:
                logger.error(f"Unsupported file format: {filename}")
                return None
            
            # Try to read from different sheet names in order of preference
            sheet_names_to_try = ["data", "Data", "DATA", "Page 1", 0]  # 0 means first sheet
            df = None
            last_error = None
            
            for sheet_name in sheet_names_to_try:
                try:
                    df = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name, engine=engine)
                    logger.info(f"Successfully read Excel file from sheet: {sheet_name}")
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if df is None:
                logger.error(f"Error reading Excel file - tried sheets {sheet_names_to_try}. Last error: {last_error}")
                return None

            # Clean the DataFrame
            df = self._clean_dataframe(df)
            return df

        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            return None

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare the DataFrame for processing, specifically for Adisyo format.
        """
        try:
            # Remove empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Strip whitespace from string columns
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()
            
            # Handle Adisyo specific column mapping
            column_mapping = {
                # Turkish column names to English
                'Ürün Adı': 'product_name',
                'ürün adı': 'product_name',
                'Urun Adi': 'product_name',
                'urun adi': 'product_name',
                'Miktar': 'quantity',
                'miktar': 'quantity',
                'Adet': 'quantity',
                'adet': 'quantity',
                # Keep existing mappings for backward compatibility
                'sku': 'product_sku',
                'product_sku': 'product_sku',
                'product_code': 'product_sku',
                'qty': 'quantity',
                'quantity': 'quantity',
                'amount': 'unit_price',
                'price': 'unit_price',
                'unit_price': 'unit_price',
                'customer': 'customer_name',
                'client': 'customer_name',
                'invoice': 'invoice_number',
                'invoice_no': 'invoice_number',
                'payment': 'payment_method',
                'method': 'payment_method',
                'date': 'sale_date',
                'sale_date': 'sale_date',
                'transaction_date': 'sale_date'
            }
            
            # Rename columns based on mapping
            df = df.rename(columns=column_mapping)
            
            return df

        except Exception as e:
            logger.error(f"Error cleaning DataFrame: {str(e)}")
            return df

    def _validate_excel_data(self, df: pd.DataFrame) -> Dict:
        """
        Validate the Excel data for Adisyo format.
        Returns validation result with is_valid flag and errors list.
        """
        errors = []
        
        # Check if required columns exist
        missing_columns = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return {'is_valid': False, 'errors': errors}
        
        # Check for empty data
        if df.empty:
            errors.append("Excel file contains no data")
            return {'is_valid': False, 'errors': errors}
        
        # Validate each row
        for idx, row in df.iterrows():
            product_name = row.get('product_name', '')
            quantity = row.get('quantity', 0)
            
            # Check product name
            if not product_name or pd.isna(product_name):
                errors.append(f"Row {idx + 1}: Missing product name")
                continue
            
            # Check quantity
            if pd.isna(quantity) or quantity <= 0:
                errors.append(f"Row {idx + 1}: Invalid quantity for {product_name}")
                continue
            
            # Ensure quantity is a whole number
            try:
                qty = float(quantity)
                if qty != int(qty):
                    errors.append(f"Row {idx + 1}: Quantity must be a whole number for {product_name}")
                    continue
            except (ValueError, TypeError):
                errors.append(f"Row {idx + 1}: Invalid quantity format for {product_name}")
                continue
        
        # Note: We don't check for duplicates anymore since Adisyo format has different sizes/variants
        # for the same product (SMALL, MEDIUM, etc.)
        
        if errors:
            return {'is_valid': False, 'errors': errors}
        
        return {'is_valid': True, 'errors': []}

    def _convert_to_sale_data(self, df: pd.DataFrame) -> Dict:
        """
        Convert the validated DataFrame to sale data format for Adisyo exports.
        """
        try:
            # For Adisyo format, we focus on product_name and quantity
            sale_data = {
                'sale_date': self._get_sale_date(df),
                'invoice_number': self._get_invoice_number(df),
                'customer_name': self._get_customer_name(df),
                'payment_method': self._get_payment_method(df),
                'notes': self._get_notes(df),
                'items': []
            }

            # Process each row as a sale item
            for _, row in df.iterrows():
                item = {
                    'product_name': str(row['product_name']).strip(),
                    'quantity': int(float(row['quantity'])),  # Ensure integer conversion
                }
                
                # Add optional fields if they exist
                if 'unit_price' in df.columns:
                    item['unit_price'] = float(row['unit_price'])
                if 'notes' in df.columns:
                    item['notes'] = str(row.get('notes', '')).strip()
                
                sale_data['items'].append(item)

            return sale_data

        except Exception as e:
            logger.error(f"Error converting to sale data: {str(e)}")
            raise

    def _get_sale_date(self, df: pd.DataFrame) -> datetime:
        """
        Extract sale date from the DataFrame or use current date.
        """
        try:
            if 'sale_date' in df.columns:
                # Try to parse the first non-null date
                for date_val in df['sale_date'].dropna():
                    if pd.notna(date_val):
                        if isinstance(date_val, str):
                            # Try different date formats
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                                try:
                                    return datetime.strptime(str(date_val), fmt)
                                except ValueError:
                                    continue
                        elif pd.notna(date_val):
                            # Handle pandas datetime
                            return pd.to_datetime(date_val).to_pydatetime()
            
            # Default to current date if no valid date found
            return datetime.now()
            
        except Exception as e:
            logger.warning(f"Could not parse sale date, using current date: {str(e)}")
            return datetime.now()

    def _get_invoice_number(self, df: pd.DataFrame) -> Optional[str]:
        """
        Extract invoice number from the DataFrame.
        """
        if 'invoice_number' in df.columns:
            invoice_numbers = df['invoice_number'].dropna().unique()
            if len(invoice_numbers) == 1:
                return str(invoice_numbers[0]).strip()
        return None

    def _get_customer_name(self, df: pd.DataFrame) -> Optional[str]:
        """
        Extract customer name from the DataFrame.
        """
        if 'customer_name' in df.columns:
            customer_names = df['customer_name'].dropna().unique()
            if len(customer_names) == 1:
                return str(customer_names[0]).strip()
        return None

    def _get_payment_method(self, df: pd.DataFrame) -> Optional[str]:
        """
        Extract payment method from the DataFrame.
        """
        if 'payment_method' in df.columns:
            payment_methods = df['payment_method'].dropna().unique()
            if len(payment_methods) == 1:
                return str(payment_methods[0]).strip()
        return None

    def _get_notes(self, df: pd.DataFrame) -> Optional[str]:
        """
        Extract notes from the DataFrame.
        """
        if 'notes' in df.columns:
            notes = df['notes'].dropna().unique()
            if len(notes) == 1:
                return str(notes[0]).strip()
        return None

    def get_sample_excel_format(self) -> Dict:
        """
        Return a sample Excel format for Adisyo exports.
        """
        return {
            'description': 'Sample Excel format for Adisyo daily sales upload',
            'required_columns': self.required_columns,
            'optional_columns': self.optional_columns,
            'adisyo_format': {
                'sheet_name': 'data',
                'columns': {
                    'Ürün Adı': 'Product Name (required)',
                    'Miktar': 'Quantity (required, must be integer)'
                }
            },
            'sample_data': [
                {
                    'product_name': 'ICE WHITE MOCHA',
                    'quantity': 120,
                    'unit_price': 25.00,
                    'customer_name': 'Daily Sales',
                    'invoice_number': 'ADISYO001',
                    'payment_method': 'Cash',
                    'notes': 'Daily sales from Adisyo',
                    'sale_date': '2024-01-15'
                },
                {
                    'product_name': 'AMERICANO',
                    'quantity': 85,
                    'unit_price': 20.00,
                    'customer_name': 'Daily Sales',
                    'invoice_number': 'ADISYO001',
                    'payment_method': 'Cash',
                    'notes': 'Daily sales from Adisyo',
                    'sale_date': '2024-01-15'
                }
            ]
        }
