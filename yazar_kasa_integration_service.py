
from datetime import datetime
import json
import requests
from typing import Dict, List, Any

class YazarKasaIntegrationService:
    def __init__(self, api_key: str, serial_number: str, base_url: str):
        self.api_key = api_key
        self.serial_number = serial_number
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-Serial-Number": serial_number
        }
    
    def send_sale_transaction(self, sale_data: Dict[str, Any]) -> Dict[str, Any]:
        """Satış işlemini YAZAR KASA LİNK'e gönder"""
        try:
            url = f"{self.base_url}/api/sale"
            response = requests.post(url, json=sale_data, headers=self.headers)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_sales_data(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """Belirli tarih aralığındaki satış verilerini al"""
        try:
            url = f"{self.base_url}/api/sales"
            params = {
                "date_from": date_from,
                "date_to": date_to,
                "serial_number": self.serial_number
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                return []
                
        except Exception as e:
            print(f"Satış verisi alma hatası: {str(e)}")
            return []
    
    def sync_to_supabase(self, supabase_service, date_from: str = None, date_to: str = None):
        """YAZAR KASA LİNK verilerini Supabase'e senkronize et"""
        if not date_from:
            date_from = datetime.now().strftime("%Y-%m-%d")
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        
        # YAZAR KASA LİNK'den veri al
        sales_data = self.get_sales_data(date_from, date_to)
        
        for sale in sales_data:
            # Bizim formata dönüştür
            analyzer = YazarKasaAPIAnalyzer()
            extracted = analyzer.extract_sales_data(sale)
            our_format = analyzer.convert_to_our_format(extracted)
            
            # Supabase'e kaydet
            try:
                supabase_service.client.table("sales_history").insert(our_format).execute()
                print(f"Satış kaydedildi: {our_format['transaction_id']}")
            except Exception as e:
                print(f"Supabase kayıt hatası: {str(e)}")
