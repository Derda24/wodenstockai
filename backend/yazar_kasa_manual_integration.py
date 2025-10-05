"""
YAZAR KASA LİNK Manuel Entegrasyon Sistemi
API çalışmadığında alternatif çözüm
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class YazarKasaManualIntegration:
    def __init__(self):
        self.api_key = os.getenv('YAZAR_KASA_API_KEY')
        self.serial_number = os.getenv('YAZAR_KASA_SERIAL_NUMBER')
        self.base_url = os.getenv('YAZAR_KASA_BASE_URL', 'http://192.168.1.187:4568')
        
    def check_api_status(self):
        """API durumunu kontrol et"""
        print("YAZAR KASA LİNK API Durum Kontrolü")
        print("=" * 40)
        print(f"API Key: {self.api_key[:10] if self.api_key else 'YOK'}...")
        print(f"Serial: {self.serial_number if self.serial_number else 'YOK'}")
        print(f"URL: {self.base_url}")
        
        # Basit bağlantı testi
        import requests
        try:
            response = requests.get(self.base_url, timeout=5, verify=False)
            print(f"API Status: BAŞARILI ({response.status_code})")
            return True
        except Exception as e:
            print(f"API Status: BAŞARISIZ - {str(e)}")
            return False
    
    def suggest_alternatives(self):
        """Alternatif entegrasyon yöntemleri öner"""
        print("\nALTERNATIF ENTEGRASYON YONTEMLERI")
        print("=" * 50)
        
        alternatives = [
            {
                "method": "1. YAZAR KASA LİNK Ayarları",
                "description": "YAZAR KASA LİNK yazılımında API servisini aktifleştir",
                "steps": [
                    "YAZAR KASA LİNK yazılımını aç",
                    "Ayarlar > API/Ağ bölümüne git",
                    "API servisini aktifleştir",
                    "Port numarasını kontrol et (4568)",
                    "API Key'i doğrula"
                ]
            },
            {
                "method": "2. Veritabanı Bağlantısı",
                "description": "YAZAR KASA LİNK'in veritabanına direkt bağlan",
                "steps": [
                    "YAZAR KASA LİNK'in kullandığı veritabanını bul",
                    "Veritabanı bağlantı bilgilerini al",
                    "SQL sorguları ile veri çek",
                    "Otomatik senkronizasyon kur"
                ]
            },
            {
                "method": "3. Dosya Paylaşımı",
                "description": "Network üzerinden dosya paylaşımı",
                "steps": [
                    "YAZAR KASA LİNK'den Excel export ayarla",
                    "Belirli klasöre otomatik kaydet",
                    "Bizim sistem dosyayı okuyup işle",
                    "Zamanlanmış görev ile otomatikleştir"
                ]
            },
            {
                "method": "4. Web Interface",
                "description": "YAZAR KASA LİNK'in web arayüzünü kullan",
                "steps": [
                    "YAZAR KASA LİNK'in web arayüzünü bul",
                    "Tarayıcı ile giriş yap",
                    "Veri export/import işlemleri",
                    "Otomatik scraping sistemi kur"
                ]
            }
        ]
        
        for alt in alternatives:
            print(f"\n{alt['method']}")
            print(f"  {alt['description']}")
            print("  Adımlar:")
            for step in alt['steps']:
                print(f"    - {step}")
    
    def create_excel_template(self):
        """YAZAR KASA LİNK için Excel template oluştur"""
        print("\nEXCEL TEMPLATE OLUSTURMA")
        print("=" * 30)
        
        template = {
            "instructions": [
                "Bu template YAZAR KASA LİNK'den export edilecek veri formatını gösterir",
                "YAZAR KASA LİNK'de bu formatta export yapın",
                "Export edilen dosyayı bizim sisteme yükleyin"
            ],
            "required_columns": [
                "Tarih",
                "Ürün Adı", 
                "Miktar",
                "Birim Fiyat",
                "Toplam Tutar",
                "Müşteri (opsiyonel)"
            ],
            "date_format": "YYYY-MM-DD",
            "file_format": "Excel (.xlsx)"
        }
        
        print("Template Bilgileri:")
        for key, value in template.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")
        
        # Template dosyasını kaydet
        with open('yazar_kasa_template.json', 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"\nTemplate 'yazar_kasa_template.json' dosyasına kaydedildi.")
    
    def generate_integration_plan(self):
        """Entegrasyon planı oluştur"""
        print("\nENTEGRASYON PLANI")
        print("=" * 30)
        
        plan = {
            "phase1": {
                "title": "YAZAR KASA LİNK Kurulumu",
                "tasks": [
                    "YAZAR KASA LİNK yazılımını kontrol et",
                    "API servisini aktifleştir",
                    "Port ve IP ayarlarını doğrula",
                    "API Key'i test et"
                ],
                "estimated_time": "30 dakika"
            },
            "phase2": {
                "title": "API Entegrasyonu",
                "tasks": [
                    "API endpoint'lerini keşfet",
                    "Veri formatını analiz et",
                    "Entegrasyon servisi oluştur",
                    "Test verileri ile dene"
                ],
                "estimated_time": "2-3 saat"
            },
            "phase3": {
                "title": "Otomatik Senkronizasyon",
                "tasks": [
                    "Zamanlanmış görevler kur",
                    "Hata yönetimi ekle",
                    "Log sistemi oluştur",
                    "Performans optimizasyonu"
                ],
                "estimated_time": "1-2 saat"
            }
        }
        
        for phase_key, phase in plan.items():
            print(f"\n{phase['title']} ({phase['estimated_time']})")
            for task in phase['tasks']:
                print(f"  - {task}")
        
        return plan

def main():
    integration = YazarKasaManualIntegration()
    
    # API durumunu kontrol et
    api_working = integration.check_api_status()
    
    if not api_working:
        # Alternatif yöntemleri öner
        integration.suggest_alternatives()
        
        # Excel template oluştur
        integration.create_excel_template()
        
        # Entegrasyon planı oluştur
        integration.generate_integration_plan()
        
        print(f"\n{'='*50}")
        print("SONRAKI ADIMLAR:")
        print("1. YAZAR KASA LİNK yazılımını kontrol edin")
        print("2. API servisini aktifleştirin")
        print("3. Port ayarlarını doğrulayın")
        print("4. Test yapmak için tekrar çalıştırın")

if __name__ == "__main__":
    main()
