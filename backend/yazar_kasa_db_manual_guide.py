"""
YAZAR KASA LİNK Manuel Veritabanı Keşif Rehberi
"""

import json
from datetime import datetime

def create_manual_discovery_guide():
    """Manuel veritabanı keşif rehberi oluştur"""
    
    guide = {
        "title": "YAZAR KASA LİNK Veritabanı Manuel Keşif Rehberi",
        "created_at": datetime.now().isoformat(),
        
        "step1": {
            "title": "YAZAR KASA LİNK Yazılımını İnceleyin",
            "description": "YAZAR KASA LİNK programını açıp ayarlarını kontrol edin",
            "actions": [
                "YAZAR KASA LİNK yazılımını açın",
                "Ayarlar/Settings menüsüne gidin",
                "Veritabanı/Database bölümünü bulun",
                "Bağlantı bilgilerini not edin",
                "Veritabanı tipini öğrenin (MySQL, PostgreSQL, SQLite, vb.)"
            ]
        },
        
        "step2": {
            "title": "Veritabanı Bağlantı Bilgilerini Toplayın",
            "description": "Gerekli bağlantı parametrelerini öğrenin",
            "required_info": {
                "database_type": "Veritabanı tipi (MySQL, PostgreSQL, SQLite, vb.)",
                "host": "Sunucu adresi (192.168.1.187 veya localhost)",
                "port": "Port numarası (3306, 5432, vb.)",
                "database_name": "Veritabanı adı",
                "username": "Kullanıcı adı",
                "password": "Şifre",
                "file_path": "SQLite için dosya yolu"
            }
        },
        
        "step3": {
            "title": "Network Erişim Kontrolü",
            "description": "YAZAR KASA LİNK sunucusuna erişimi kontrol edin",
            "actions": [
                "YAZAR KASA LİNK sunucusunda Windows Firewall'u kontrol edin",
                "Veritabanı port'unun açık olduğunu doğrulayın",
                "Network dosya paylaşımını kontrol edin",
                "YAZAR KASA LİNK'in hangi IP'de çalıştığını doğrulayın"
            ]
        },
        
        "step4": {
            "title": "Alternatif Erişim Yöntemleri",
            "description": "Direkt erişim mümkün değilse alternatif yöntemler",
            "methods": [
                {
                    "method": "Remote Desktop",
                    "description": "YAZAR KASA LİNK sunucusuna uzaktan bağlan",
                    "steps": [
                        "Remote Desktop ile 192.168.1.187'e bağlan",
                        "YAZAR KASA LİNK yazılımını aç",
                        "Veritabanı ayarlarını kontrol et",
                        "Veri export işlemini yap"
                    ]
                },
                {
                    "method": "Network Dosya Paylaşımı",
                    "description": "Dosya paylaşımı üzerinden erişim",
                    "steps": [
                        "YAZAR KASA LİNK sunucusunda dosya paylaşımını aktifleştir",
                        "Veritabanı dosyalarının bulunduğu klasörü paylaş",
                        "Network üzerinden dosyalara eriş",
                        "Veritabanı dosyalarını kopyala"
                    ]
                },
                {
                    "method": "YAZAR KASA LİNK Export",
                    "description": "YAZAR KASA LİNK'den veri export et",
                    "steps": [
                        "YAZAR KASA LİNK'de rapor/export menüsünü bul",
                        "Satış verilerini Excel/CSV formatında export et",
                        "Export edilen dosyayı bizim sisteme yükle",
                        "Otomatik export ayarlarını yap"
                    ]
                }
            ]
        },
        
        "step5": {
            "title": "Veritabanı Şeması Analizi",
            "description": "YAZAR KASA LİNK'in veri yapısını anlayın",
            "common_tables": [
                "sales - Satış kayıtları",
                "products - Ürün bilgileri", 
                "customers - Müşteri bilgileri",
                "transactions - İşlem kayıtları",
                "inventory - Stok bilgileri",
                "users - Kullanıcı bilgileri",
                "settings - Sistem ayarları"
            ],
            "important_columns": {
                "sales": ["date", "product_id", "quantity", "price", "total", "customer_id"],
                "products": ["id", "name", "price", "category", "stock_quantity"],
                "customers": ["id", "name", "phone", "email", "address"]
            }
        },
        
        "step6": {
            "title": "SQL Sorguları",
            "description": "Veri çekmek için kullanılabilecek SQL sorguları",
            "queries": {
                "daily_sales": "SELECT * FROM sales WHERE DATE(created_at) = CURDATE()",
                "product_sales": "SELECT product_id, SUM(quantity) as total_qty FROM sales GROUP BY product_id",
                "customer_sales": "SELECT c.name, SUM(s.total) as total_spent FROM sales s JOIN customers c ON s.customer_id = c.id GROUP BY c.id",
                "inventory_check": "SELECT p.name, p.stock_quantity FROM products p WHERE p.stock_quantity < 10"
            }
        }
    }
    
    # Rehberi dosyaya kaydet
    with open('yazar_kasa_manual_guide.json', 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)
    
    return guide

def print_guide_summary():
    """Rehber özetini yazdır"""
    guide = create_manual_discovery_guide()
    
    print("YAZAR KASA LİNK Manuel Veritabanı Keşif Rehberi")
    print("=" * 60)
    
    for key, step in guide.items():
        if key.startswith('step'):
            print(f"\n{step['title']}")
            print("-" * 40)
            print(f"{step['description']}")
            
            if 'actions' in step:
                print("Adımlar:")
                for action in step['actions']:
                    print(f"  • {action}")
            
            if 'required_info' in step:
                print("Gerekli Bilgiler:")
                for info_key, info_desc in step['required_info'].items():
                    print(f"  • {info_key}: {info_desc}")
            
            if 'methods' in step:
                for method in step['methods']:
                    print(f"\n  {method['method']}:")
                    print(f"    {method['description']}")
                    print("    Adımlar:")
                    for step_desc in method['steps']:
                        print(f"      - {step_desc}")
            
            if 'common_tables' in step:
                print("Yaygın Tablolar:")
                for table in step['common_tables']:
                    print(f"  • {table}")
            
            if 'important_columns' in step:
                print("Önemli Sütunlar:")
                for table, columns in step['important_columns'].items():
                    print(f"  • {table}: {', '.join(columns)}")
            
            if 'queries' in step:
                print("SQL Sorguları:")
                for query_name, query in step['queries'].items():
                    print(f"  • {query_name}: {query}")

if __name__ == "__main__":
    print_guide_summary()
    print(f"\n{'='*60}")
    print("Detaylı rehber 'yazar_kasa_manual_guide.json' dosyasına kaydedildi.")
    print("\nSONRAKI ADIMLAR:")
    print("1. YAZAR KASA LİNK yazılımını açın")
    print("2. Veritabanı ayarlarını kontrol edin")
    print("3. Bağlantı bilgilerini toplayın")
    print("4. Bilgileri paylaşın")
