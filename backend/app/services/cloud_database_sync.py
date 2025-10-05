"""
Cloud Veritabanı Eşleştirme Sistemi
YAZAR KASA LİNK'in cloud veritabanı ile otomatik senkronizasyon
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import sqlite3
import pymysql
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class CloudDatabaseSync:
    def __init__(self, supabase_service):
        self.supabase = supabase_service
        self.sync_interval = int(os.getenv('YAZAR_KASA_SYNC_INTERVAL', 300))  # 5 dakika
        self.last_sync_time = None
        
        # Cloud veritabanı bağlantı bilgileri (DARA'dan alınacak)
        self.cloud_db_config = {
            "type": os.getenv('YAZAR_KASA_CLOUD_DB_TYPE', 'mysql'),  # mysql, postgresql, sqlite
            "host": os.getenv('YAZAR_KASA_CLOUD_DB_HOST', ''),
            "port": int(os.getenv('YAZAR_KASA_CLOUD_DB_PORT', 3306)),
            "database": os.getenv('YAZAR_KASA_CLOUD_DB_NAME', ''),
            "username": os.getenv('YAZAR_KASA_CLOUD_DB_USER', ''),
            "password": os.getenv('YAZAR_KASA_CLOUD_DB_PASSWORD', ''),
            "api_url": os.getenv('YAZAR_KASA_CLOUD_API_URL', ''),
            "api_key": os.getenv('YAZAR_KASA_API_KEY', '')
        }
        
        print(f"Cloud Database Sync initialized")
        print(f"  DB Type: {self.cloud_db_config['type']}")
        print(f"  Host: {self.cloud_db_config['host']}")
        print(f"  API URL: {self.cloud_db_config['api_url']}")
    
    def test_cloud_connection(self) -> Dict[str, Any]:
        """Cloud veritabanı bağlantısını test et"""
        print("Cloud Database Connection Test")
        print("=" * 40)
        
        if self.cloud_db_config['api_url']:
            # API tabanlı bağlantı testi
            return self._test_api_connection()
        elif self.cloud_db_config['host']:
            # Direkt veritabanı bağlantı testi
            return self._test_direct_db_connection()
        else:
            return {
                "success": False,
                "error": "No cloud database configuration found"
            }
    
    def _test_api_connection(self) -> Dict[str, Any]:
        """API tabanlı cloud bağlantısını test et"""
        try:
            headers = {
                'Authorization': f"Bearer {self.cloud_db_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            # Test endpoint'leri
            test_endpoints = [
                f"{self.cloud_db_config['api_url']}/api/health",
                f"{self.cloud_db_config['api_url']}/api/status",
                f"{self.cloud_db_config['api_url']}/api/test",
                f"{self.cloud_db_config['api_url']}/"
            ]
            
            for endpoint in test_endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=5, verify=False)
                    if response.status_code == 200:
                        return {
                            "success": True,
                            "method": "API",
                            "endpoint": endpoint,
                            "response": response.json() if response.content else {}
                        }
                except Exception as e:
                    continue
            
            return {
                "success": False,
                "method": "API",
                "error": "No working API endpoint found"
            }
            
        except Exception as e:
            return {
                "success": False,
                "method": "API",
                "error": str(e)
            }
    
    def _test_direct_db_connection(self) -> Dict[str, Any]:
        """Direkt veritabanı bağlantısını test et"""
        try:
            db_type = self.cloud_db_config['type'].lower()
            
            if db_type == 'mysql':
                connection = pymysql.connect(
                    host=self.cloud_db_config['host'],
                    port=self.cloud_db_config['port'],
                    user=self.cloud_db_config['username'],
                    password=self.cloud_db_config['password'],
                    database=self.cloud_db_config['database'],
                    connect_timeout=5
                )
                
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                connection.close()
                
                return {
                    "success": True,
                    "method": "Direct DB",
                    "type": "MySQL"
                }
                
            elif db_type == 'postgresql':
                connection = psycopg2.connect(
                    host=self.cloud_db_config['host'],
                    port=self.cloud_db_config['port'],
                    user=self.cloud_db_config['username'],
                    password=self.cloud_db_config['password'],
                    database=self.cloud_db_config['database'],
                    connect_timeout=5
                )
                
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                connection.close()
                
                return {
                    "success": True,
                    "method": "Direct DB",
                    "type": "PostgreSQL"
                }
                
            else:
                return {
                    "success": False,
                    "method": "Direct DB",
                    "error": f"Unsupported database type: {db_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "Direct DB",
                "error": str(e)
            }
    
    def get_sales_data_from_cloud(self, date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """Cloud'dan satış verilerini al"""
        try:
            if not date_from:
                date_from = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if not date_to:
                date_to = datetime.now().strftime("%Y-%m-%d")
            
            if self.cloud_db_config['api_url']:
                return self._get_sales_data_from_api(date_from, date_to)
            else:
                return self._get_sales_data_from_db(date_from, date_to)
                
        except Exception as e:
            print(f"Cloud veri alma hatası: {str(e)}")
            return []
    
    def _get_sales_data_from_api(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """API'den satış verilerini al"""
        try:
            headers = {
                'Authorization': f"Bearer {self.cloud_db_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            params = {
                'date_from': date_from,
                'date_to': date_to,
                'format': 'json'
            }
            
            # API endpoint'lerini dene
            api_endpoints = [
                f"{self.cloud_db_config['api_url']}/api/sales",
                f"{self.cloud_db_config['api_url']}/api/transactions",
                f"{self.cloud_db_config['api_url']}/api/reports/sales",
                f"{self.cloud_db_config['api_url']}/api/data/sales"
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, params=params, timeout=10, verify=False)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict) and "data" in data:
                            return data["data"]
                        elif isinstance(data, list):
                            return data
                        else:
                            return [data]
                            
                except Exception as e:
                    continue
            
            return []
            
        except Exception as e:
            print(f"API veri alma hatası: {str(e)}")
            return []
    
    def _get_sales_data_from_db(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """Veritabanından satış verilerini al"""
        try:
            db_type = self.cloud_db_config['type'].lower()
            
            if db_type == 'mysql':
                return self._get_sales_data_from_mysql(date_from, date_to)
            elif db_type == 'postgresql':
                return self._get_sales_data_from_postgresql(date_from, date_to)
            else:
                print(f"Desteklenmeyen veritabanı tipi: {db_type}")
                return []
                
        except Exception as e:
            print(f"Veritabanı veri alma hatası: {str(e)}")
            return []
    
    def _get_sales_data_from_mysql(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """MySQL'den satış verilerini al"""
        try:
            connection = pymysql.connect(
                host=self.cloud_db_config['host'],
                port=self.cloud_db_config['port'],
                user=self.cloud_db_config['username'],
                password=self.cloud_db_config['password'],
                database=self.cloud_db_config['database']
            )
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            # Yaygın tablo isimlerini dene
            table_queries = [
                "SELECT * FROM sales WHERE DATE(created_at) BETWEEN %s AND %s",
                "SELECT * FROM transactions WHERE DATE(transaction_date) BETWEEN %s AND %s",
                "SELECT * FROM orders WHERE DATE(order_date) BETWEEN %s AND %s",
                "SELECT * FROM receipts WHERE DATE(receipt_date) BETWEEN %s AND %s"
            ]
            
            for query in table_queries:
                try:
                    cursor.execute(query, (date_from, date_to))
                    results = cursor.fetchall()
                    
                    if results:
                        print(f"MySQL'den {len(results)} kayıt alındı")
                        return results
                        
                except Exception as e:
                    continue
            
            connection.close()
            return []
            
        except Exception as e:
            print(f"MySQL bağlantı hatası: {str(e)}")
            return []
    
    def _get_sales_data_from_postgresql(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """PostgreSQL'den satış verilerini al"""
        try:
            connection = psycopg2.connect(
                host=self.cloud_db_config['host'],
                port=self.cloud_db_config['port'],
                user=self.cloud_db_config['username'],
                password=self.cloud_db_config['password'],
                database=self.cloud_db_config['database']
            )
            
            cursor = connection.cursor()
            
            # Yaygın tablo isimlerini dene
            table_queries = [
                "SELECT * FROM sales WHERE DATE(created_at) BETWEEN %s AND %s",
                "SELECT * FROM transactions WHERE DATE(transaction_date) BETWEEN %s AND %s",
                "SELECT * FROM orders WHERE DATE(order_date) BETWEEN %s AND %s"
            ]
            
            for query in table_queries:
                try:
                    cursor.execute(query, (date_from, date_to))
                    columns = [desc[0] for desc in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    if results:
                        print(f"PostgreSQL'den {len(results)} kayıt alındı")
                        return results
                        
                except Exception as e:
                    continue
            
            connection.close()
            return []
            
        except Exception as e:
            print(f"PostgreSQL bağlantı hatası: {str(e)}")
            return []
    
    def convert_cloud_data_to_our_format(self, cloud_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cloud verisini bizim formata dönüştür"""
        converted_data = []
        
        for record in cloud_data:
            try:
                # Tarih formatını dönüştür
                date_field = None
                for field in ['created_at', 'transaction_date', 'order_date', 'receipt_date', 'date']:
                    if field in record and record[field]:
                        date_field = record[field]
                        break
                
                if date_field:
                    if isinstance(date_field, str):
                        date_part = date_field.split(' ')[0] if ' ' in date_field else date_field.split('T')[0]
                    else:
                        date_part = date_field.strftime("%Y-%m-%d")
                else:
                    date_part = datetime.now().strftime("%Y-%m-%d")
                
                # Ürün bilgilerini çıkar
                items = []
                total_amount = 0
                total_quantity = 0
                
                # Tek ürün kaydı mı yoksa detay kayıtları mı?
                if 'product_name' in record or 'item_name' in record:
                    # Tek ürün kaydı
                    product_name = record.get('product_name') or record.get('item_name', '')
                    quantity = float(record.get('quantity', record.get('qty', 1)))
                    unit_price = float(record.get('unit_price', record.get('price', 0)))
                    total_price = float(record.get('total_price', record.get('amount', quantity * unit_price)))
                    
                    items.append({
                        "product": product_name,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "total_price": total_price
                    })
                    
                    total_amount = total_price
                    total_quantity = quantity
                else:
                    # Toplam tutar varsa kullan
                    total_amount = float(record.get('total_amount', record.get('total', record.get('amount', 0))))
                
                our_format = {
                    "date": date_part,
                    "total_quantity": total_quantity,
                    "total_sales": total_amount,
                    "items_sold": json.dumps(items, ensure_ascii=False),
                    "customer_info": json.dumps({
                        "name": record.get('customer_name', ''),
                        "phone": record.get('customer_phone', ''),
                        "email": record.get('customer_email', '')
                    }, ensure_ascii=False),
                    "payment_info": json.dumps([{
                        "method": record.get('payment_method', ''),
                        "amount": total_amount
                    }], ensure_ascii=False),
                    "transaction_id": record.get('id', record.get('transaction_id', '')),
                    "order_no": record.get('order_no', record.get('order_number', '')),
                    "learning_data": json.dumps({
                        "source": "yazar_kasa_cloud",
                        "sync_date": datetime.now().isoformat(),
                        "original_data": record
                    }, ensure_ascii=False)
                }
                
                converted_data.append(our_format)
                
            except Exception as e:
                print(f"Veri dönüştürme hatası: {str(e)}")
                continue
        
        return converted_data
    
    def sync_to_supabase(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Cloud verilerini Supabase'e senkronize et"""
        try:
            print(f"Cloud senkronizasyon başlıyor: {date_from or 'yesterday'} - {date_to or 'today'}")
            
            # Cloud'dan veri al
            cloud_data = self.get_sales_data_from_cloud(date_from, date_to)
            
            if not cloud_data:
                return {
                    "success": False,
                    "error": "No data received from cloud"
                }
            
            # Bizim formata dönüştür
            converted_data = self.convert_cloud_data_to_our_format(cloud_data)
            
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
                    result = self.supabase.client.table("sales_history").insert(data).execute()
                    
                    if result.data:
                        synced_count += 1
                        print(f"Cloud satış kaydedildi: {data.get('transaction_id')}")
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
            
            print(f"Cloud senkronizasyon tamamlandı: {synced_count}/{len(converted_data)} kayıt başarılı")
            return result
            
        except Exception as e:
            error_msg = f"Cloud senkronizasyon hatası: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    
    def start_auto_sync(self):
        """Otomatik senkronizasyonu başlat"""
        print(f"Otomatik cloud senkronizasyon başlatıldı (her {self.sync_interval} saniyede)")
        
        async def sync_loop():
            while True:
                try:
                    await asyncio.sleep(self.sync_interval)
                    
                    # Son senkronizasyondan bu yana geçen süre
                    if self.last_sync_time:
                        time_diff = datetime.now() - self.last_sync_time
                        if time_diff.total_seconds() < self.sync_interval:
                            continue
                    
                    # Son 1 saatteki verileri senkronize et
                    end_time = datetime.now()
                    start_time = end_time - timedelta(hours=1)
                    
                    result = self.sync_to_supabase(
                        start_time.strftime("%Y-%m-%d"),
                        end_time.strftime("%Y-%m-%d")
                    )
                    
                    if result["success"]:
                        self.last_sync_time = datetime.now()
                        print(f"Otomatik senkronizasyon başarılı: {result['synced_count']} kayıt")
                    else:
                        print(f"Otomatik senkronizasyon başarısız: {result.get('error')}")
                        
                except Exception as e:
                    print(f"Otomatik senkronizasyon hatası: {str(e)}")
                    await asyncio.sleep(60)  # Hata durumunda 1 dakika bekle
        
        # Async loop'u başlat
        asyncio.create_task(sync_loop())
