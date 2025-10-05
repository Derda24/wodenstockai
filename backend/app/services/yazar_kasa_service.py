"""
YAZAR KASA LİNK Entegrasyon Servisi
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class YazarKasaService:
    def __init__(self):
        self.api_key = os.getenv('YAZAR_KASA_API_KEY')
        self.serial_number = os.getenv('YAZAR_KASA_SERIAL_NUMBER')
        self.base_url = os.getenv('YAZAR_KASA_BASE_URL', 'http://192.168.1.187:4568')
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Serial-Number": self.serial_number
        }
        
        print(f"YAZAR KASA LİNK Service initialized")
        print(f"  Base URL: {self.base_url}")
        print(f"  Serial Number: {self.serial_number}")
        print(f"  API Key: {self.api_key[:10] if self.api_key else 'None'}...")
    
    def test_connection(self) -> Dict[str, Any]:
        """API bağlantısını test et"""
        try:
            # Basit bir test endpoint'i dene
            test_endpoints = [
                f"{self.base_url}/api/health",
                f"{self.base_url}/api/status",
                f"{self.base_url}/api/info",
                f"{self.base_url}/"
            ]
            
            for endpoint in test_endpoints:
                try:
                    response = requests.get(endpoint, headers=self.headers, timeout=5, verify=False)
                    if response.status_code == 200:
                        return {
                            "success": True,
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "response": response.text[:200]
                        }
                except Exception as e:
                    continue
            
            return {
                "success": False,
                "error": "No working endpoint found",
                "tested_endpoints": test_endpoints
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_sale_transaction(self, sale_data: Dict[str, Any]) -> Dict[str, Any]:
        """Satış işlemini YAZAR KASA LİNK'e gönder"""
        try:
            # API endpoint'lerini dene
            endpoints = [
                f"{self.base_url}/api/sale",
                f"{self.base_url}/api/transaction",
                f"{self.base_url}/api/send",
                f"{self.base_url}/sale"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.post(endpoint, json=sale_data, headers=self.headers, timeout=10, verify=False)
                    
                    if response.status_code in [200, 201]:
                        return {
                            "success": True,
                            "endpoint": endpoint,
                            "data": response.json() if response.content else {}
                        }
                    else:
                        print(f"Endpoint {endpoint} failed with status {response.status_code}")
                        
                except Exception as e:
                    print(f"Endpoint {endpoint} error: {str(e)[:50]}")
                    continue
            
            return {
                "success": False,
                "error": "No working endpoint found for sending sales"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_sales_data(self, date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """Belirli tarih aralığındaki satış verilerini al"""
        try:
            if not date_from:
                date_from = datetime.now().strftime("%Y-%m-%d")
            if not date_to:
                date_to = datetime.now().strftime("%Y-%m-%d")
            
            # API endpoint'lerini dene
            endpoints = [
                f"{self.base_url}/api/sales",
                f"{self.base_url}/api/transactions",
                f"{self.base_url}/api/reports",
                f"{self.base_url}/sales"
            ]
            
            params = {
                "date_from": date_from,
                "date_to": date_to,
                "serial_number": self.serial_number
            }
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=self.headers, params=params, timeout=10, verify=False)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict) and "data" in data:
                            return data["data"]
                        elif isinstance(data, list):
                            return data
                        else:
                            return [data]
                            
                except Exception as e:
                    print(f"Endpoint {endpoint} error: {str(e)[:50]}")
                    continue
            
            return []
            
        except Exception as e:
            print(f"Satış verisi alma hatası: {str(e)}")
            return []
    
    def extract_sales_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """API verisinden satış bilgilerini çıkar"""
        try:
            transaction = api_data.get("TransactionHandle", {})
            sale = api_data.get("Sale", {})
            
            extracted_data = {
                "transaction_id": f"{transaction.get('SerialNumber', '')}_{transaction.get('TransactionSequence', 0)}",
                "transaction_date": transaction.get("TransactionDate", ""),
                "order_no": sale.get("OrderNo", ""),
                "total_amount": sale.get("TotalPrice", 0.0),
                "currency": sale.get("CurrencyCode", "TRY"),
                "customer": {
                    "name": f"{sale.get('CustomerParty', {}).get('FirstName', '')} {sale.get('CustomerParty', {}).get('FamilyName', '')}".strip(),
                    "phone": sale.get('CustomerParty', {}).get('Phone', ''),
                    "email": sale.get('CustomerParty', {}).get('EMail', ''),
                    "address": sale.get('CustomerParty', {}).get('Address', '')
                },
                "items": [],
                "payments": []
            }
            
            # Satış kalemlerini çıkar
            for item in sale.get("AddedSaleItems", []):
                item_data = {
                    "product_name": item.get("Name", ""),
                    "quantity": item.get("ItemQuantity", 0.0),
                    "unit_price": item.get("UnitPriceAmount", 0.0),
                    "total_price": item.get("TotalPriceAmount", 0.0),
                    "tax_code": item.get("TaxGroupCode", ""),
                    "unit_code": item.get("UnitCode", "")
                }
                extracted_data["items"].append(item_data)
            
            # Ödeme bilgilerini çıkar
            for payment in sale.get("PaymentInformations", []):
                payment_data = {
                    "mediator": payment.get("Mediator", 0),
                    "amount": payment.get("Amount", 0.0),
                    "currency": payment.get("CurrencyCode", "TRY")
                }
                extracted_data["payments"].append(payment_data)
            
            return extracted_data
            
        except Exception as e:
            print(f"Veri çıkarma hatası: {str(e)}")
            return {}
    
    def convert_to_our_format(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Bizim sistem formatına dönüştür"""
        try:
            # Tarih formatını dönüştür
            transaction_date = extracted_data.get("transaction_date", "")
            if transaction_date:
                # ISO formatından tarih çıkar
                date_part = transaction_date.split("T")[0]
            else:
                date_part = datetime.now().strftime("%Y-%m-%d")
            
            our_format = {
                "date": date_part,
                "total_quantity": sum(item.get("quantity", 0) for item in extracted_data.get("items", [])),
                "total_sales": extracted_data.get("total_amount", 0.0),
                "items_sold": json.dumps([
                    {
                        "product": item.get("product_name", ""),
                        "quantity": item.get("quantity", 0.0),
                        "unit_price": item.get("unit_price", 0.0),
                        "total_price": item.get("total_price", 0.0)
                    }
                    for item in extracted_data.get("items", [])
                ], ensure_ascii=False),
                "customer_info": json.dumps(extracted_data.get("customer", {}), ensure_ascii=False),
                "payment_info": json.dumps(extracted_data.get("payments", []), ensure_ascii=False),
                "transaction_id": extracted_data.get("transaction_id", ""),
                "order_no": extracted_data.get("order_no", ""),
                "learning_data": json.dumps({"source": "yazar_kasa_link", "sync_date": datetime.now().isoformat()}, ensure_ascii=False)
            }
            
            return our_format
            
        except Exception as e:
            print(f"Format dönüştürme hatası: {str(e)}")
            return {}
    
    def sync_to_supabase(self, supabase_service, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """YAZAR KASA LİNK verilerini Supabase'e senkronize et"""
        try:
            if not date_from:
                date_from = datetime.now().strftime("%Y-%m-%d")
            if not date_to:
                date_to = datetime.now().strftime("%Y-%m-%d")
            
            print(f"YAZAR KASA LİNK senkronizasyon başlıyor: {date_from} - {date_to}")
            
            # YAZAR KASA LİNK'den veri al
            sales_data = self.get_sales_data(date_from, date_to)
            
            if not sales_data:
                print("YAZAR KASA LİNK'den veri alınamadı")
                return {"success": False, "error": "No data received from YAZAR KASA LİNK"}
            
            synced_count = 0
            errors = []
            
            for sale in sales_data:
                try:
                    # Bizim formata dönüştür
                    extracted = self.extract_sales_data(sale)
                    our_format = self.convert_to_our_format(extracted)
                    
                    if our_format:
                        # Supabase'e kaydet
                        result = supabase_service.client.table("sales_history").insert(our_format).execute()
                        
                        if result.data:
                            synced_count += 1
                            print(f"Satış kaydedildi: {our_format.get('transaction_id')}")
                        else:
                            errors.append(f"Insert failed for {our_format.get('transaction_id')}")
                    
                except Exception as e:
                    error_msg = f"Error processing sale: {str(e)}"
                    errors.append(error_msg)
                    print(error_msg)
            
            result = {
                "success": synced_count > 0,
                "synced_count": synced_count,
                "total_received": len(sales_data),
                "errors": errors
            }
            
            print(f"Senkronizasyon tamamlandı: {synced_count}/{len(sales_data)} kayıt başarılı")
            return result
            
        except Exception as e:
            error_msg = f"Senkronizasyon hatası: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    
    def create_sample_transaction(self) -> Dict[str, Any]:
        """Örnek satış işlemi oluştur"""
        return {
            "TransactionHandle": {
                "SerialNumber": self.serial_number,
                "TransactionDate": datetime.now().isoformat(),
                "TransactionSequence": 1,
                "Fingerprint": "WODEN_AI"
            },
            "Sale": {
                "OrderNo": f"WODEN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "MainDocumentType": 1,
                "GrossPrice": 25.0,
                "TotalPrice": 25.0,
                "CurrencyCode": "TRY",
                "ExchangeRate": 1,
                "PriceEffect": {"Type": 2, "Rate": 0.0, "Amount": 0.0},
                "AddedSaleItems": [
                    {
                        "Name": "Test Ürün",
                        "IsGeneric": False,
                        "UnitCode": "ADT",
                        "TaxGroupCode": "KDV18",
                        "ItemQuantity": 1.0,
                        "UnitPriceAmount": 25.0,
                        "GrossPriceAmount": 25.0,
                        "TotalPriceAmount": 25.0,
                        "PriceEffect": {"Type": 1, "Rate": 0.0, "Amount": 0.0}
                    }
                ],
                "PaymentInformations": [
                    {"Mediator": 1, "Amount": 25.0, "CurrencyCode": "TRY", "ExchangeRate": 1}
                ],
                "AllowedPaymentMediators": [{"Mediator": 1}],
                "ReceiptInformation": {
                    "ReceiptImageEnabled": False,
                    "ReceiptWidth": "58mm",
                    "PrintCustomerReceipt": True,
                    "PrintMerchantReceipt": True
                },
                "CustomerParty": {
                    "CustomerType": 1,
                    "FirstName": "Test",
                    "FamilyName": "Müşteri"
                }
            }
        }
