"""
YAZAR KASA LİNK API Format Analizi ve Entegrasyon Sistemi
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class YazarKasaAPIAnalyzer:
    def __init__(self):
        self.api_format = {
            "TransactionHandle": {
                "SerialNumber": "PAV860027763",
                "TransactionDate": "2025-10-04T23:39:22.31077",
                "TransactionSequence": 31,
                "Fingerprint": "DARA"
            },
            "Sale": {
                "AdisyonName": None,
                "AdisyonTableName": None,
                "AdisyonStaffName": None,
                "AdisyonOpenTime": None,
                "RefererApp": "Harici Uygulama",
                "RefererAppVersion": "1",
                "OrderNo": "0000000000ABC0020",
                "MainDocumentType": 1,
                "GrossPrice": 20.0,
                "TotalPrice": 20.0,
                "CurrencyCode": "TRY",
                "ExchangeRate": 1,
                "PriceEffect": {"Type": 2, "Rate": 10.0, "Amount": 0.0},
                "SendPhoneNotification": False,
                "SendEMailNotification": False,
                "NotificationPhone": "",
                "DocumentNote": None,
                "Reserved03": "",
                "NotificationEMail": "",
                "ShowCreditCardMenu": False,
                "InstallmentCount": 0,
                "SelectedSlots": [],
                "AllowDismissCardRead": False,
                "CardReadTimeout": 60,
                "SkipAmountCash": False,
                "CancelPaymentLater": True,
                "AskCustomer": False,
                "SendResponseBeforePrint": False,
                "AddedSaleItems": [
                    {
                        "Name": "Gofret",
                        "IsGeneric": False,
                        "UnitCode": "KGM",
                        "TaxGroupCode": "KDV18",
                        "ItemQuantity": 1.0,
                        "UnitPriceAmount": 20.0,
                        "GrossPriceAmount": 20.0,
                        "TotalPriceAmount": 20.0,
                        "ReservedText": None,
                        "PriceEffect": {"Type": 1, "Rate": 10.0, "Amount": 0.0}
                    }
                ],
                "PaymentInformations": [
                    {"Mediator": 2, "Amount": 16.2, "CurrencyCode": "TRY", "ExchangeRate": 1}
                ],
                "AllowedPaymentMediators": [
                    {"Mediator": 1},
                    {"Mediator": 1}
                ],
                "ReceiptInformation": {
                    "ReceiptImageEnabled": False,
                    "ReceiptWidth": "58mm",
                    "PrintCustomerReceipt": True,
                    "PrintCustomerReceiptCopy": False,
                    "PrintMerchantReceipt": True,
                    "EnableExchangeRateField": False
                },
                "CustomerParty": {
                    "CustomerType": 1,
                    "FirstName": "Ahmet",
                    "MiddleName": "",
                    "FamilyName": "as",
                    "CompanyName": "",
                    "TaxOfficeCode": "",
                    "TaxNumber": "11111111111",
                    "Phone": "",
                    "EMail": "",
                    "Country": "istanbul",
                    "City": "pendik",
                    "District": "yeni şehir",
                    "Neighborhood": "",
                    "Address": ""
                },
                "AdditionalInfo": [
                    {"Key": "Test", "Value": "Test", "Print": True}
                ]
            }
        }
    
    def analyze_api_structure(self):
        """API yapısını analiz et"""
        print("YAZAR KASA LİNK API Format Analizi")
        print("=" * 50)
        
        analysis = {
            "transaction_info": {
                "serial_number": "Kasa seri numarası",
                "transaction_date": "İşlem tarihi ve saati",
                "transaction_sequence": "İşlem sıra numarası",
                "fingerprint": "Sistem parmak izi"
            },
            "sale_info": {
                "order_no": "Sipariş numarası",
                "gross_price": "Brüt fiyat",
                "total_price": "Toplam fiyat",
                "currency_code": "Para birimi",
                "main_document_type": "Belge tipi"
            },
            "sale_items": {
                "name": "Ürün adı",
                "quantity": "Miktar",
                "unit_price": "Birim fiyat",
                "total_price": "Toplam fiyat",
                "tax_group_code": "Vergi grubu kodu",
                "unit_code": "Birim kodu"
            },
            "payment_info": {
                "mediator": "Ödeme yöntemi (1=Nakit, 2=Kart)",
                "amount": "Ödeme tutarı",
                "currency_code": "Para birimi"
            },
            "customer_info": {
                "first_name": "Müşteri adı",
                "family_name": "Müşteri soyadı",
                "phone": "Telefon",
                "email": "E-posta",
                "address": "Adres bilgileri"
            }
        }
        
        print("API Yapısı:")
        for section, fields in analysis.items():
            print(f"\n{section.upper().replace('_', ' ')}:")
            for field, description in fields.items():
                print(f"  • {field}: {description}")
        
        return analysis
    
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
                "order_no": extracted_data.get("order_no", "")
            }
            
            return our_format
            
        except Exception as e:
            print(f"Format dönüştürme hatası: {str(e)}")
            return {}
    
    def create_integration_service(self):
        """Entegrasyon servisi oluştur"""
        service_code = '''
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
'''
        
        with open('yazar_kasa_integration_service.py', 'w', encoding='utf-8') as f:
            f.write(service_code)
        
        print("Entegrasyon servisi 'yazar_kasa_integration_service.py' dosyasına kaydedildi.")
    
    def test_with_sample_data(self):
        """Örnek veri ile test et"""
        print("\nÖrnek Veri ile Test")
        print("=" * 30)
        
        # Örnek veriyi çıkar
        extracted = self.extract_sales_data(self.api_format)
        our_format = self.convert_to_our_format(extracted)
        
        print("Çıkarılan Veriler:")
        print(f"  Tarih: {our_format.get('date')}")
        print(f"  Toplam Tutar: {our_format.get('total_sales')}")
        print(f"  Toplam Miktar: {our_format.get('total_quantity')}")
        print(f"  İşlem ID: {our_format.get('transaction_id')}")
        
        items = json.loads(our_format.get('items_sold', '[]'))
        print(f"  Ürünler:")
        for item in items:
            print(f"    - {item.get('product')}: {item.get('quantity')} x {item.get('unit_price')} = {item.get('total_price')}")
        
        return our_format

def main():
    analyzer = YazarKasaAPIAnalyzer()
    
    # API yapısını analiz et
    analyzer.analyze_api_structure()
    
    # Entegrasyon servisi oluştur
    analyzer.create_integration_service()
    
    # Örnek veri ile test et
    test_result = analyzer.test_with_sample_data()
    
    print(f"\n{'='*50}")
    print("SONUÇ:")
    print("✅ YAZAR KASA LİNK API formatı analiz edildi")
    print("✅ Entegrasyon servisi oluşturuldu")
    print("✅ Veri dönüştürme sistemi hazır")
    print("\nSONRAKI ADIMLAR:")
    print("1. YAZAR KASA LİNK API endpoint'ini bulun")
    print("2. API Key ve Serial Number ile test edin")
    print("3. Otomatik senkronizasyonu kurun")

if __name__ == "__main__":
    main()
