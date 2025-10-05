"""
Cloud Database Sync Test Aracı
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'services'))

from cloud_database_sync import CloudDatabaseSync
from supabase_service import SupabaseService

def test_cloud_database_sync():
    """Cloud veritabanı senkronizasyonunu test et"""
    print("Cloud Database Sync Test")
    print("=" * 50)
    
    # Servisleri başlat
    try:
        supabase = SupabaseService()
        cloud_sync = CloudDatabaseSync(supabase)
        print("Servisler başlatıldı")
    except Exception as e:
        print(f"Servis başlatma hatası: {str(e)}")
        return
    
    # 1. Cloud bağlantı testi
    print("\n1. Cloud Database Bağlantı Testi")
    print("-" * 40)
    
    connection_test = cloud_sync.test_cloud_connection()
    if connection_test["success"]:
        print("SUCCESS: Cloud database bağlantısı başarılı")
        print(f"  Method: {connection_test.get('method')}")
        print(f"  Type: {connection_test.get('type', 'Unknown')}")
        if 'endpoint' in connection_test:
            print(f"  Endpoint: {connection_test.get('endpoint')}")
    else:
        print("FAILED: Cloud database bağlantısı başarısız")
        print(f"  Method: {connection_test.get('method')}")
        print(f"  Error: {connection_test.get('error')}")
        
        print("\nCloud database yapılandırması gerekli:")
        print("1. DARA YAZILIM'dan cloud veritabanı bilgilerini alın")
        print("2. .env dosyasına ekleyin:")
        print("   YAZAR_KASA_CLOUD_DB_HOST=your-host")
        print("   YAZAR_KASA_CLOUD_DB_USER=your-username")
        print("   YAZAR_KASA_CLOUD_DB_PASSWORD=your-password")
        print("   YAZAR_KASA_CLOUD_DB_NAME=your-database")
        return
    
    # 2. Veri alma testi
    print("\n2. Cloud'dan Veri Alma Testi")
    print("-" * 40)
    
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    cloud_data = cloud_sync.get_sales_data_from_cloud(yesterday, today)
    
    if cloud_data:
        print(f"SUCCESS: {len(cloud_data)} veri alındı")
        
        # İlk veriyi analiz et
        if len(cloud_data) > 0:
            first_record = cloud_data[0]
            print("  İlk kayıt:")
            print(f"    Keys: {list(first_record.keys())}")
            print(f"    Sample: {str(first_record)[:200]}...")
            
            # Veri dönüştürme testi
            converted_data = cloud_sync.convert_cloud_data_to_our_format([first_record])
            if converted_data:
                print("  Dönüştürülen format:")
                print(f"    Tarih: {converted_data[0].get('date')}")
                print(f"    Toplam tutar: {converted_data[0].get('total_sales')}")
                print(f"    Toplam miktar: {converted_data[0].get('total_quantity')}")
    else:
        print("FAILED: Cloud'dan veri alınamadı")
        print("Olası nedenler:")
        print("- Veritabanı bağlantı bilgileri yanlış")
        print("- Tablo isimleri farklı")
        print("- Tarih formatı uyumsuz")
        print("- Veri yok")
    
    # 3. Supabase senkronizasyon testi
    print("\n3. Supabase Senkronizasyon Testi")
    print("-" * 40)
    
    try:
        sync_result = cloud_sync.sync_to_supabase(yesterday, today)
        
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

def create_setup_guide():
    """Kurulum rehberi oluştur"""
    guide = {
        "title": "YAZAR KASA LİNK Cloud Database Kurulum Rehberi",
        "steps": [
            {
                "step": 1,
                "title": "DARA YAZILIM ile İletişim",
                "description": "Cloud veritabanı bilgilerini alın",
                "required_info": [
                    "Veritabanı tipi (MySQL, PostgreSQL, SQLite)",
                    "Host adresi",
                    "Port numarası",
                    "Veritabanı adı",
                    "Kullanıcı adı ve şifre",
                    "Tablo yapısı (sales, transactions, orders, vb.)",
                    "API URL (varsa)"
                ]
            },
            {
                "step": 2,
                "title": "Environment Dosyası Güncelleme",
                "description": ".env dosyasına cloud bilgilerini ekleyin",
                "example": {
                    "YAZAR_KASA_CLOUD_DB_TYPE": "mysql",
                    "YAZAR_KASA_CLOUD_DB_HOST": "your-host.com",
                    "YAZAR_KASA_CLOUD_DB_PORT": "3306",
                    "YAZAR_KASA_CLOUD_DB_NAME": "yazarkasa_db",
                    "YAZAR_KASA_CLOUD_DB_USER": "your_username",
                    "YAZAR_KASA_CLOUD_DB_PASSWORD": "your_password"
                }
            },
            {
                "step": 3,
                "title": "Test ve Doğrulama",
                "description": "Bağlantıyı test edin",
                "commands": [
                    "python backend/test_cloud_database_sync.py"
                ]
            },
            {
                "step": 4,
                "title": "Otomatik Senkronizasyon",
                "description": "Otomatik senkronizasyonu aktifleştirin",
                "benefits": [
                    "Her 5 dakikada bir otomatik veri çekme",
                    "Gerçek zamanlı satış verileri",
                    "Manuel Excel işlemi gereksiz",
                    "AI Analytics otomatik güncellenir"
                ]
            }
        ],
        "benefits": [
            "Manuel Excel export/import gereksiz",
            "Gerçek zamanlı veri senkronizasyonu",
            "AI Analytics otomatik güncellenir",
            "Hata riski minimize edilir",
            "İnsan müdahalesi gereksiz"
        ]
    }
    
    import json
    with open('cloud_database_setup_guide.json', 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)
    
    print("\nKurulum Rehberi:")
    print("=" * 30)
    for step in guide["steps"]:
        print(f"\n{step['step']}. {step['title']}")
        print(f"   {step['description']}")
        if 'required_info' in step:
            print("   Gerekli Bilgiler:")
            for info in step['required_info']:
                print(f"     - {info}")
        if 'example' in step:
            print("   Örnek:")
            for key, value in step['example'].items():
                print(f"     {key}={value}")
    
    print(f"\nFaydalar:")
    for benefit in guide["benefits"]:
        print(f"  • {benefit}")
    
    print(f"\nDetaylı rehber 'cloud_database_setup_guide.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    create_setup_guide()
    print("\n" + "="*50)
    test_cloud_database_sync()
