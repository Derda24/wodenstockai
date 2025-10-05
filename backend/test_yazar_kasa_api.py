import requests
import json
from datetime import datetime, timedelta
import urllib3
import os
from dotenv import load_dotenv

# SSL uyarılarını devre dışı bırak (test amaçlı)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Environment dosyasını yükle
load_dotenv()

class YazarKasaAPITester:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Yaygın API base URL'leri (YAZAR KASA LİNK URL'si öncelikli)
        self.possible_urls = [
            'https://192.168.1.187:4568',  # YAZAR KASA LİNK URL
            'http://192.168.1.187:4568',   # HTTP alternatifi
            'http://localhost:8080',
            'http://localhost:3000',
            'http://localhost:5000',
            'http://127.0.0.1:8080',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:5000',
            'https://api.yazarkasa.com',
            'https://api.yazarkasa.link',
            'https://yazarkasa.com/api',
            'https://yazarkasa.link/api'
        ]
        
        # Yaygın endpoint'ler
        self.common_endpoints = [
            '/api',
            '/api/v1',
            '/api/v2',
            '/api/sales',
            '/api/products',
            '/api/stock',
            '/api/reports',
            '/api/daily',
            '/api/orders',
            '/api/transactions',
            '/health',
            '/status',
            '/info',
            '/version'
        ]
    
    def test_api_discovery(self):
        """API endpoint'lerini kesfet"""
        print("YAZAR KASA LINK API Kefsi Basliyor...")
        print("=" * 50)
        
        discovered_endpoints = []
        
        for base_url in self.possible_urls:
            print(f"\nTesting base URL: {base_url}")
            
            for endpoint in self.common_endpoints:
                full_url = base_url + endpoint
                try:
                    response = requests.get(full_url, headers=self.headers, timeout=5, verify=False)
                    
                    if response.status_code == 200:
                        print(f"SUCCESS {full_url} - Status: {response.status_code}")
                        discovered_endpoints.append({
                            'url': full_url,
                            'status': response.status_code,
                            'response': response.text[:200] + "..." if len(response.text) > 200 else response.text
                        })
                    elif response.status_code == 401:
                        print(f"AUTH {full_url} - Unauthorized (API Key gerekli)")
                    elif response.status_code == 404:
                        print(f"NOT FOUND {full_url} - Not Found")
                    else:
                        print(f"OTHER {full_url} - Status: {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"ERROR {full_url} - Connection Error: {str(e)[:50]}")
        
        return discovered_endpoints
    
    def test_specific_endpoints(self, base_url: str):
        """Belirli bir base URL icin detayli test"""
        print(f"\nDetayli Test: {base_url}")
        print("=" * 50)
        
        # Test edilecek endpoint'ler
        test_endpoints = [
            '/api/sales/today',
            '/api/sales/yesterday',
            '/api/sales/week',
            '/api/products/all',
            '/api/stock/current',
            '/api/reports/daily',
            '/api/orders/today',
            '/api/transactions/today',
            '/api/health',
            '/api/status',
            '/api/info'
        ]
        
        for endpoint in test_endpoints:
            full_url = base_url + endpoint
            try:
                response = requests.get(full_url, headers=self.headers, timeout=5, verify=False)
                
                if response.status_code == 200:
                    print(f"SUCCESS {endpoint}")
                    try:
                        data = response.json()
                        print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    except:
                        print(f"   Response: {response.text[:100]}...")
                else:
                    print(f"FAILED {endpoint} - Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"ERROR {endpoint} - Error: {str(e)[:50]}")
    
    def test_post_endpoints(self, base_url: str):
        """POST endpoint'lerini test et"""
        print(f"\n📤 POST Endpoint Test: {base_url}")
        print("=" * 50)
        
        test_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'test': True
        }
        
        post_endpoints = [
            '/api/sales/query',
            '/api/reports/generate',
            '/api/data/export',
            '/api/query'
        ]
        
        for endpoint in post_endpoints:
            full_url = base_url + endpoint
            try:
                response = requests.post(full_url, json=test_data, headers=self.headers, timeout=5, verify=False)
                
                if response.status_code in [200, 201]:
                    print(f"✅ {endpoint} - Status: {response.status_code}")
                    try:
                        data = response.json()
                        print(f"   📊 Response: {data}")
                    except:
                        print(f"   📄 Response: {response.text[:100]}...")
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"🚫 {endpoint} - Error: {str(e)[:50]}")

def main():
    print("YAZAR KASA LINK API Test Araci")
    print("=" * 50)
    
    # API Key'i environment dosyasından oku
    api_key = os.getenv('YAZAR_KASA_API_KEY')
    
    if not api_key:
        print("API Key bulunamadi! .env dosyasinda YAZAR_KASA_API_KEY tanimlayin.")
        return
    
    print(f"API Key bulundu: {api_key[:10]}...")
    
    tester = YazarKasaAPITester(api_key)
    
    # 1. API Kefsi
    discovered = tester.test_api_discovery()
    
    if discovered:
        print(f"\n{len(discovered)} endpoint kesfedildi!")
        
        # 2. En basarili base URL icin detayli test
        best_url = discovered[0]['url'].split('/api')[0] if '/api' in discovered[0]['url'] else discovered[0]['url']
        tester.test_specific_endpoints(best_url)
        tester.test_post_endpoints(best_url)
        
        # 3. Sonuclari kaydet
        with open('yazar_kasa_discovery.json', 'w', encoding='utf-8') as f:
            json.dump(discovered, f, indent=2, ensure_ascii=False)
        
        print(f"\nKefis sonuclari 'yazar_kasa_discovery.json' dosyasina kaydedildi")
    else:
        print("\nHicbir endpoint kesfedilemedi. API Key'i kontrol edin.")

if __name__ == "__main__":
    main()
