"""
Adisyon API Test Aracı (Port 4567)
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def test_adisyon_api():
    """Adisyon API'sini test et"""
    print("Adisyon API Test Aracı (Port 4567)")
    print("=" * 50)
    
    base_url = "http://192.168.1.187:4567"
    api_key = os.getenv('YAZAR_KASA_API_KEY')
    serial_number = os.getenv('YAZAR_KASA_SERIAL_NUMBER')
    
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10] if api_key else 'None'}...")
    print(f"Serial Number: {serial_number}")
    
    # Farklı header kombinasyonları
    header_combinations = [
        # Sadece API Key
        {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        # API Key + Serial Number
        {
            'Authorization': f'Bearer {api_key}',
            'X-Serial-Number': serial_number,
            'Content-Type': 'application/json'
        },
        # API Key header
        {
            'API-Key': api_key,
            'Content-Type': 'application/json'
        },
        # API Key + Serial Number farklı format
        {
            'API-Key': api_key,
            'Serial-Number': serial_number,
            'Content-Type': 'application/json'
        },
        # Query parameter olarak
        {
            'Content-Type': 'application/json'
        }
    ]
    
    # Test endpoint'leri
    test_endpoints = [
        '',
        '/',
        '/api',
        '/api/v1',
        '/api/v2',
        '/health',
        '/status',
        '/info',
        '/auth',
        '/login',
        '/sales',
        '/transactions',
        '/reports',
        '/data',
        '/export',
        '/import',
        '/sync',
        '/adisyon',
        '/pos',
        '/kasa',
        '/yazarkasa'
    ]
    
    successful_endpoints = []
    
    print(f"\nTest edilecek {len(header_combinations)} header kombinasyonu ve {len(test_endpoints)} endpoint")
    print("=" * 60)
    
    for i, headers in enumerate(header_combinations):
        print(f"\n--- Header Kombinasyonu {i+1} ---")
        print(f"Headers: {headers}")
        
        for endpoint in test_endpoints:
            full_url = base_url + endpoint
            
            # Query parameter test (sadece son kombinasyon için)
            if i == 4 and api_key:  # Son kombinasyon
                full_url += f"?api_key={api_key}"
                if serial_number:
                    full_url += f"&serial={serial_number}"
            
            try:
                print(f"  Testing: {full_url}")
                response = requests.get(full_url, headers=headers, timeout=5, verify=False)
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("    SUCCESS!")
                    try:
                        data = response.json()
                        print(f"    JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                        print(f"    Sample: {str(data)[:150]}...")
                        successful_endpoints.append({
                            'url': full_url,
                            'headers': headers,
                            'response': data
                        })
                    except:
                        print(f"    Text: {response.text[:150]}...")
                        successful_endpoints.append({
                            'url': full_url,
                            'headers': headers,
                            'response': response.text
                        })
                elif response.status_code == 401:
                    print("    AUTH REQUIRED")
                elif response.status_code == 403:
                    print("    FORBIDDEN")
                elif response.status_code == 404:
                    print("    NOT FOUND")
                else:
                    print(f"    Other: {response.text[:50]}...")
                    
            except Exception as e:
                print(f"    ERROR: {str(e)[:80]}")
    
    # Sonuçları özetle
    print(f"\n{'='*60}")
    print(f"TEST SONUÇLARI")
    print(f"{'='*60}")
    
    if successful_endpoints:
        print(f"SUCCESS: {len(successful_endpoints)} başarılı endpoint bulundu!")
        for endpoint in successful_endpoints:
            print(f"  - {endpoint['url']}")
            print(f"    Headers: {endpoint['headers']}")
    else:
        print("BAŞARISIZ: Hiçbir endpoint çalışmıyor.")
        print("\nOlası nedenler:")
        print("- API Key yanlış")
        print("- Serial Number yanlış")
        print("- Farklı authentication yöntemi gerekli")
        print("- API dokümantasyonu gerekli")
    
    # Sonuçları dosyaya kaydet
    with open('adisyon_api_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'successful_endpoints': successful_endpoints,
            'api_key': api_key[:10] + "..." if api_key else None,
            'serial_number': serial_number,
            'base_url': base_url,
            'test_date': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetaylı sonuçlar 'adisyon_api_test_results.json' dosyasına kaydedildi.")
    
    return successful_endpoints

def test_post_endpoints():
    """POST endpoint'lerini test et"""
    print(f"\nPOST Endpoint Testi")
    print("=" * 30)
    
    base_url = "http://192.168.1.187:4567"
    api_key = os.getenv('YAZAR_KASA_API_KEY')
    serial_number = os.getenv('YAZAR_KASA_SERIAL_NUMBER')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'X-Serial-Number': serial_number,
        'Content-Type': 'application/json'
    }
    
    test_data = {
        'test': True,
        'date': datetime.now().isoformat(),
        'serial_number': serial_number
    }
    
    post_endpoints = [
        '/api/sales/query',
        '/api/reports/generate',
        '/api/data/export',
        '/api/query',
        '/api/sync',
        '/api/import'
    ]
    
    for endpoint in post_endpoints:
        full_url = base_url + endpoint
        try:
            response = requests.post(full_url, json=test_data, headers=headers, timeout=5, verify=False)
            
            if response.status_code in [200, 201]:
                print(f"SUCCESS {endpoint} - Status: {response.status_code}")
                try:
                    data = response.json()
                    print(f"   Response: {data}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"FAILED {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR {endpoint} - Error: {str(e)[:50]}")

if __name__ == "__main__":
    successful_endpoints = test_adisyon_api()
    test_post_endpoints()
