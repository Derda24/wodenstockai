"""
Supabase sales_history tablosu sütunlarını kontrol et
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'services'))

from supabase_service import SupabaseService

def check_supabase_columns():
    """Supabase sales_history tablosu sütunlarını kontrol et"""
    print("Supabase sales_history Tablo Kontrolü")
    print("=" * 50)
    
    try:
        supabase = SupabaseService()
        
        # Tablo yapısını kontrol et
        print("Mevcut sütunları kontrol ediliyor...")
        
        # Örnek bir kayıt al
        result = supabase.client.table("sales_history").select("*").limit(1).execute()
        
        if result.data:
            print("Mevcut sütunlar:")
            for key in result.data[0].keys():
                print(f"  - {key}")
            
            # transaction_id sütunu var mı kontrol et
            if 'transaction_id' in result.data[0]:
                print("\n✅ transaction_id sütunu mevcut!")
            else:
                print("\n❌ transaction_id sütunu eksik!")
                print("Eklenmesi gereken sütunlar:")
                print("  - transaction_id (text)")
                print("  - order_no (text)")
                
        else:
            print("Tabloda veri bulunamadı, yeni sütunlar eklenebilir")
            
    except Exception as e:
        print(f"Kontrol hatası: {str(e)}")

if __name__ == "__main__":
    check_supabase_columns()
