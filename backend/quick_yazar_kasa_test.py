import requests
import json
import os
from dotenv import load_dotenv
import urllib3

# SSL uyarılarını devre dışı bırak
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Environment dosyasını yükle
load_dotenv()

def quick_test():
    print("YAZAR KASA LINK Hizli Test")
    print("=" * 40)
    
    # API Key ve URL'i al
    api_key = os.getenv('YAZAR_KASA_API_KEY')
    base_url = os.getenv('YAZAR_KASA_BASE_URL', 'http://192.168.1.187:4568')
    
    if not api_key:
        print("HATA: API Key bulunamadi!")
        return
    
    print(f"API Key: {api_key[:10]}...")
    print(f"Base URL: {base_url}")
    
    # Headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Test endpoint'leri
    test_endpoints = [
        '/',
        '/api',
        '/api/v1',
        '/health',
        '/status',
        '/info'
    ]
    
    print("\nTest endpoint'leri:")
    print("-" * 40)
    
    for endpoint in test_endpoints:
        full_url = base_url + endpoint
        try:
            print(f"Testing: {full_url}")
            response = requests.get(full_url, headers=headers, timeout=10, verify=False)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print("  SUCCESS!")
                try:
                    data = response.json()
                    print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                    print(f"  Sample: {str(data)[:100]}...")
                except:
                    print(f"  Response: {response.text[:100]}...")
            elif response.status_code == 401:
                print("  AUTH REQUIRED (API Key gerekli)")
            elif response.status_code == 404:
                print("  NOT FOUND")
            else:
                print(f"  OTHER: {response.text[:50]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"  ERROR: {str(e)[:50]}")
        
        print()

if __name__ == "__main__":
    quick_test()
