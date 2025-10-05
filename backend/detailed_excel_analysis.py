"""
DARA Excel Dosyası Detaylı Analizi
"""

import pandas as pd
import json
from datetime import datetime

def detailed_excel_analysis():
    """Excel dosyasını detaylı analiz et"""
    print("DARA Excel Dosyası Detaylı Analizi")
    print("=" * 50)
    
    try:
        # Excel dosyasını oku
        df = pd.read_excel("5.10.2025.xls", header=None)
        
        print(f"Toplam satır: {len(df)}")
        print(f"Toplam sütun: {len(df.columns)}")
        
        # İlk 20 satırı göster
        print("\nİlk 20 satır:")
        print("-" * 80)
        for i in range(min(20, len(df))):
            row_data = []
            for j in range(min(10, len(df.columns))):  # İlk 10 sütun
                cell_value = df.iloc[i, j]
                if pd.isna(cell_value):
                    row_data.append("[BOŞ]")
                else:
                    row_data.append(str(cell_value)[:20])  # İlk 20 karakter
            print(f"Satır {i:2d}: {' | '.join(row_data)}")
        
        # Satış verilerini bul
        print("\nSatış Verilerini Bulma:")
        print("-" * 40)
        
        # Başlık satırını bul
        header_row = None
        for i in range(len(df)):
            row_values = df.iloc[i].astype(str).tolist()
            if any('ÜRÜN' in val.upper() or 'PRODUCT' in val.upper() for val in row_values):
                header_row = i
                break
        
        if header_row is not None:
            print(f"Başlık satırı bulundu: {header_row}")
            
            # Başlık satırından sonraki verileri al
            sales_data = df.iloc[header_row+1:].copy()
            
            # Boş satırları temizle
            sales_data = sales_data.dropna(how='all')
            
            print(f"Satış verisi satır sayısı: {len(sales_data)}")
            
            if len(sales_data) > 0:
                print("\nİlk 10 satış verisi:")
                print("-" * 80)
                for i in range(min(10, len(sales_data))):
                    row_data = []
                    for j in range(min(8, len(sales_data.columns))):
                        cell_value = sales_data.iloc[i, j]
                        if pd.isna(cell_value):
                            row_data.append("[BOŞ]")
                        else:
                            row_data.append(str(cell_value)[:15])
                    print(f"Satır {i:2d}: {' | '.join(row_data)}")
                
                # Sütun analizi
                print(f"\nSütun Analizi:")
                print("-" * 40)
                
                # Her sütunu analiz et
                for col_idx in range(min(8, len(sales_data.columns))):
                    col_data = sales_data.iloc[:, col_idx].dropna()
                    if len(col_data) > 0:
                        print(f"Sütun {col_idx}:")
                        print(f"  Dolu satır sayısı: {len(col_data)}")
                        
                        # Veri tipini tahmin et
                        sample_values = col_data.head(5).tolist()
                        print(f"  Örnek değerler: {sample_values}")
                        
                        # Sayısal veri kontrolü
                        numeric_count = 0
                        for val in col_data:
                            try:
                                float(str(val))
                                numeric_count += 1
                            except:
                                pass
                        
                        if numeric_count > len(col_data) * 0.8:
                            print(f"  → Sayısal sütun (muhtemelen miktar/fiyat)")
                        elif numeric_count == 0:
                            print(f"  → Metin sütun (muhtemelen ürün adı)")
                        else:
                            print(f"  → Karışık sütun")
                
                # Satış verisi formatını tahmin et
                print(f"\nSatış Verisi Format Tahmini:")
                print("-" * 40)
                
                # En çok dolu olan sütunları bul
                column_fill_rates = []
                for col_idx in range(len(sales_data.columns)):
                    col_data = sales_data.iloc[:, col_idx]
                    fill_rate = len(col_data.dropna()) / len(col_data)
                    column_fill_rates.append((col_idx, fill_rate))
                
                # En dolu sütunları sırala
                column_fill_rates.sort(key=lambda x: x[1], reverse=True)
                
                print("Sütun doldurma oranları:")
                for col_idx, fill_rate in column_fill_rates[:8]:
                    print(f"  Sütun {col_idx}: {fill_rate:.2%}")
                
                # Muhtemel sütun eşleştirmesi
                print(f"\nMuhtemel Sütun Eşleştirmesi:")
                print("-" * 40)
                
                suggestions = {}
                
                # Ürün adı sütunu (en çok metin içeren)
                text_columns = []
                for col_idx in range(len(sales_data.columns)):
                    col_data = sales_data.iloc[:, col_idx].dropna()
                    if len(col_data) > 0:
                        text_count = 0
                        for val in col_data:
                            if not str(val).replace('.', '').replace(',', '').replace('-', '').isdigit():
                                text_count += 1
                        
                        if text_count > len(col_data) * 0.7:
                            text_columns.append((col_idx, text_count))
                
                if text_columns:
                    text_columns.sort(key=lambda x: x[1], reverse=True)
                    suggestions['product'] = text_columns[0][0]
                    print(f"  Ürün Adı: Sütun {text_columns[0][0]}")
                
                # Miktar sütunu (sayısal, orta değerler)
                numeric_columns = []
                for col_idx in range(len(sales_data.columns)):
                    col_data = sales_data.iloc[:, col_idx].dropna()
                    if len(col_data) > 0:
                        numeric_count = 0
                        numeric_values = []
                        for val in col_data:
                            try:
                                num_val = float(str(val))
                                numeric_count += 1
                                numeric_values.append(num_val)
                            except:
                                pass
                        
                        if numeric_count > len(col_data) * 0.8 and numeric_values:
                            avg_value = sum(numeric_values) / len(numeric_values)
                            numeric_columns.append((col_idx, numeric_count, avg_value))
                
                if numeric_columns:
                    # Miktar için orta değerli sütunları seç
                    quantity_candidates = [col for col in numeric_columns if 0.1 <= col[2] <= 100]
                    if quantity_candidates:
                        suggestions['quantity'] = quantity_candidates[0][0]
                        print(f"  Miktar: Sütun {quantity_candidates[0][0]} (ortalama: {quantity_candidates[0][2]:.2f})")
                    
                    # Fiyat için yüksek değerli sütunları seç
                    price_candidates = [col for col in numeric_columns if col[2] > 10]
                    if price_candidates:
                        suggestions['price'] = price_candidates[0][0]
                        print(f"  Fiyat: Sütun {price_candidates[0][0]} (ortalama: {price_candidates[0][2]:.2f})")
                
                # Sonuçları kaydet
                analysis_result = {
                    "file_name": "5.10.2025.xls",
                    "analysis_date": datetime.now().isoformat(),
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "header_row": header_row,
                    "sales_data_rows": len(sales_data),
                    "column_suggestions": suggestions,
                    "sample_data": sales_data.head(5).to_dict('records') if len(sales_data) > 0 else []
                }
                
                with open('dara_excel_detailed_analysis.json', 'w', encoding='utf-8') as f:
                    json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"\nDetaylı analiz 'dara_excel_detailed_analysis.json' dosyasına kaydedildi")
                
                return analysis_result
        
        else:
            print("Başlık satırı bulunamadı!")
            return None
            
    except Exception as e:
        print(f"Analiz hatası: {str(e)}")
        return None

if __name__ == "__main__":
    detailed_excel_analysis()
