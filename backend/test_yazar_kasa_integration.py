"""
YAZAR KASA LİNK Entegrasyon Test Aracı
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'services'))

from yazar_kasa_service import YazarKasaService
from supabase_service import SupabaseService

def test_yazar_kasa_integration():
    """YAZAR KASA LİNK entegrasyonunu test et"""
    print("YAZAR KASA LİNK Entegrasyon Test")
    print("=" * 50)
    
    # Servisleri başlat
    try:
        yazar_kasa = YazarKasaService()
        supabase = SupabaseService()
        print("Servisler başlatıldı")
    except Exception as e:
        print(f"Servis başlatma hatası: {str(e)}")
        return
    
    # 1. Bağlantı testi
    print("\n1. YAZAR KASA LİNK Bağlantı Testi")
    print("-" * 40)
    
    connection_test = yazar_kasa.test_connection()
    if connection_test["success"]:
        print("SUCCESS: YAZAR KASA LİNK bağlantısı başarılı")
        print(f"  Endpoint: {connection_test.get('endpoint')}")
        print(f"  Response: {connection_test.get('response', '')[:100]}...")
    else:
        print("FAILED: YAZAR KASA LİNK bağlantısı başarısız")
        print(f"  Error: {connection_test.get('error')}")
        print("  Test edilen endpoint'ler:")
        for endpoint in connection_test.get('tested_endpoints', []):
            print(f"    - {endpoint}")
    
    # 2. Örnek işlem gönderme testi
    print("\n2. Örnek Satış İşlemi Gönderme Testi")
    print("-" * 40)
    
    sample_transaction = yazar_kasa.create_sample_transaction()
    send_result = yazar_kasa.send_sale_transaction(sample_transaction)
    
    if send_result["success"]:
        print("SUCCESS: Örnek işlem gönderildi")
        print(f"  Endpoint: {send_result.get('endpoint')}")
    else:
        print("FAILED: Örnek işlem gönderilemedi")
        print(f"  Error: {send_result.get('error')}")
    
    # 3. Veri alma testi
    print("\n3. Satış Verisi Alma Testi")
    print("-" * 40)
    
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    sales_data = yazar_kasa.get_sales_data(yesterday, today)
    
    if sales_data:
        print(f"SUCCESS: {len(sales_data)} satış verisi alındı")
        
        # İlk veriyi analiz et
        if len(sales_data) > 0:
            first_sale = sales_data[0]
            print("  İlk satış verisi:")
            print(f"    Keys: {list(first_sale.keys())}")
            
            # Veri çıkarma testi
            extracted = yazar_kasa.extract_sales_data(first_sale)
            if extracted:
                print("  Çıkarılan veriler:")
                print(f"    İşlem ID: {extracted.get('transaction_id')}")
                print(f"    Tarih: {extracted.get('transaction_date')}")
                print(f"    Tutar: {extracted.get('total_amount')}")
                print(f"    Ürün sayısı: {len(extracted.get('items', []))}")
                
                # Bizim formata dönüştürme testi
                our_format = yazar_kasa.convert_to_our_format(extracted)
                if our_format:
                    print("  Bizim format:")
                    print(f"    Tarih: {our_format.get('date')}")
                    print(f"    Toplam tutar: {our_format.get('total_sales')}")
                    print(f"    Toplam miktar: {our_format.get('total_quantity')}")
    else:
        print("FAILED: Satış verisi alınamadı")
    
    # 4. Supabase senkronizasyon testi
    print("\n4. Supabase Senkronizasyon Testi")
    print("-" * 40)
    
    try:
        sync_result = yazar_kasa.sync_to_supabase(supabase, yesterday, today)
        
        if sync_result["success"]:
            print("SUCCESS: Senkronizasyon başarılı")
            print(f"  Senkronize edilen: {sync_result.get('synced_count')}")
            print(f"  Toplam alınan: {sync_result.get('total_received')}")
            
            if sync_result.get('errors'):
                print("  Hatalar:")
                for error in sync_result['errors'][:3]:  # İlk 3 hatayı göster
                    print(f"    - {error}")
        else:
            print("FAILED: Senkronizasyon başarısız")
            print(f"  Error: {sync_result.get('error')}")
            
    except Exception as e:
        print(f"Senkronizasyon test hatası: {str(e)}")
    
    print(f"\n{'='*50}")
    print("TEST TAMAMLANDI")
    print("=" * 50)

if __name__ == "__main__":
    test_yazar_kasa_integration()
