import socket
import requests
from datetime import datetime

def scan_ports():
    """YAZAR KASA LİNK için yaygın port'ları tara"""
    print("YAZAR KASA LİNK Port Tarama")
    print("=" * 40)
    
    host = "192.168.1.187"
    
    # Yaygın port'lar
    common_ports = [
        4568, 8080, 8000, 3000, 5000, 9000,  # Web servisleri
        80, 443, 8081, 8082, 8083,           # HTTP/HTTPS
        3306, 5432, 1433,                    # Veritabanları
        22, 21, 23, 25, 110, 143, 993, 995   # Diğer servisler
    ]
    
    open_ports = []
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            
            if result == 0:
                print(f"OPEN Port {port}: ACIK")
                open_ports.append(port)
                
                # HTTP servis test et
                try:
                    response = requests.get(f"http://{host}:{port}", timeout=3)
                    print(f"   HTTP Status: {response.status_code}")
                    print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                except:
                    try:
                        response = requests.get(f"https://{host}:{port}", timeout=3, verify=False)
                        print(f"   HTTPS Status: {response.status_code}")
                    except:
                        print(f"   HTTP/HTTPS test basarisiz")
            else:
                print(f"CLOSED Port {port}: KAPALI")
                
            sock.close()
            
        except Exception as e:
            print(f"ERROR Port {port}: HATA - {str(e)[:30]}")
    
    print(f"\n{'='*40}")
    print(f"SONUÇ: {len(open_ports)} port açık")
    if open_ports:
        print(f"Açık port'lar: {open_ports}")
        print("\nYAZAR KASA LİNK muhtemelen şu port'lardan birinde:")
        for port in open_ports:
            if port in [4568, 8080, 8000, 3000, 5000, 9000]:
                print(f"  - http://{host}:{port}")
    else:
        print("Hiçbir port açık değil!")
        print("YAZAR KASA LİNK çalışmıyor olabilir.")
    
    return open_ports

def test_http_endpoints(host, ports):
    """Açık port'larda HTTP endpoint'lerini test et"""
    print(f"\nHTTP Endpoint Testi")
    print("=" * 30)
    
    test_endpoints = ['/', '/api', '/health', '/status', '/info']
    
    for port in ports:
        if port in [80, 443, 8080, 8000, 3000, 5000, 9000, 4568]:
            print(f"\nPort {port} için endpoint testi:")
            
            for endpoint in test_endpoints:
                for protocol in ['http', 'https']:
                    url = f"{protocol}://{host}:{port}{endpoint}"
                    try:
                        response = requests.get(url, timeout=3, verify=False)
                        print(f"  SUCCESS {url} - Status: {response.status_code}")
                        if response.status_code == 200:
                            print(f"     Content: {response.text[:100]}...")
                    except:
                        pass

if __name__ == "__main__":
    open_ports = scan_ports()
    if open_ports:
        test_http_endpoints("192.168.1.187", open_ports)
