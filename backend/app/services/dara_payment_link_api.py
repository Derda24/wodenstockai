"""
DARA Payment Link API Entegrasyon Sistemi
Fotoğraftaki "Payment Link Request Response" API'sini kullanarak entegrasyon
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class DaraPaymentLinkAPI:
    def __init__(self):
        self.api_key = os.getenv('YAZAR_KASA_API_KEY')
        self.serial_number = os.getenv('YAZAR_KASA_SERIAL_NUMBER')
        
        # DARA Payment Link API endpoints (fotoğraftaki hata mesajından çıkarılan)
        self.base_urls = [
            "https://api.dara.com.tr",  # Muhtemel DARA API URL
            "https://payment.dara.com.tr",
            "https://cloud.dara.com.tr",
            "https://api.yazarkasa.com",
            "https://payment.yazarkasa.com"
        ]
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Serial-Number": self.serial_number,
            "X-API-Key": self.api_key,
            "User-Agent": "WodenAI-Integration/1.0"
        }
        
        print(f"DARA Payment Link API initialized")
        print(f"  Serial Number: {self.serial_number}")
        print(f"  API Key: {self.api_key[:10] if self.api_key else 'None'}...")
    
    def test_payment_link_api(self) -> Dict[str, Any]:
        """Payment Link API'sini test et"""
        print("DARA Payment Link API Test")
        print("=" * 40)
        
        # Test endpoint'leri (fotoğraftaki "Payment Link Request Response" dan çıkarılan)
        test_endpoints = [
            "/api/payment-link",
            "/api/payment/request",
            "/api/transactions",
            "/api/sales",
            "/api/cloud-sync",
            "/api/data/sync",
            "/payment-link/request",
            "/payment/request",
            "/cloud/sync"
        ]
        
        successful_connections = []
        
        for base_url in self.base_urls:
            print(f"\nTesting base URL: {base_url}")
            
            for endpoint in test_endpoints:
                full_url = base_url + endpoint
                try:
                    # GET request test
                    response = requests.get(full_url, headers=self.headers, timeout=10, verify=False)
                    
                    print(f"  GET {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"    SUCCESS!")
                        successful_connections.append({
                            'url': full_url,
                            'method': 'GET',
                            'status': response.status_code,
                            'response': response.json() if response.content else {}
                        })
                    elif response.status_code == 401:
                        print(f"    AUTH REQUIRED (API Key doğru olabilir)")
                        # 401 alıyorsak API endpoint doğru ama auth eksik olabilir
                        successful_connections.append({
                            'url': full_url,
                            'method': 'GET',
                            'status': response.status_code,
                            'note': 'Authentication required'
                        })
                    elif response.status_code == 404:
                        print(f"    NOT FOUND")
                    else:
                        print(f"    Status: {response.status_code}")
                        
                except Exception as e:
                    print(f"  GET {endpoint}: ERROR - {str(e)[:50]}")
                
                # POST request test
                try:
                    test_data = {
                        "SerialNumber": self.serial_number,
                        "TransactionDate": datetime.now().isoformat(),
                        "TransactionSequence": 1,
                        "Fingerprint": "WODEN_AI"
                    }
                    
                    response = requests.post(full_url, json=test_data, headers=self.headers, timeout=10, verify=False)
                    
                    print(f"  POST {endpoint}: {response.status_code}")
                    
                    if response.status_code in [200, 201]:
                        print(f"    SUCCESS!")
                        successful_connections.append({
                            'url': full_url,
                            'method': 'POST',
                            'status': response.status_code,
                            'response': response.json() if response.content else {}
                        })
                    elif response.status_code == 401:
                        print(f"    AUTH REQUIRED")
                        successful_connections.append({
                            'url': full_url,
                            'method': 'POST',
                            'status': response.status_code,
                            'note': 'Authentication required'
                        })
                        
                except Exception as e:
                    print(f"  POST {endpoint}: ERROR - {str(e)[:50]}")
        
        return {
            "successful_connections": successful_connections,
            "total_tested": len(self.base_urls) * len(test_endpoints) * 2  # GET + POST
        }
    
    def send_payment_link_request(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Payment Link Request gönder (fotoğraftaki hata mesajından)"""
        print("Payment Link Request gönderiliyor...")
        
        # Fotoğraftaki JSON formatını kullan
        payment_request = {
            "TransactionHandle": {
                "SerialNumber": self.serial_number,
                "TransactionDate": transaction_data.get("TransactionDate", datetime.now().isoformat()),
                "TransactionSequence": transaction_data.get("TransactionSequence", 1),
                "Fingerprint": "WODEN_AI"
            },
            "Sale": transaction_data.get("Sale", {})
        }
        
        # API endpoint'lerini dene
        endpoints = [
            "/api/payment-link/request",
            "/api/payment/request", 
            "/payment-link/request",
            "/payment/request",
            "/api/transactions",
            "/api/sales"
        ]
        
        for base_url in self.base_urls:
            for endpoint in endpoints:
                full_url = base_url + endpoint
                try:
                    response = requests.post(
                        full_url, 
                        json=payment_request, 
                        headers=self.headers, 
                        timeout=10, 
                        verify=False
                    )
                    
                    print(f"Payment Link Request to {full_url}: {response.status_code}")
                    
                    if response.status_code == 200:
                        return {
                            "success": True,
                            "url": full_url,
                            "response": response.json() if response.content else {},
                            "status": response.status_code
                        }
                    elif response.status_code == 401:
                        print(f"  401 Unauthorized - API Key veya auth eksik")
                        return {
                            "success": False,
                            "url": full_url,
                            "error": "401 Unauthorized",
                            "note": "API Key veya authentication eksik",
                            "status": response.status_code,
                            "response": response.text
                        }
                    else:
                        print(f"  Status {response.status_code}: {response.text[:100]}")
                        
                except Exception as e:
                    print(f"  Error: {str(e)[:50]}")
                    continue
        
        return {
            "success": False,
            "error": "No working endpoint found for Payment Link Request"
        }
    
    def get_cloud_sync_data(self, date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """Cloud'dan senkronizasyon verilerini al"""
        try:
            if not date_from:
                date_from = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if not date_to:
                date_to = datetime.now().strftime("%Y-%m-%d")
            
            print(f"Cloud sync data alınıyor: {date_from} - {date_to}")
            
            # Cloud sync endpoint'lerini dene
            sync_endpoints = [
                "/api/cloud-sync",
                "/api/data/sync",
                "/api/transactions",
                "/api/sales",
                "/cloud/sync",
                "/data/sync"
            ]
            
            params = {
                "date_from": date_from,
                "date_to": date_to,
                "serial_number": self.serial_number
            }
            
            for base_url in self.base_urls:
                for endpoint in sync_endpoints:
                    full_url = base_url + endpoint
                    try:
                        response = requests.get(
                            full_url, 
                            headers=self.headers, 
                            params=params, 
                            timeout=10, 
                            verify=False
                        )
                        
                        print(f"Cloud sync {full_url}: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            if isinstance(data, dict) and "data" in data:
                                return data["data"]
                            elif isinstance(data, list):
                                return data
                            else:
                                return [data]
                        elif response.status_code == 401:
                            print(f"  401 Unauthorized - Auth eksik")
                            
                    except Exception as e:
                        print(f"  Error: {str(e)[:50]}")
                        continue
            
            return []
            
        except Exception as e:
            print(f"Cloud sync veri alma hatası: {str(e)}")
            return []
    
    def create_sample_transaction(self) -> Dict[str, Any]:
        """Örnek transaction oluştur (gönderilen JSON'a benzer)"""
        return {
            "TransactionHandle": {
                "SerialNumber": self.serial_number,
                "TransactionDate": datetime.now().isoformat(),
                "TransactionSequence": 1,
                "Fingerprint": "WODEN_AI"
            },
            "Sale": {
                "AdisyonName": None,
                "AdisyonTableName": None,
                "AdisyonStaffName": None,
                "AdisyonOpenTime": None,
                "RefererApp": "Woden AI Integration",
                "RefererAppVersion": "1.0",
                "OrderNo": f"WODEN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "MainDocumentType": 1,
                "GrossPrice": 25.0,
                "TotalPrice": 25.0,
                "CurrencyCode": "TRY",
                "ExchangeRate": 1,
                "PriceEffect": {"Type": 2, "Rate": 0.0, "Amount": 0.0},
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
                        "Name": "Test Ürün",
                        "IsGeneric": False,
                        "UnitCode": "ADT",
                        "TaxGroupCode": "KDV18",
                        "ItemQuantity": 1.0,
                        "UnitPriceAmount": 25.0,
                        "GrossPriceAmount": 25.0,
                        "TotalPriceAmount": 25.0,
                        "ReservedText": None,
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
                    "PrintCustomerReceiptCopy": False,
                    "PrintMerchantReceipt": True,
                    "EnableExchangeRateField": False
                },
                "CustomerParty": {
                    "CustomerType": 1,
                    "FirstName": "Test",
                    "MiddleName": "",
                    "FamilyName": "Müşteri",
                    "CompanyName": "",
                    "TaxOfficeCode": "",
                    "TaxNumber": "",
                    "Phone": "",
                    "EMail": "",
                    "Country": "",
                    "City": "",
                    "District": "",
                    "Neighborhood": "",
                    "Address": ""
                },
                "AdditionalInfo": [
                    {"Key": "Source", "Value": "WodenAI", "Print": True}
                ]
            }
        }
    
    def sync_to_supabase(self, supabase_service, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """DARA Payment Link API'den verileri Supabase'e senkronize et"""
        try:
            print(f"DARA Payment Link senkronizasyon başlıyor: {date_from or 'yesterday'} - {date_to or 'today'}")
            
            # Cloud'dan veri al
            cloud_data = self.get_cloud_sync_data(date_from, date_to)
            
            if not cloud_data:
                return {
                    "success": False,
                    "error": "No data received from DARA Payment Link API"
                }
            
            # Bizim formata dönüştür
            converted_data = self.convert_dara_data_to_our_format(cloud_data)
            
            if not converted_data:
                return {
                    "success": False,
                    "error": "No data could be converted"
                }
            
            # Supabase'e kaydet
            synced_count = 0
            errors = []
            
            for data in converted_data:
                try:
                    result = supabase_service.client.table("sales_history").insert(data).execute()
                    
                    if result.data:
                        synced_count += 1
                        print(f"DARA satış kaydedildi: {data.get('transaction_id')}")
                    else:
                        errors.append(f"Insert failed for {data.get('transaction_id')}")
                        
                except Exception as e:
                    error_msg = f"Error saving {data.get('transaction_id')}: {str(e)}"
                    errors.append(error_msg)
                    print(error_msg)
            
            result = {
                "success": synced_count > 0,
                "synced_count": synced_count,
                "total_received": len(converted_data),
                "errors": errors
            }
            
            print(f"DARA senkronizasyon tamamlandı: {synced_count}/{len(converted_data)} kayıt başarılı")
            return result
            
        except Exception as e:
            error_msg = f"DARA senkronizasyon hatası: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    
    def convert_dara_data_to_our_format(self, dara_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """DARA verisini bizim formata dönüştür"""
        converted_data = []
        
        for record in dara_data:
            try:
                # TransactionHandle'dan bilgileri çıkar
                transaction_handle = record.get("TransactionHandle", {})
                sale_data = record.get("Sale", {})
                
                # Tarih formatını dönüştür
                transaction_date = transaction_handle.get("TransactionDate", "")
                if transaction_date:
                    date_part = transaction_date.split("T")[0]
                else:
                    date_part = datetime.now().strftime("%Y-%m-%d")
                
                # Ürün bilgilerini çıkar
                items = []
                total_amount = sale_data.get("TotalPrice", 0.0)
                total_quantity = 0
                
                for item in sale_data.get("AddedSaleItems", []):
                    item_data = {
                        "product": item.get("Name", ""),
                        "quantity": item.get("ItemQuantity", 0.0),
                        "unit_price": item.get("UnitPriceAmount", 0.0),
                        "total_price": item.get("TotalPriceAmount", 0.0)
                    }
                    items.append(item_data)
                    total_quantity += item.get("ItemQuantity", 0.0)
                
                # Müşteri bilgilerini çıkar
                customer_party = sale_data.get("CustomerParty", {})
                customer_info = {
                    "name": f"{customer_party.get('FirstName', '')} {customer_party.get('FamilyName', '')}".strip(),
                    "phone": customer_party.get("Phone", ""),
                    "email": customer_party.get("EMail", ""),
                    "address": customer_party.get("Address", "")
                }
                
                # Ödeme bilgilerini çıkar
                payments = []
                for payment in sale_data.get("PaymentInformations", []):
                    payment_data = {
                        "mediator": payment.get("Mediator", 0),
                        "amount": payment.get("Amount", 0.0),
                        "currency": payment.get("CurrencyCode", "TRY")
                    }
                    payments.append(payment_data)
                
                our_format = {
                    "date": date_part,
                    "total_quantity": total_quantity,
                    "total_sales": total_amount,
                    "items_sold": json.dumps(items, ensure_ascii=False),
                    "customer_info": json.dumps(customer_info, ensure_ascii=False),
                    "payment_info": json.dumps(payments, ensure_ascii=False),
                    "transaction_id": f"{transaction_handle.get('SerialNumber', '')}_{transaction_handle.get('TransactionSequence', 0)}",
                    "order_no": sale_data.get("OrderNo", ""),
                    "learning_data": json.dumps({
                        "source": "dara_payment_link_api",
                        "sync_date": datetime.now().isoformat(),
                        "fingerprint": transaction_handle.get("Fingerprint", ""),
                        "original_data": record
                    }, ensure_ascii=False)
                }
                
                converted_data.append(our_format)
                
            except Exception as e:
                print(f"DARA veri dönüştürme hatası: {str(e)}")
                continue
        
        return converted_data
