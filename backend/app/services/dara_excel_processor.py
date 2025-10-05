"""
DARA Excel Dosyası Otomatik İşleyici
5.10.2025.xls formatını analiz edip Supabase'e kaydeder
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class DaraExcelProcessor:
    def __init__(self, supabase_service):
        self.supabase = supabase_service
        self.date_from_file = None  # Dosya adından tarih çıkar
        
    def process_dara_excel(self, file_path: str) -> Dict[str, Any]:
        """DARA Excel dosyasını işle ve Supabase'e kaydet"""
        try:
            print(f"DARA Excel işleniyor: {file_path}")
            
            # Dosya adından tarih çıkar
            self.date_from_file = self.extract_date_from_filename(file_path)
            
            # Excel dosyasını oku
            df = pd.read_excel(file_path, header=None)
            
            # Satış verilerini bul ve işle
            sales_data = self.find_and_extract_sales_data(df)
            
            if sales_data.empty:
                return {
                    "success": False,
                    "error": "No sales data found in Excel file"
                }
            
            # Veri temizleme ve dönüştürme
            processed_data = self.clean_and_convert_data(sales_data)
            
            if not processed_data:
                return {
                    "success": False,
                    "error": "No data could be processed"
                }
            
            # Supabase'e kaydet
            result = self.save_to_supabase(processed_data)
            
            return {
                "success": True,
                "processed_count": len(processed_data),
                "saved_count": result.get("saved_count", 0),
                "errors": result.get("errors", []),
                "date": self.date_from_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_date_from_filename(self, file_path: str) -> str:
        """Dosya adından tarih çıkar (5.10.2025.xls -> 2025-10-05)"""
        try:
            import re
            import os
            filename = os.path.basename(file_path)  # Sadece dosya adını al
            
            # Tarih formatını bul (5.10.2025, 05.10.2025, vb.)
            date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', filename)
            
            if date_match:
                day, month, year = date_match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            else:
                return datetime.now().strftime("%Y-%m-%d")
                
        except Exception as e:
            print(f"Tarih çıkarma hatası: {str(e)}")
            return datetime.now().strftime("%Y-%m-%d")
    
    def find_and_extract_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Excel'deki satış verilerini bul ve çıkar"""
        try:
            # "AÇIKLAMA" başlığını bul
            header_row = None
            for i in range(len(df)):
                row_values = df.iloc[i].astype(str).tolist()
                if any('AÇIKLAMA' in val.upper() or 'ÜRÜN' in val.upper() for val in row_values):
                    header_row = i
                    break
            
            if header_row is None:
                print("AÇIKLAMA başlığı bulunamadı!")
                return pd.DataFrame()
            
            print(f"AÇIKLAMA başlığı bulundu: Satır {header_row}")
            
            # Başlık satırından sonraki verileri al
            sales_data = df.iloc[header_row+1:].copy()
            
            # Boş satırları temizle
            sales_data = sales_data.dropna(how='all')
            
            # Sadece ürün satırlarını al (ilk sütunda ürün adı olan satırlar)
            product_rows = []
            for i in range(len(sales_data)):
                first_col_value = sales_data.iloc[i, 0]
                if pd.notna(first_col_value) and str(first_col_value).strip() != "":
                    # Ürün adı kontrolü
                    product_name = str(first_col_value).strip()
                    if not product_name.isdigit() and len(product_name) > 2:
                        product_rows.append(i)
            
            if product_rows:
                # Ürün satırlarını al
                filtered_data = sales_data.iloc[product_rows].copy()
                print(f"Satış verisi satır sayısı: {len(filtered_data)}")
                return filtered_data
            else:
                print("Ürün satırı bulunamadı!")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Satış verisi çıkarma hatası: {str(e)}")
            return pd.DataFrame()
    
    def clean_and_convert_data(self, sales_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Excel verisini temizle ve bizim formata dönüştür"""
        processed_data = []
        
        print("Veri dönüştürme başlıyor...")
        
        # DARA Excel formatı analizi:
        # Sütun 0: Ürün adı (AÇIKLAMA)
        # Sütun 7: Miktar 
        # Sütun 11: Tutar (fiyat)
        
        total_quantity = 0
        total_amount = 0
        items = []
        
        for index, row in sales_data.iterrows():
            try:
                # Ürün adı (Sütun 0)
                product_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                
                if not product_name or len(product_name) < 2:
                    continue
                
                # Miktar (Sütun 7)
                quantity = 0.0
                if pd.notna(row.iloc[7]):
                    try:
                        quantity = float(row.iloc[7])
                    except:
                        quantity = 0.0
                
                # Tutar (Sütun 11)
                amount = 0.0
                if pd.notna(row.iloc[11]):
                    try:
                        amount = float(row.iloc[11])
                    except:
                        amount = 0.0
                
                # Birim fiyat hesapla
                unit_price = amount / quantity if quantity > 0 else 0.0
                
                # Veri toplama
                total_quantity += quantity
                total_amount += amount
                
                item_data = {
                    "product": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": amount
                }
                items.append(item_data)
                
                print(f"  {product_name}: {quantity} adet, {amount:.2f} TL")
                
            except Exception as e:
                print(f"Satır {index} işleme hatası: {str(e)}")
                continue
        
        if items:
            # Günlük toplam kaydı oluştur (mevcut sütunlarla uyumlu)
            daily_record = {
                "date": self.date_from_file,
                "total_sales": total_amount,
                "items_sold": json.dumps({
                    "total_quantity": total_quantity,
                    "items": items,
                    "transaction_id": f"DARA_EXCEL_{self.date_from_file.replace('-', '')}",
                    "order_no": f"DARA_{self.date_from_file.replace('-', '')}",
                    "source": "dara_excel_import",
                    "import_date": datetime.now().isoformat(),
                    "file_date": self.date_from_file,
                    "total_items": len(items),
                    "processing_method": "dara_excel_processor_v1"
                }, ensure_ascii=False)
            }
            
            processed_data.append(daily_record)
            
            print(f"Toplam: {total_quantity} adet, {total_amount:.2f} TL")
            print(f"İşlenen ürün sayısı: {len(items)}")
        
        return processed_data
    
    def save_to_supabase(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """İşlenmiş veriyi Supabase'e kaydet"""
        saved_count = 0
        errors = []
        
        for data in processed_data:
            try:
                # Önce aynı tarih ile kayıt var mı kontrol et
                items_data = json.loads(data["items_sold"])
                transaction_id = items_data.get("transaction_id", "")
                
                existing = self.supabase.client.table("sales_history").select("*").eq("date", data["date"]).execute()
                
                # Aynı transaction_id ile kayıt var mı kontrol et
                existing_with_same_id = False
                for existing_record in existing.data:
                    existing_items = json.loads(existing_record.get("items_sold", "{}"))
                    existing_transaction_id = existing_items.get("transaction_id", "")
                    if existing_transaction_id == transaction_id:
                        existing_with_same_id = True
                        break
                
                if existing_with_same_id:
                    print(f"Kayıt zaten mevcut: {transaction_id} - Güncelleniyor...")
                    # Mevcut kaydı güncelle
                    update_result = self.supabase.client.table("sales_history").update(data).eq("date", data["date"]).execute()
                    if update_result.data:
                        saved_count += 1
                        print(f"DARA Excel verisi güncellendi: {transaction_id}")
                    continue
                
                result = self.supabase.client.table("sales_history").insert(data).execute()
                
                if result.data:
                    saved_count += 1
                    print(f"DARA Excel verisi kaydedildi: {transaction_id}")
                else:
                    errors.append(f"Insert failed for {transaction_id}")
                    
            except Exception as e:
                error_msg = f"Error saving {transaction_id}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        return {
            "saved_count": saved_count,
            "errors": errors
        }
    
    def get_sales_summary(self, date: str = None) -> Dict[str, Any]:
        """Belirli bir tarih için satış özeti al"""
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Supabase'den o tarihteki DARA Excel verilerini al
            result = self.supabase.client.table("sales_history").select("*").eq("date", date).execute()
            
            if result.data:
                total_sales = sum(float(record.get("total_sales", 0)) for record in result.data)
                
                # items_sold'dan total_quantity çıkar
                total_quantity = 0
                for record in result.data:
                    items_sold = record.get("items_sold", "{}")
                    try:
                        items_data = json.loads(items_sold)
                        total_quantity += float(items_data.get("total_quantity", 0))
                    except:
                        pass
                
                return {
                    "date": date,
                    "total_sales": total_sales,
                    "total_quantity": total_quantity,
                    "record_count": len(result.data),
                    "source": "DARA Excel Import"
                }
            else:
                return {
                    "date": date,
                    "total_sales": 0,
                    "total_quantity": 0,
                    "record_count": 0,
                    "source": "DARA Excel Import"
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "date": date,
                "source": "DARA Excel Import"
            }

# Test fonksiyonu
def test_dara_excel_processor():
    """DARA Excel işleyiciyi test et"""
    try:
        from supabase_service import SupabaseService
        
        print("DARA Excel Processor Test")
        print("=" * 40)
        
        # Supabase servisini başlat
        supabase = SupabaseService()
        processor = DaraExcelProcessor(supabase)
        
        # Excel dosyasını işle
        result = processor.process_dara_excel("../5.10.2025.xls")
        
        print(f"\nİşlem Sonucu:")
        print(f"Başarılı: {result['success']}")
        
        if result['success']:
            print(f"İşlenen: {result['processed_count']}")
            print(f"Kaydedilen: {result['saved_count']}")
            print(f"Tarih: {result['date']}")
            
            if result['errors']:
                print(f"Hatalar: {len(result['errors'])}")
                for error in result['errors'][:3]:
                    print(f"  - {error}")
        else:
            print(f"Hata: {result['error']}")
        
        # Satış özeti al
        if result['success'] and result['date']:
            summary = processor.get_sales_summary(result['date'])
            print(f"\nSatış Özeti ({summary['date']}):")
            print(f"Toplam Satış: {summary['total_sales']:.2f} TL")
            print(f"Toplam Miktar: {summary['total_quantity']} adet")
            print(f"Kayıt Sayısı: {summary['record_count']}")
        
    except Exception as e:
        print(f"Test hatası: {str(e)}")

if __name__ == "__main__":
    test_dara_excel_processor()
