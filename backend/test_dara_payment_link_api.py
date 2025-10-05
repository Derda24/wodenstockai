"""
DARA Payment Link API Test Aracı
Fotoğraftaki "Payment Link Request Response" API'sini test eder
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'services'))

from dara_payment_link_api import DaraPaymentLinkAPI
from supabase_service import SupabaseService

def test_dara_payment_link_api():
    """DARA Payment Link API'sini test et"""
    print("DARA Payment Link API Test")
    print("=" * 50)
    
    # Servisleri başlat
    try:
        dara_api = DaraPaymentLinkAPI()
        supabase = SupabaseService()
        print("Servisler başlatıldı")
    except Exception as e:
        print(f"Servis başlatma hatası: {str(e)}")
        return
    
    # 1. Payment Link API testi
    print("\n1. DARA Payment Link API Testi")
    print("-" * 40)
    
    api_test = dara_api.test_payment_link_api()
    
    if api_test["successful_connections"]:
        print(f"SUCCESS: {len(api_test['successful_connections'])} bağlantı bulundu!")
        
        for conn in api_test['successful_connections']:
            print(f"  - {conn['method']} {conn['url']} - Status: {conn['status']}")
            if 'note' in conn:
                print(f"    Note: {conn['note']}")
    else:
        print("FAILED: Hiçbir bağlantı bulunamadı")
        print("Olası nedenler:")
        print("- API Key yanlış")
        print("- DARA API URL'leri farklı")
        print("- Authentication yöntemi farklı")
    
    # 2. Payment Link Request testi
    print("\n2. Payment Link Request Testi")
    print("-" * 40)
    
    sample_transaction = dara_api.create_sample_transaction()
    payment_result = dara_api.send_payment_link_request(sample_transaction)
    
    if payment_result["success"]:
        print("SUCCESS: Payment Link Request gönderildi")
        print(f"  URL: {payment_result.get('url')}")
        print(f"  Response: {payment_result.get('response')}")
    else:
        print("FAILED: Payment Link Request gönderilemedi")
        print(f"  Error: {payment_result.get('error')}")
        if 'note' in payment_result:
            print(f"  Note: {payment_result.get('note')}")
        if 'response' in payment_result:
            print(f"  Response: {payment_result.get('response')[:200]}...")
    
    # 3. Cloud sync testi
    print("\n3. Cloud Sync Testi")
    print("-" * 40)
    
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    cloud_data = dara_api.get_cloud_sync_data(yesterday, today)
    
    if cloud_data:
        print(f"SUCCESS: {len(cloud_data)} cloud verisi alındı")
        
        # İlk veriyi analiz et
        if len(cloud_data) > 0:
            first_record = cloud_data[0]
            print("  İlk kayıt:")
            print(f"    Keys: {list(first_record.keys())}")
            
            # Veri dönüştürme testi
            converted_data = dara_api.convert_dara_data_to_our_format([first_record])
            if converted_data:
                print("  Dönüştürülen format:")
                print(f"    Tarih: {converted_data[0].get('date')}")
                print(f"    Toplam tutar: {converted_data[0].get('total_sales')}")
                print(f"    Toplam miktar: {converted_data[0].get('total_quantity')}")
    else:
        print("FAILED: Cloud'dan veri alınamadı")
        print("Olası nedenler:")
        print("- 401 Unauthorized (auth eksik)")
        print("- API endpoint'leri yanlış")
        print("- Veri yok")
    
    # 4. Supabase senkronizasyon testi
    print("\n4. Supabase Senkronizasyon Testi")
    print("-" * 40)
    
    try:
        sync_result = dara_api.sync_to_supabase(supabase, yesterday, today)
        
        if sync_result["success"]:
            print("SUCCESS: Senkronizasyon başarılı")
            print(f"  Senkronize edilen: {sync_result.get('synced_count')}")
            print(f"  Toplam alınan: {sync_result.get('total_received')}")
            
            if sync_result.get('errors'):
                print("  Hatalar:")
                for error in sync_result['errors'][:3]:
                    print(f"    - {error}")
        else:
            print("FAILED: Senkronizasyon başarısız")
            print(f"  Error: {sync_result.get('error')}")
            
    except Exception as e:
        print(f"Senkronizasyon test hatası: {str(e)}")
    
    print(f"\n{'='*50}")
    print("TEST TAMAMLANDI")
    print("=" * 50)
    
    # Özet rapor
    print("\nÖZET RAPOR:")
    print("-" * 20)
    
    if api_test["successful_connections"]:
        print("✅ API bağlantıları bulundu")
    else:
        print("❌ API bağlantısı bulunamadı")
    
    if payment_result["success"]:
        print("✅ Payment Link Request başarılı")
    else:
        print("❌ Payment Link Request başarısız")
        if payment_result.get('status') == 401:
            print("   🔑 401 Unauthorized - API Key veya auth eksik")
    
    if cloud_data:
        print("✅ Cloud veri alma başarılı")
    else:
        print("❌ Cloud veri alma başarısız")
    
    print(f"\nSONRAKI ADIMLAR:")
    if not api_test["successful_connections"]:
        print("1. DARA YAZILIM'dan doğru API URL'lerini alın")
        print("2. API Key ve authentication yöntemini doğrulayın")
    elif payment_result.get('status') == 401:
        print("1. API Key'i doğrulayın")
        print("2. Authentication yöntemini kontrol edin")
        print("3. DARA YAZILIM'dan doğru auth bilgilerini alın")
    else:
        print("1. Entegrasyonu aktifleştirin")
        print("2. Otomatik senkronizasyonu kurun")

def create_dara_setup_guide():
    """DARA Payment Link API kurulum rehberi"""
    guide = {
        "title": "DARA Payment Link API Kurulum Rehberi",
        "based_on": "Fotoğraftaki 'Payment Link Request Response' 401 hatası",
        "steps": [
            {
                "step": 1,
                "title": "DARA YAZILIM ile İletişim",
                "description": "Payment Link API bilgilerini alın",
                "required_info": [
                    "Doğru API URL'leri",
                    "Authentication yöntemi",
                    "API Key doğrulaması",
                    "Payment Link endpoint'leri",
                    "Cloud sync endpoint'leri"
                ]
            },
            {
                "step": 2,
                "title": "API Key Doğrulama",
                "description": "Mevcut API Key'i doğrulayın",
                "current_key": "6cbeec6d6e56797f335916a9736b24e58c21c641fa1bba81cd21ea4a81f953dd",
                "serial_number": "PAV860076930",
                "note": "Bu bilgiler fotoğraftaki JSON'da görülen bilgilerle eşleşiyor"
            },
            {
                "step": 3,
                "title": "401 Unauthorized Çözümü",
                "description": "Fotoğraftaki 401 hatasını çözün",
                "possible_causes": [
                    "API Key yanlış veya eksik",
                    "Authentication header'ı eksik",
                    "Endpoint URL'i yanlış",
                    "Permission eksik"
                ],
                "solutions": [
                    "DARA YAZILIM'dan doğru API Key'i alın",
                    "Authentication yöntemini öğrenin",
                    "Doğru endpoint URL'lerini alın"
                ]
            },
            {
                "step": 4,
                "title": "Test ve Doğrulama",
                "description": "Bağlantıyı test edin",
                "commands": [
                    "python backend/test_dara_payment_link_api.py"
                ]
            }
        ],
        "json_format": {
            "description": "DARA JSON formatı (gönderilen örnekten)",
            "sample": {
                "TransactionHandle": {
                    "SerialNumber": "PAV860076930",
                    "TransactionDate": "2025-10-05T18:57:21.31077",
                    "TransactionSequence": 31,
                    "Fingerprint": "DARA"
                },
                "Sale": {
                    "OrderNo": "0000000000ABC0020",
                    "TotalPrice": 20.0,
                    "AddedSaleItems": [],
                    "PaymentInformations": [],
                    "CustomerParty": {}
                }
            }
        }
    }
    
    import json
    with open('dara_payment_link_setup_guide.json', 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)
    
    print("\nDARA Payment Link API Kurulum Rehberi:")
    print("=" * 50)
    
    for step in guide["steps"]:
        print(f"\n{step['step']}. {step['title']}")
        print(f"   {step['description']}")
        
        if 'required_info' in step:
            print("   Gerekli Bilgiler:")
            for info in step['required_info']:
                print(f"     - {info}")
        
        if 'current_key' in step:
            print(f"   Mevcut API Key: {step['current_key'][:20]}...")
            print(f"   Serial Number: {step['serial_number']}")
            print(f"   Not: {step['note']}")
        
        if 'possible_causes' in step:
            print("   Olası Nedenler:")
            for cause in step['possible_causes']:
                print(f"     - {cause}")
            print("   Çözümler:")
            for solution in step['solutions']:
                print(f"     - {solution}")
        
        if 'commands' in step:
            print("   Komutlar:")
            for cmd in step['commands']:
                print(f"     {cmd}")
    
    print(f"\nDetaylı rehber 'dara_payment_link_setup_guide.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    create_dara_setup_guide()
    print("\n" + "="*50)
    test_dara_payment_link_api()
