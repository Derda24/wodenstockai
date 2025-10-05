"""
DARA Excel Dosyası Analiz Aracı
5.10.2025.xls dosyasını analiz eder ve formatını çıkarır
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any

def analyze_dara_excel(file_path: str = "5.10.2025.xls"):
    """DARA Excel dosyasını analiz et"""
    print("DARA Excel Dosyası Analizi")
    print("=" * 50)
    
    try:
        # Excel dosyasını oku
        print(f"Dosya okunuyor: {file_path}")
        
        # Farklı sheet'leri kontrol et
        excel_file = pd.ExcelFile(file_path)
        print(f"Sheet'ler: {excel_file.sheet_names}")
        
        analysis_results = {
            "file_name": file_path,
            "analysis_date": datetime.now().isoformat(),
            "sheets": {},
            "recommendations": []
        }
        
        # Her sheet'i analiz et
        for sheet_name in excel_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                sheet_analysis = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns),
                    "data_types": df.dtypes.to_dict(),
                    "sample_data": df.head(3).to_dict('records'),
                    "null_counts": df.isnull().sum().to_dict()
                }
                
                print(f"Satır sayısı: {sheet_analysis['row_count']}")
                print(f"Sütun sayısı: {sheet_analysis['column_count']}")
                print(f"Sütunlar: {sheet_analysis['columns']}")
                
                # Veri tiplerini göster
                print("Veri tipleri:")
                for col, dtype in sheet_analysis['data_types'].items():
                    print(f"  {col}: {dtype}")
                
                # Null değerleri göster
                print("Null değerler:")
                for col, null_count in sheet_analysis['null_counts'].items():
                    if null_count > 0:
                        print(f"  {col}: {null_count}")
                
                # İlk birkaç satırı göster
                print("Örnek veriler:")
                print(df.head(3).to_string())
                
                analysis_results["sheets"][sheet_name] = sheet_analysis
                
                # Satış verisi analizi
                if sheet_analysis['row_count'] > 0:
                    analyze_sales_data(df, sheet_name)
                
            except Exception as e:
                print(f"Sheet '{sheet_name}' analiz hatası: {str(e)}")
                analysis_results["sheets"][sheet_name] = {"error": str(e)}
        
        # Genel öneriler
        generate_recommendations(analysis_results)
        
        # Sonuçları kaydet
        with open('dara_excel_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n{'='*50}")
        print("ANALİZ TAMAMLANDI")
        print(f"Detaylı sonuçlar 'dara_excel_analysis.json' dosyasına kaydedildi")
        
        return analysis_results
        
    except Exception as e:
        print(f"Excel dosyası okuma hatası: {str(e)}")
        return None

def analyze_sales_data(df: pd.DataFrame, sheet_name: str):
    """Satış verilerini analiz et"""
    print(f"\n--- Satış Verisi Analizi: {sheet_name} ---")
    
    # Olası tarih sütunları
    date_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['tarih', 'date', 'gün', 'zaman', 'time']):
            date_columns.append(col)
    
    if date_columns:
        print(f"Tarih sütunları: {date_columns}")
        for date_col in date_columns:
            try:
                unique_dates = df[date_col].dropna().unique()
                print(f"  {date_col} - Benzersiz tarih sayısı: {len(unique_dates)}")
                if len(unique_dates) <= 5:
                    print(f"    Tarihler: {list(unique_dates)}")
            except:
                pass
    
    # Olası ürün sütunları
    product_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['ürün', 'product', 'mal', 'item', 'adı', 'name']):
            product_columns.append(col)
    
    if product_columns:
        print(f"Ürün sütunları: {product_columns}")
        for prod_col in product_columns:
            try:
                unique_products = df[prod_col].dropna().unique()
                print(f"  {prod_col} - Benzersiz ürün sayısı: {len(unique_products)}")
                if len(unique_products) <= 10:
                    print(f"    Ürünler: {list(unique_products)}")
            except:
                pass
    
    # Olası miktar sütunları
    quantity_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['miktar', 'quantity', 'adet', 'qty', 'sayı']):
            quantity_columns.append(col)
    
    if quantity_columns:
        print(f"Miktar sütunları: {quantity_columns}")
    
    # Olası fiyat sütunları
    price_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['fiyat', 'price', 'tutar', 'amount', 'ücret', 'bedel']):
            price_columns.append(col)
    
    if price_columns:
        print(f"Fiyat sütunları: {price_columns}")

def generate_recommendations(analysis_results: Dict[str, Any]):
    """Analiz sonuçlarına göre öneriler oluştur"""
    print(f"\n--- ÖNERİLER ---")
    
    recommendations = []
    
    for sheet_name, sheet_data in analysis_results["sheets"].items():
        if "error" in sheet_data:
            continue
            
        if sheet_data["row_count"] > 0:
            recommendations.append({
                "sheet": sheet_name,
                "recommendation": f"Bu sheet'te {sheet_data['row_count']} satır veri var",
                "action": "Otomatik işleme için uygun"
            })
            
            # Sütun analizi
            columns = sheet_data["columns"]
            has_date = any('tarih' in str(col).lower() or 'date' in str(col).lower() for col in columns)
            has_product = any('ürün' in str(col).lower() or 'product' in str(col).lower() for col in columns)
            has_quantity = any('miktar' in str(col).lower() or 'quantity' in str(col).lower() for col in columns)
            has_price = any('fiyat' in str(col).lower() or 'price' in str(col).lower() for col in columns)
            
            if has_date and has_product and has_quantity:
                recommendations.append({
                    "sheet": sheet_name,
                    "recommendation": "Satış verisi formatında görünüyor",
                    "action": "Supabase'e otomatik import için hazır"
                })
            else:
                missing = []
                if not has_date: missing.append("tarih")
                if not has_product: missing.append("ürün")
                if not has_quantity: missing.append("miktar")
                
                recommendations.append({
                    "sheet": sheet_name,
                    "recommendation": f"Eksik sütunlar: {', '.join(missing)}",
                    "action": "Sütun eşleştirme gerekebilir"
                })
    
    # Önerileri yazdır
    for rec in recommendations:
        print(f"• {rec['sheet']}: {rec['recommendation']}")
        print(f"  → {rec['action']}")
    
    analysis_results["recommendations"] = recommendations

def create_excel_processor():
    """DARA Excel dosyası için otomatik işleyici oluştur"""
    processor_code = '''
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any

class DaraExcelProcessor:
    def __init__(self, supabase_service):
        self.supabase = supabase_service
        
    def process_dara_excel(self, file_path: str) -> Dict[str, Any]:
        """DARA Excel dosyasını işle ve Supabase'e kaydet"""
        try:
            print(f"DARA Excel işleniyor: {file_path}")
            
            # Excel dosyasını oku
            df = pd.read_excel(file_path)
            
            # Veri temizleme ve dönüştürme
            processed_data = self.clean_and_convert_data(df)
            
            # Supabase'e kaydet
            result = self.save_to_supabase(processed_data)
            
            return {
                "success": True,
                "processed_count": len(processed_data),
                "saved_count": result.get("saved_count", 0),
                "errors": result.get("errors", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def clean_and_convert_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Excel verisini temizle ve bizim formata dönüştür"""
        processed_data = []
        
        # Sütun eşleştirme (analiz sonuçlarına göre güncellenecek)
        column_mapping = {
            "date": None,      # Tarih sütunu
            "product": None,   # Ürün sütunu
            "quantity": None,  # Miktar sütunu
            "price": None,     # Fiyat sütunu
            "total": None      # Toplam sütunu
        }
        
        # Sütunları otomatik tespit et
        for col in df.columns:
            col_lower = str(col).lower()
            
            if not column_mapping["date"] and ('tarih' in col_lower or 'date' in col_lower):
                column_mapping["date"] = col
            
            if not column_mapping["product"] and ('ürün' in col_lower or 'product' in col_lower or 'mal' in col_lower):
                column_mapping["product"] = col
            
            if not column_mapping["quantity"] and ('miktar' in col_lower or 'quantity' in col_lower or 'adet' in col_lower):
                column_mapping["quantity"] = col
            
            if not column_mapping["price"] and ('fiyat' in col_lower or 'price' in col_lower or 'birim' in col_lower):
                column_mapping["price"] = col
            
            if not column_mapping["total"] and ('toplam' in col_lower or 'total' in col_lower or 'tutar' in col_lower):
                column_mapping["total"] = col
        
        print(f"Sütun eşleştirme: {column_mapping}")
        
        # Her satırı işle
        for index, row in df.iterrows():
            try:
                # Tarih işleme
                date_value = None
                if column_mapping["date"]:
                    date_value = row[column_mapping["date"]]
                    if pd.notna(date_value):
                        if isinstance(date_value, str):
                            date_value = datetime.strptime(date_value, "%d.%m.%Y").strftime("%Y-%m-%d")
                        else:
                            date_value = date_value.strftime("%Y-%m-%d")
                    else:
                        date_value = datetime.now().strftime("%Y-%m-%d")
                else:
                    date_value = datetime.now().strftime("%Y-%m-%d")
                
                # Ürün işleme
                product_name = ""
                if column_mapping["product"]:
                    product_name = str(row[column_mapping["product"]]) if pd.notna(row[column_mapping["product"]]) else ""
                
                # Miktar işleme
                quantity = 0.0
                if column_mapping["quantity"]:
                    try:
                        quantity = float(row[column_mapping["quantity"]]) if pd.notna(row[column_mapping["quantity"]]) else 0.0
                    except:
                        quantity = 0.0
                
                # Fiyat işleme
                unit_price = 0.0
                if column_mapping["price"]:
                    try:
                        unit_price = float(row[column_mapping["price"]]) if pd.notna(row[column_mapping["price"]]) else 0.0
                    except:
                        unit_price = 0.0
                
                # Toplam hesaplama
                total_price = 0.0
                if column_mapping["total"]:
                    try:
                        total_price = float(row[column_mapping["total"]]) if pd.notna(row[column_mapping["total"]]) else 0.0
                    except:
                        total_price = quantity * unit_price
                else:
                    total_price = quantity * unit_price
                
                # Bizim formata dönüştür
                our_format = {
                    "date": date_value,
                    "total_quantity": quantity,
                    "total_sales": total_price,
                    "items_sold": json.dumps([{
                        "product": product_name,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "total_price": total_price
                    }], ensure_ascii=False),
                    "customer_info": json.dumps({}, ensure_ascii=False),
                    "payment_info": json.dumps([{
                        "method": "unknown",
                        "amount": total_price
                    }], ensure_ascii=False),
                    "transaction_id": f"DARA_EXCEL_{index}",
                    "order_no": f"EXCEL_{index}",
                    "learning_data": json.dumps({
                        "source": "dara_excel_import",
                        "import_date": datetime.now().isoformat(),
                        "original_row": row.to_dict()
                    }, ensure_ascii=False)
                }
                
                processed_data.append(our_format)
                
            except Exception as e:
                print(f"Satır {index} işleme hatası: {str(e)}")
                continue
        
        return processed_data
    
    def save_to_supabase(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """İşlenmiş veriyi Supabase'e kaydet"""
        saved_count = 0
        errors = []
        
        for data in processed_data:
            try:
                result = self.supabase.client.table("sales_history").insert(data).execute()
                
                if result.data:
                    saved_count += 1
                    print(f"DARA Excel verisi kaydedildi: {data['transaction_id']}")
                else:
                    errors.append(f"Insert failed for {data['transaction_id']}")
                    
            except Exception as e:
                error_msg = f"Error saving {data['transaction_id']}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        return {
            "saved_count": saved_count,
            "errors": errors
        }
'''
    
    with open('dara_excel_processor.py', 'w', encoding='utf-8') as f:
        f.write(processor_code)
    
    print(f"\nDARA Excel işleyici 'dara_excel_processor.py' dosyasına kaydedildi")

def main():
    # Excel dosyasını analiz et
    analysis = analyze_dara_excel("5.10.2025.xls")
    
    if analysis:
        # Excel işleyici oluştur
        create_excel_processor()
        
        print(f"\n{'='*50}")
        print("SONRAKI ADIMLAR:")
        print("1. Excel dosyası analiz edildi")
        print("2. Otomatik işleyici oluşturuldu")
        print("3. Sütun eşleştirme yapılacak")
        print("4. Otomatik import sistemi kurulacak")

if __name__ == "__main__":
    main()
