"""
YAZAR KASA LİNK Veritabanı Keşif ve Bağlantı Aracı
"""

import os
import socket
import sqlite3
import pymysql
import psycopg2
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

class YazarKasaDBDiscovery:
    def __init__(self):
        self.host = "192.168.1.187"
        self.common_db_ports = [3306, 5432, 1433, 1521, 3050]  # MySQL, PostgreSQL, SQL Server, Oracle, Firebird
        self.discovered_databases = []
    
    def scan_database_ports(self):
        """Veritabanı port'larını tara"""
        print("YAZAR KASA LİNK Veritabanı Port Tarama")
        print("=" * 50)
        
        open_db_ports = []
        
        for port in self.common_db_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.host, port))
                
                if result == 0:
                    db_type = self.get_db_type_by_port(port)
                    print(f"OPEN Port {port}: {db_type}")
                    open_db_ports.append((port, db_type))
                else:
                    db_type = self.get_db_type_by_port(port)
                    print(f"CLOSED Port {port}: {db_type}")
                    
                sock.close()
                
            except Exception as e:
                print(f"ERROR Port {port}: {str(e)[:30]}")
        
        return open_db_ports
    
    def get_db_type_by_port(self, port):
        """Port numarasına göre veritabanı tipini belirle"""
        db_types = {
            3306: "MySQL",
            5432: "PostgreSQL", 
            1433: "SQL Server",
            1521: "Oracle",
            3050: "Firebird",
            6379: "Redis",
            27017: "MongoDB"
        }
        return db_types.get(port, "Unknown")
    
    def test_mysql_connection(self, port=3306):
        """MySQL bağlantısını test et"""
        print(f"\nMySQL Bağlantı Testi (Port {port})")
        print("-" * 30)
        
        # Yaygın MySQL kullanıcı adları ve şifreler
        test_credentials = [
            ("root", ""),
            ("root", "root"),
            ("root", "password"),
            ("admin", ""),
            ("admin", "admin"),
            ("yazarkasa", ""),
            ("yazarkasa", "yazarkasa"),
            ("pos", ""),
            ("pos", "pos"),
            ("kasa", ""),
            ("kasa", "kasa")
        ]
        
        for username, password in test_credentials:
            try:
                connection = pymysql.connect(
                    host=self.host,
                    port=port,
                    user=username,
                    password=password,
                    connect_timeout=5
                )
                
                print(f"SUCCESS: {username}/{password}")
                
                # Veritabanlarını listele
                cursor = connection.cursor()
                cursor.execute("SHOW DATABASES")
                databases = cursor.fetchall()
                
                print("Available Databases:")
                for db in databases:
                    print(f"  - {db[0]}")
                
                # Tabloları listele
                for db in databases:
                    if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']:
                        cursor.execute(f"USE {db[0]}")
                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()
                        
                        print(f"\nDatabase: {db[0]}")
                        print("Tables:")
                        for table in tables:
                            print(f"  - {table[0]}")
                
                connection.close()
                return True, username, password, databases
                
            except Exception as e:
                print(f"FAILED: {username}/{password} - {str(e)[:50]}")
        
        return False, None, None, None
    
    def test_postgresql_connection(self, port=5432):
        """PostgreSQL bağlantısını test et"""
        print(f"\nPostgreSQL Bağlantı Testi (Port {port})")
        print("-" * 30)
        
        test_credentials = [
            ("postgres", ""),
            ("postgres", "postgres"),
            ("postgres", "password"),
            ("admin", ""),
            ("admin", "admin"),
            ("yazarkasa", ""),
            ("yazarkasa", "yazarkasa")
        ]
        
        for username, password in test_credentials:
            try:
                connection = psycopg2.connect(
                    host=self.host,
                    port=port,
                    user=username,
                    password=password,
                    connect_timeout=5
                )
                
                print(f"SUCCESS: {username}/{password}")
                
                cursor = connection.cursor()
                cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
                databases = cursor.fetchall()
                
                print("Available Databases:")
                for db in databases:
                    print(f"  - {db[0]}")
                
                connection.close()
                return True, username, password, databases
                
            except Exception as e:
                print(f"FAILED: {username}/{password} - {str(e)[:50]}")
        
        return False, None, None, None
    
    def test_sqlite_files(self):
        """SQLite dosyalarını ara"""
        print(f"\nSQLite Dosya Arama")
        print("-" * 30)
        
        # YAZAR KASA LİNK'in muhtemel SQLite dosya konumları
        possible_paths = [
            "\\\\192.168.1.187\\c$\\Program Files\\YazarKasa\\data\\",
            "\\\\192.168.1.187\\c$\\Program Files (x86)\\YazarKasa\\data\\",
            "\\\\192.168.1.187\\c$\\Users\\Public\\YazarKasa\\",
            "\\\\192.168.1.187\\c$\\YazarKasa\\",
        ]
        
        sqlite_files = []
        
        for path in possible_paths:
            try:
                # Network path kontrolü
                if os.path.exists(path):
                    print(f"FOUND: {path}")
                    for file in os.listdir(path):
                        if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
                            full_path = os.path.join(path, file)
                            print(f"  SQLite: {full_path}")
                            sqlite_files.append(full_path)
                else:
                    print(f"NOT FOUND: {path}")
            except Exception as e:
                print(f"ERROR: {path} - {str(e)[:50]}")
        
        return sqlite_files
    
    def analyze_sqlite_database(self, db_path):
        """SQLite veritabanını analiz et"""
        print(f"\nSQLite Analiz: {db_path}")
        print("-" * 40)
        
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            
            # Tabloları listele
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("Tables:")
            for table in tables:
                table_name = table[0]
                print(f"  - {table_name}")
                
                # Tablo yapısını göster
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"    Columns:")
                for col in columns:
                    print(f"      {col[1]} ({col[2]})")
                
                # Kayıt sayısını göster
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    Records: {count}")
                
                # İlk birkaç kaydı göster
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_data = cursor.fetchall()
                    print(f"    Sample Data:")
                    for row in sample_data:
                        print(f"      {row}")
                print()
            
            connection.close()
            return tables
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return []
    
    def create_connection_config(self, db_type, host, port, username, password, database=None):
        """Bağlantı konfigürasyonu oluştur"""
        config = {
            "db_type": db_type,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": database,
            "discovered_at": datetime.now().isoformat()
        }
        
        with open('yazar_kasa_db_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Database config saved to 'yazar_kasa_db_config.json'")
        return config

def main():
    discovery = YazarKasaDBDiscovery()
    
    print("YAZAR KASA LİNK Veritabanı Keşif Aracı")
    print("=" * 50)
    
    # 1. Port tarama
    open_ports = discovery.scan_database_ports()
    
    # 2. Açık port'larda veritabanı bağlantısı test et
    for port, db_type in open_ports:
        if db_type == "MySQL":
            success, username, password, databases = discovery.test_mysql_connection(port)
            if success:
                config = discovery.create_connection_config(
                    "MySQL", discovery.host, port, username, password
                )
                break
        elif db_type == "PostgreSQL":
            success, username, password, databases = discovery.test_postgresql_connection(port)
            if success:
                config = discovery.create_connection_config(
                    "PostgreSQL", discovery.host, port, username, password
                )
                break
    
    # 3. SQLite dosyalarını ara
    sqlite_files = discovery.test_sqlite_files()
    
    # 4. SQLite dosyalarını analiz et
    for sqlite_file in sqlite_files:
        discovery.analyze_sqlite_database(sqlite_file)
    
    print(f"\n{'='*50}")
    print("SONUÇ:")
    if open_ports:
        print(f"Açık veritabanı port'ları: {[p[0] for p in open_ports]}")
    if sqlite_files:
        print(f"Bulunan SQLite dosyaları: {sqlite_files}")
    
    if not open_ports and not sqlite_files:
        print("Hiçbir veritabanı bulunamadı!")
        print("\nAlternatif yöntemler:")
        print("1. YAZAR KASA LİNK yazılımının ayarlarını kontrol edin")
        print("2. Veritabanı bağlantı bilgilerini manuel olarak öğrenin")
        print("3. Network dosya paylaşımını kontrol edin")

if __name__ == "__main__":
    main()
