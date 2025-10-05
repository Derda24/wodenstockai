import requests
import json
import os
from dotenv import load_dotenv
import urllib3

# SSL uyarılarını devre dışı bırak
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Environment dosyasını yükle
load_dotenv()

def full_yazar_kasa_test():
    print("YAZAR KASA LINK Tam Test")
    print("=" * 40)
    
    # API Key, Serial Number ve URL'i al
    api_key = os.getenv('YAZAR_KASA_API_KEY')
    serial_number = os.getenv('YAZAR_KASA_SERIAL_NUMBER')
    base_url = os.getenv('YAZAR_KASA_BASE_URL', 'http://192.168.1.187:4568')
    
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10] if api_key else 'YOK'}...")
    print(f"Serial Number: {serial_number if serial_number else 'YOK'}")
    
    if not api_key:
        print("HATA: API Key bulunamadi!")
        return
    
    # Farklı header kombinasyonları test et
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
        '/health',
        '/status',
        '/info',
        '/auth',
        '/login'
    ]
    
    print(f"\nTest edilecek {len(header_combinations)} header kombinasyonu ve {len(test_endpoints)} endpoint")
    print("=" * 60)
    
    successful_connections = []
    
    for i, headers in enumerate(header_combinations):
        print(f"\n--- Header Kombinasyonu {i+1} ---")
        print(f"Headers: {headers}")
        
        for endpoint in test_endpoints:
            full_url = base_url + endpoint
            
            # Query parameter test (sadece ilk kombinasyon için)
            if i == 4 and api_key:  # Son kombinasyon
                full_url += f"?api_key={api_key}"
                if serial_number:
                    full_url += f"&serial={serial_number}"
            
            try:
                print(f"  Testing: {full_url}")
                response = requests.get(full_url, headers=headers, timeout=10, verify=False)
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("    SUCCESS!")
                    try:
                        data = response.json()
                        print(f"    JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                        print(f"    Sample: {str(data)[:150]}...")
                        successful_connections.append({
                            'url': full_url,
                            'headers': headers,
                            'response': data
                        })
                    except:
                        print(f"    Text: {response.text[:150]}...")
                        successful_connections.append({
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
                    
            except requests.exceptions.RequestException as e:
                print(f"    ERROR: {str(e)[:80]}")
    
    # Sonuçları özetle
    print(f"\n{'='*60}")
    print(f"TEST SONUÇLARI")
    print(f"{'='*60}")
    
    if successful_connections:
        print(f"SUCCESS: {len(successful_connections)} başarılı bağlantı bulundu!")
        for conn in successful_connections:
            print(f"  - {conn['url']}")
            print(f"    Headers: {conn['headers']}")
    else:
        print("BAŞARISIZ: Hiçbir bağlantı kurulamadı.")
        print("\nOlası nedenler:")
        print("- YAZAR KASA LİNK yazılımı çalışmıyor")
        print("- Yanlış IP adresi veya port")
        print("- Firewall engeli")
        print("- API Key veya Serial Number hatalı")
        print("- Farklı authentication yöntemi gerekli")
    
    # Sonuçları dosyaya kaydet
    with open('yazar_kasa_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'successful_connections': successful_connections,
            'api_key': api_key[:10] + "..." if api_key else None,
            'serial_number': serial_number,
            'base_url': base_url
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetaylı sonuçlar 'yazar_kasa_test_results.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    full_yazar_kasa_test()
