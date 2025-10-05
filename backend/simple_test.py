import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def simple_test():
    print("YAZAR KASA LINK Basit Test")
    print("=" * 30)
    
    # Manuel URL ve API Key
    base_url = "http://192.168.1.187:4568"  # HTTP kullan
    api_key = os.getenv('YAZAR_KASA_API_KEY')
    
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10] if api_key else 'YOK'}...")
    
    if not api_key:
        print("API Key bulunamadi!")
        return
    
    # Headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Sadece ana endpoint'i test et
    test_urls = [
        base_url,
        f"{base_url}/api",
        f"{base_url}/health",
        f"{base_url}/status"
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print("  SUCCESS!")
                try:
                    data = response.json()
                    print(f"  JSON Response: {data}")
                except:
                    print(f"  Text Response: {response.text[:200]}")
            else:
                print(f"  Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"  ERROR: {str(e)}")

if __name__ == "__main__":
    simple_test()
