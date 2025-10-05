"""
Adisyon Sistemi Keşif ve Bağlantı Aracı
YAZAR KASA LİNK POS cihazından Adisyon sistemine bağlantı
"""

import requests
import json
import socket
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class AdisyonSystemDiscovery:
    def __init__(self):
        self.host = "192.168.1.187"
        self.common_ports = [
            80, 443, 8080, 8000, 3000, 5000, 9000,  # Web servisleri
            3306, 5432, 1433, 1521, 3050,           # Veritabanları
            4567, 4568, 4569,                       # Adisyon özel portları
            8081, 8082, 8083,                       # Alternatif web portları
        ]
        
    def scan_adisyon_ports(self):
        """Adisyon sisteminin port'larını tara"""
        print("Adisyon Sistemi Port Tarama")
        print("=" * 40)
        
        open_ports = []
        
        for port in self.common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.host, port))
                
                if result == 0:
                    service_type = self.get_service_type(port)
                    print(f"OPEN Port {port}: {service_type}")
                    open_ports.append((port, service_type))
                else:
                    service_type = self.get_service_type(port)
                    print(f"CLOSED Port {port}: {service_type}")
                    
                sock.close()
                
            except Exception as e:
                print(f"ERROR Port {port}: {str(e)[:30]}")
        
        return open_ports
    
    def get_service_type(self, port):
        """Port numarasına göre servis tipini belirle"""
        service_types = {
            80: "HTTP",
            443: "HTTPS",
            8080: "HTTP Alt",
            8000: "HTTP Alt",
            3000: "Node.js",
            5000: "Flask",
            9000: "Web Alt",
            3306: "MySQL",
            5432: "PostgreSQL",
            1433: "SQL Server",
            1521: "Oracle",
            3050: "Firebird",
            4567: "Adisyon API",
            4568: "YAZAR KASA LİNK",
            4569: "Adisyon Alt",
            8081: "Web Alt 1",
            8082: "Web Alt 2",
            8083: "Web Alt 3"
        }
        return service_types.get(port, "Unknown")
    
    def test_web_interfaces(self, open_ports):
        """Açık port'larda web arayüzlerini test et"""
        print(f"\nWeb Arayüz Testi")
        print("=" * 30)
        
        web_ports = [port for port, service in open_ports if service in ['HTTP', 'HTTPS', 'HTTP Alt', 'Node.js', 'Flask', 'Web Alt']]
        
        test_paths = [
            '/',
            '/admin',
            '/login',
            '/dashboard',
            '/api',
            '/adisyon',
            '/pos',
            '/kasa',
            '/yazarkasa',
            '/reports',
            '/sales',
            '/transactions'
        ]
        
        working_interfaces = []
        
        for port in web_ports:
            print(f"\nPort {port} için web arayüz testi:")
            
            for protocol in ['http', 'https']:
                for path in test_paths:
                    url = f"{protocol}://{self.host}:{port}{path}"
                    try:
                        response = requests.get(url, timeout=3, verify=False)
                        
                        if response.status_code == 200:
                            print(f"  SUCCESS: {url}")
                            working_interfaces.append({
                                'url': url,
                                'port': port,
                                'protocol': protocol,
                                'path': path,
                                'status': response.status_code,
                                'content_type': response.headers.get('Content-Type', 'Unknown')
                            })
                            
                            # Sayfa içeriğini analiz et
                            content = response.text.lower()
                            if any(keyword in content for keyword in ['login', 'giriş', 'admin', 'yönetici']):
                                print(f"    -> Login/Admin sayfası olabilir")
                            if any(keyword in content for keyword in ['adisyon', 'pos', 'kasa', 'satış']):
                                print(f"    -> Adisyon/POS sayfası olabilir")
                            if any(keyword in content for keyword in ['api', 'json', 'data']):
                                print(f"    -> API endpoint olabilir")
                                
                    except Exception as e:
                        pass  # Sessizce devam et
        
        return working_interfaces
    
    def test_api_endpoints(self, open_ports):
        """API endpoint'lerini test et"""
        print(f"\nAPI Endpoint Testi")
        print("=" * 30)
        
        web_ports = [port for port, service in open_ports if service in ['HTTP', 'HTTPS', 'HTTP Alt', 'Node.js', 'Flask']]
        
        api_paths = [
            '/api',
            '/api/v1',
            '/api/v2',
            '/api/sales',
            '/api/transactions',
            '/api/reports',
            '/api/data',
            '/api/export',
            '/api/import',
            '/api/sync',
            '/adisyon/api',
            '/pos/api',
            '/kasa/api'
        ]
        
        working_apis = []
        
        for port in web_ports:
            print(f"\nPort {port} için API testi:")
            
            for protocol in ['http', 'https']:
                for path in api_paths:
                    url = f"{protocol}://{self.host}:{port}{path}"
                    try:
                        response = requests.get(url, timeout=3, verify=False)
                        
                        if response.status_code in [200, 401, 403]:  # 401/403 de API olduğunu gösterir
                            print(f"  API FOUND: {url} - Status: {response.status_code}")
                            working_apis.append({
                                'url': url,
                                'port': port,
                                'protocol': protocol,
                                'path': path,
                                'status': response.status_code,
                                'response': response.text[:200] if response.text else ''
                            })
                            
                    except Exception as e:
                        pass
        
        return working_apis
    
    def test_database_connections(self, open_ports):
        """Veritabanı bağlantılarını test et"""
        print(f"\nVeritabanı Bağlantı Testi")
        print("=" * 30)
        
        db_ports = [port for port, service in open_ports if service in ['MySQL', 'PostgreSQL', 'SQL Server', 'Oracle', 'Firebird']]
        
        if not db_ports:
            print("Açık veritabanı port'u bulunamadı")
            return []
        
        # MySQL test
        if 3306 in [port for port, _ in open_ports]:
            print("MySQL bağlantısı test ediliyor...")
            try:
                import pymysql
                connection = pymysql.connect(
                    host=self.host,
                    port=3306,
                    user='root',
                    password='',
                    connect_timeout=5
                )
                print("  MySQL bağlantısı başarılı!")
                connection.close()
            except Exception as e:
                print(f"  MySQL bağlantısı başarısız: {str(e)[:50]}")
        
        # PostgreSQL test
        if 5432 in [port for port, _ in open_ports]:
            print("PostgreSQL bağlantısı test ediliyor...")
            try:
                import psycopg2
                connection = psycopg2.connect(
                    host=self.host,
                    port=5432,
                    user='postgres',
                    password='postgres',
                    connect_timeout=5
                )
                print("  PostgreSQL bağlantısı başarılı!")
                connection.close()
            except Exception as e:
                print(f"  PostgreSQL bağlantısı başarısız: {str(e)[:50]}")
        
        return db_ports
    
    def create_connection_guide(self, open_ports, working_interfaces, working_apis):
        """Bağlantı rehberi oluştur"""
        guide = {
            "discovery_date": datetime.now().isoformat(),
            "host": self.host,
            "open_ports": [{"port": port, "service": service} for port, service in open_ports],
            "working_interfaces": working_interfaces,
            "working_apis": working_apis,
            "recommendations": []
        }
        
        # Öneriler oluştur
        if working_interfaces:
            guide["recommendations"].append({
                "method": "Web Interface",
                "description": "Adisyon sisteminin web arayüzünü kullan",
                "steps": [
                    f"Tarayıcıda {working_interfaces[0]['url']} adresine git",
                    "Login bilgileri ile giriş yap",
                    "Satış verilerini export et",
                    "Bizim sisteme import et"
                ]
            })
        
        if working_apis:
            guide["recommendations"].append({
                "method": "API Integration",
                "description": "Adisyon sisteminin API'sini kullan",
                "steps": [
                    f"API endpoint: {working_apis[0]['url']}",
                    "API dokümantasyonunu bul",
                    "Authentication yöntemini öğren",
                    "Otomatik entegrasyon kur"
                ]
            })
        
        if any(service in ['MySQL', 'PostgreSQL'] for _, service in open_ports):
            guide["recommendations"].append({
                "method": "Database Connection",
                "description": "Adisyon sisteminin veritabanına direkt bağlan",
                "steps": [
                    "Veritabanı bağlantı bilgilerini bul",
                    "SQL sorguları ile veri çek",
                    "Otomatik senkronizasyon kur"
                ]
            })
        
        # Rehberi kaydet
        with open('adisyon_connection_guide.json', 'w', encoding='utf-8') as f:
            json.dump(guide, f, indent=2, ensure_ascii=False)
        
        return guide
    
    def print_summary(self, guide):
        """Özet raporu yazdır"""
        print(f"\n{'='*50}")
        print("ADISYON SİSTEMİ KEŞİF RAPORU")
        print(f"{'='*50}")
        
        print(f"Host: {guide['host']}")
        print(f"Keşif Tarihi: {guide['discovery_date']}")
        print(f"Açık Port Sayısı: {len(guide['open_ports'])}")
        
        if guide['working_interfaces']:
            print(f"\nÇalışan Web Arayüzleri: {len(guide['working_interfaces'])}")
            for interface in guide['working_interfaces'][:3]:
                print(f"  - {interface['url']}")
        
        if guide['working_apis']:
            print(f"\nÇalışan API'ler: {len(guide['working_apis'])}")
            for api in guide['working_apis'][:3]:
                print(f"  - {api['url']}")
        
        print(f"\nÖNERİLER:")
        for i, rec in enumerate(guide['recommendations'], 1):
            print(f"{i}. {rec['method']}: {rec['description']}")
        
        print(f"\nDetaylı rehber 'adisyon_connection_guide.json' dosyasına kaydedildi.")

def main():
    discovery = AdisyonSystemDiscovery()
    
    print("Adisyon Sistemi Keşif Aracı")
    print("=" * 50)
    print("YAZAR KASA LİNK POS cihazından Adisyon sistemine bağlantı")
    print()
    
    # 1. Port tarama
    open_ports = discovery.scan_adisyon_ports()
    
    if not open_ports:
        print("\nHiçbir port açık değil!")
        print("Adisyon sistemi çalışmıyor olabilir.")
        return
    
    # 2. Web arayüzlerini test et
    working_interfaces = discovery.test_web_interfaces(open_ports)
    
    # 3. API endpoint'lerini test et
    working_apis = discovery.test_api_endpoints(open_ports)
    
    # 4. Veritabanı bağlantılarını test et
    discovery.test_database_connections(open_ports)
    
    # 5. Bağlantı rehberi oluştur
    guide = discovery.create_connection_guide(open_ports, working_interfaces, working_apis)
    
    # 6. Özet raporu yazdır
    discovery.print_summary(guide)

if __name__ == "__main__":
    main()
