"""
DARA Excel Dosyası Otomatik İşleyici
5.10.2025.xls formatını analiz edip Supabase'e kaydeder
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class DaraExcelProcessor:
    def __init__(self, supabase_service):
        self.supabase = supabase_service
        self.date_from_file = None  # Dosya adından tarih çıkar
        
    def _normalize_text(self, text: str) -> str:
        """Turkce karakter ve bazi ekleri normalize et, parantez/ek aciklamalari kaldir."""
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        base = text.strip()
        # Parantez ve sonrasini temizle: "Latte (Soguk)" -> "Latte"
        import re
        base = re.split(r"[\(\[]", base, maxsplit=1)[0].strip()
        # Asiri bosluklari tek bosluga indir
        base = re.sub(r"\s+", " ", base)
        # Turkce karakterleri ascii'ye cikar
        mapping = {
            'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
            'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S',
            'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C',
            'i̇': 'i', 'ï': 'i', 'ü': 'u', 'ö': 'o', 'ç': 'c', 'ş': 's', 'ğ': 'g'
        }
        normalized = base
        for k, v in mapping.items():
            normalized = normalized.replace(k, v)
        return normalized.strip()
        
    def process_dara_excel(self, file_path: str) -> Dict[str, Any]:
        """DARA Excel dosyasını işle ve Supabase'e kaydet"""
        try:
            print(f"DARA Excel işleniyor: {file_path}")
            
            # Dosya adından tarih çıkar
            self.date_from_file = self.extract_date_from_filename(file_path)
            
            # Excel dosyasını oku
            df = pd.read_excel(file_path, header=None)
            
            # Satış verilerini bul ve işle
            sales_data = self.find_and_extract_sales_data(df)
            
            if sales_data.empty:
                return {
                    "success": False,
                    "error": "No sales data found in Excel file"
                }
            
            # Veri temizleme ve dönüştürme
            processed_data = self.clean_and_convert_data(sales_data)
            
            if not processed_data:
                return {
                    "success": False,
                    "error": "No data could be processed"
                }
            
            # Excel'den ek analiz verilerini çıkar (grafik, demografik bilgiler)
            analysis_data = self.extract_analysis_data(df)
            
            # Stok güncellemelerini uygula (reçete/ürün bazlı düşüm)
            stock_update_result = self.update_stock_from_processed(processed_data)
            mapping_diagnostics = self.suggest_name_mappings(processed_data)
            
            # Analiz verilerini processed_data'ya ekle
            for data in processed_data:
                data["analysis_data"] = json.dumps(analysis_data)
            
            # Supabase'e kaydet
            result = self.save_to_supabase(processed_data)
            
            return {
                "success": True,
                "processed_count": len(processed_data),
                "saved_count": result.get("saved_count", 0),
                "errors": result.get("errors", []),
                "date": self.date_from_file,
                "stock_updates": stock_update_result,
                "analysis_data": analysis_data,  # Yeni: Analiz verileri
                "message": f"DARA Excel isleme tamamlandi: {len(processed_data)} kayit, stok guncelleme denemesi: {stock_update_result.get('attempted', 0)}, basari: {stock_update_result.get('updated', 0)}",
                "mapping": mapping_diagnostics
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_analysis_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Excel'den satış analizi için ek veriler çıkar (grafik, demografik bilgiler)"""
        analysis_data = {
            "sales_summary": {},
            "top_products": [],
            "demographics": {},
            "sales_chart": [],
            "category_breakdown": {}
        }
        
        try:
            # Excel'deki tüm veriyi string olarak oku
            df_str = df.astype(str)
            
            # Satış raporu başlığını ara
            report_title_row = None
            for idx, row in df_str.iterrows():
                if "SATIŞ RAPORU" in str(row.values) or "SATIS RAPORU" in str(row.values):
                    report_title_row = idx
                    break
            
            if report_title_row is not None:
                # Tarih aralığı bilgisini çıkar
                for idx in range(report_title_row, min(report_title_row + 10, len(df))):
                    row_text = " ".join(str(cell) for cell in df_str.iloc[idx].values if str(cell) != 'nan')
                    if "Tarih Aralığı" in row_text or "Tarih Araligi" in row_text:
                        analysis_data["sales_summary"]["date_range"] = row_text
                        break
                
                # Şirket adını çıkar
                for idx in range(report_title_row, min(report_title_row + 10, len(df))):
                    row_text = " ".join(str(cell) for cell in df_str.iloc[idx].values if str(cell) != 'nan')
                    if "WODEN" in row_text.upper() or "COFFEE" in row_text.upper():
                        analysis_data["sales_summary"]["company"] = row_text.strip()
                        break
            
            # GENEL YEKUN (Grand Total) satırını ara
            grand_total_row = None
            for idx, row in df_str.iterrows():
                if "GENEL YEKUN" in str(row.values) or "GENEL TOPLAM" in str(row.values):
                    grand_total_row = idx
                    break
            
            if grand_total_row is not None:
                # Toplam miktar ve tutar bilgilerini çıkar
                total_row = df_str.iloc[grand_total_row]
                for i, cell in enumerate(total_row):
                    if str(cell) != 'nan' and str(cell).replace('.', '').isdigit():
                        if i == 1:  # Miktar
                            analysis_data["sales_summary"]["total_quantity"] = float(str(cell))
                        elif i == 2:  # Tutar
                            analysis_data["sales_summary"]["total_amount"] = float(str(cell))
            
            # Demografik bilgileri ara (Kişi Sayısı, Masa Sayısı, vb.)
            demographics_row = None
            for idx, row in df_str.iterrows():
                row_text = " ".join(str(cell) for cell in row.values if str(cell) != 'nan')
                if "Kişi Sayısı" in row_text or "Kisi Sayisi" in row_text:
                    demographics_row = idx
                    break
            
            if demographics_row is not None:
                # Demografik verileri çıkar
                demo_row = df_str.iloc[demographics_row]
                demo_values = [str(cell) for cell in demo_row.values if str(cell) != 'nan' and str(cell).replace('.', '').isdigit()]
                
                if len(demo_values) >= 4:
                    analysis_data["demographics"] = {
                        "total_people": int(float(demo_values[0])),
                        "total_tables": int(float(demo_values[1])),
                        "male_count": int(float(demo_values[2])),
                        "female_count": int(float(demo_values[3]))
                    }
            
            # En çok satan ürünleri analiz et (satış tablosundan)
            top_products = []
            for idx, row in df_str.iterrows():
                row_values = [str(cell) for cell in row.values if str(cell) != 'nan']
                if len(row_values) >= 3:
                    # Ürün adı, miktar, tutar formatında satır ara
                    product_name = row_values[0].strip()
                    if (product_name and 
                        not any(keyword in product_name.upper() for keyword in ["SATIŞ", "RAPORU", "GENEL", "TOPLAM", "AÇIKLAMA", "MİKTAR", "TUTAR", "YEKUN", "GENEL YEKUN", "GENEL TOPLAM"]) and
                        len(product_name) > 2):
                        
                        try:
                            quantity = float(row_values[1]) if row_values[1].replace('.', '').isdigit() else 0
                            amount = float(row_values[2]) if row_values[2].replace('.', '').isdigit() else 0
                            
                            if quantity > 0 and amount > 0:
                                top_products.append({
                                    "product_name": product_name,
                                    "quantity": quantity,
                                    "amount": amount,
                                    "unit_price": amount / quantity if quantity > 0 else 0
                                })
                        except (ValueError, ZeroDivisionError):
                            continue
            
            # En çok satan ürünleri sırala
            top_products.sort(key=lambda x: x["amount"], reverse=True)
            analysis_data["top_products"] = top_products[:10]  # Top 10
            
            # Kategori analizi (ürün adlarından kategori çıkar)
            category_stats = {}
            for product in top_products:
                product_name = product["product_name"].upper()
                
                # Kategori belirleme
                if any(word in product_name for word in ["KAHVE", "COFFEE", "AMERICANO", "LATTE", "ESPRESSO", "CAPPUCCINO"]):
                    category = "coffee"
                elif any(word in product_name for word in ["ÇAY", "TEA", "ÇAYI"]):
                    category = "tea"
                elif any(word in product_name for word in ["PASTA", "KEK", "KURA", "BÖREK"]):
                    category = "pastry"
                elif any(word in product_name for word in ["SODA", "SU", "İÇECEK", "SOĞUK", "ICED"]):
                    category = "beverage"
                else:
                    category = "other"
                
                if category not in category_stats:
                    category_stats[category] = {"count": 0, "total_amount": 0}
                
                category_stats[category]["count"] += product["quantity"]
                category_stats[category]["total_amount"] += product["amount"]
            
            analysis_data["category_breakdown"] = category_stats
            
            print(f"Analysis data extracted: {len(top_products)} products, demographics: {analysis_data.get('demographics', {})}")
            
        except Exception as e:
            print(f"Error extracting analysis data: {str(e)}")
            analysis_data["error"] = str(e)
        
        return analysis_data
    
    def update_stock_from_processed(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """İşlenmiş veriden ürünleri okuyup stoktan düş."""
        updated = 0
        attempted = 0
        warnings: List[str] = []
        errors: List[str] = []
        try:
            for record in processed_data:
                items_sold_raw = record.get("items_sold")
                if not items_sold_raw:
                    continue
                try:
                    items_payload = json.loads(items_sold_raw)
                except Exception:
                    # Eski format: dict içinde items olabilir
                    try:
                        items_payload = json.loads(items_sold_raw).get("items", [])
                    except Exception:
                        warnings.append("items_sold parse edilemedi")
                        continue
                
                # items_payload hem liste hem dict formatında olabilir
                if isinstance(items_payload, dict) and "items" in items_payload:
                    items = items_payload.get("items", [])
                else:
                    items = items_payload if isinstance(items_payload, list) else []
                
                for item in items:
                    raw_product_name = str(item.get("product", "")).strip()
                    product_name = raw_product_name
                    normalized_product_name = self._normalize_text(product_name)
                    try:
                        quantity = float(item.get("quantity", 0))
                    except Exception:
                        quantity = 0.0
                    if not product_name or quantity <= 0:
                        continue
                    attempted += 1
                    # Önce reçete bul, yoksa direkt stok kalemi düş
                    recipe = None
                    try:
                        # Hem ham hem normalize adla dene
                        recipe = self.supabase.get_recipe_by_name(product_name) or self.supabase.get_recipe_by_name(normalized_product_name)
                    except Exception:
                        recipe = None
                    if recipe and recipe.get("ingredients"):
                        matched_recipe_name = recipe.get("name", product_name)
                        print(f"RECIPE MATCH: '{raw_product_name}' -> '{matched_recipe_name}' (qty={quantity})")
                        for ingr in recipe.get("ingredients", []):
                            ingr_name_raw = (
                                ingr.get("name") or 
                                ingr.get("item_name") or 
                                ingr.get("ingredient_name") or ""
                            )
                            name = self._normalize_text(ingr_name_raw)
                            per_unit = (
                                ingr.get("quantity") or 
                                ingr.get("amount") or 
                                ingr.get("qty") or 0
                            )
                            try:
                                per_unit = float(per_unit)
                            except Exception:
                                per_unit = 0.0
                            total_consume = per_unit * quantity
                            if not name or total_consume <= 0:
                                continue
                            try:
                                # Hem ham hem normalize isimle dene
                                dec_res = self.supabase.decrement_stock_item(name, total_consume)
                                if not dec_res.get("success"):
                                    dec_res = self.supabase.decrement_stock_item(ingr_name_raw, total_consume)
                                if dec_res.get("success"):
                                    updated += 1
                                else:
                                    msg = dec_res.get("message", f"Stok düşülemedi: {name}")
                                    warnings.append(msg)
                                    print(f"DECREMENT WARN: {msg}")
                            except Exception as ex:
                                err = f"Stok düşüm hatası ({name}): {str(ex)}"
                                errors.append(err)
                                print(f"DECREMENT ERROR: {err}")
                    else:
                        # Reçete yoksa ürünü doğrudan stoktan düşmeyi dene
                        try:
                            print(f"NO RECIPE: '{raw_product_name}' -> direct decrement (qty={quantity})")
                            # normalize ve ham adla dene
                            dec_res = self.supabase.decrement_stock_item(normalized_product_name, quantity)
                            if not dec_res.get("success"):
                                dec_res = self.supabase.decrement_stock_item(product_name, quantity)
                            if dec_res.get("success"):
                                updated += 1
                            else:
                                msg = dec_res.get("message", f"Stok düşülemedi: {product_name}")
                                warnings.append(msg)
                                print(f"DECREMENT WARN: {msg}")
                        except Exception as ex:
                            err = f"Stok düşüm hatası ({product_name}): {str(ex)}"
                            errors.append(err)
                            print(f"DECREMENT ERROR: {err}")
            
            return {
                "attempted": attempted,
                "updated": updated,
                "warnings": warnings,
                "errors": errors
            }
        except Exception as e:
            return {
                "attempted": attempted,
                "updated": updated,
                "warnings": warnings,
                "errors": errors + [str(e)]
            }

    def suggest_name_mappings(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Eşleşmeyen ürünler için Supabase'den en yakın eşleşmeleri öner."""
        suggestions: List[Dict[str, Any]] = []
        try:
            # Tüm tarif ve stok isimlerini al
            recipes_resp = self.supabase.client.table("recipes").select("recipe_name").execute()
            recipe_names = [r.get("recipe_name", "") for r in (recipes_resp.data or [])]
            items_resp = self.supabase.client.table("stock_items").select("item_name").execute()
            stock_names = [r.get("item_name", "") for r in (items_resp.data or [])]
            
            seen: set = set()
            for record in processed_data:
                items_sold_raw = record.get("items_sold")
                if not items_sold_raw:
                    continue
                try:
                    payload = json.loads(items_sold_raw)
                except Exception:
                    continue
                items = payload.get("items", payload if isinstance(payload, list) else [])
                for it in items:
                    raw_name = str(it.get("product", "")).strip()
                    if not raw_name or raw_name in seen:
                        continue
                    seen.add(raw_name)
                    norm = self._normalize_text(raw_name)
                    # Basit bulunurluk testi
                    has_recipe = any(self._normalize_text(n) == norm for n in recipe_names)
                    has_stock = any(self._normalize_text(n) == norm for n in stock_names)
                    if has_recipe or has_stock:
                        continue
                    # Fuzzy en iyi adayları bul (mevcut yardımcıyı kullanmak için private fonksiyon yok, basit skorlama)
                    def score(cand: str) -> float:
                        from difflib import SequenceMatcher
                        return SequenceMatcher(None, norm.lower(), self._normalize_text(cand).lower()).ratio()
                    best_recipe = max(recipe_names, key=score, default="")
                    best_stock = max(stock_names, key=score, default="")
                    suggestions.append({
                        "product": raw_name,
                        "normalized": norm,
                        "best_recipe": best_recipe,
                        "best_stock_item": best_stock
                    })
            if suggestions:
                print("NAME MAPPING SUGGESTIONS:")
                for s in suggestions[:20]:
                    print(f"  '{s['product']}' -> recipe?: '{s['best_recipe']}', stock?: '{s['best_stock_item']}'")
            return {"suggestions": suggestions}
        except Exception as e:
            return {"error": str(e), "suggestions": suggestions}

    def extract_date_from_filename(self, file_path: str) -> str:
        """Dosya adından tarih çıkar (5.10.2025.xls -> 2025-10-05)"""
        try:
            import re
            import os
            filename = os.path.basename(file_path)  # Sadece dosya adını al
            
            # Tarih formatını bul (5.10.2025, 05.10.2025, vb.)
            date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', filename)
            
            if date_match:
                day, month, year = date_match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            else:
                return datetime.now().strftime("%Y-%m-%d")
                
        except Exception as e:
            print(f"Tarih çıkarma hatası: {str(e)}")
            return datetime.now().strftime("%Y-%m-%d")
    
    def find_and_extract_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Excel'deki satış verilerini bul ve çıkar"""
        try:
            # "AÇIKLAMA" başlığını bul
            header_row = None
            for i in range(len(df)):
                row_values = df.iloc[i].astype(str).tolist()
                if any('AÇIKLAMA' in val.upper() or 'ÜRÜN' in val.upper() for val in row_values):
                    header_row = i
                    break
            
            if header_row is None:
                print("AÇIKLAMA başlığı bulunamadı!")
                return pd.DataFrame()
            
            print(f"AÇIKLAMA başlığı bulundu: Satır {header_row}")
            
            # Başlık satırından sonraki verileri al
            sales_data = df.iloc[header_row+1:].copy()
            
            # Boş satırları temizle
            sales_data = sales_data.dropna(how='all')
            
            # Sadece ürün satırlarını al (ilk sütunda ürün adı olan satırlar)
            product_rows = []
            for i in range(len(sales_data)):
                first_col_value = sales_data.iloc[i, 0]
                if pd.notna(first_col_value) and str(first_col_value).strip() != "":
                    # Ürün adı kontrolü
                    product_name = str(first_col_value).strip()
                    if not product_name.isdigit() and len(product_name) > 2:
                        product_rows.append(i)
            
            if product_rows:
                # Ürün satırlarını al
                filtered_data = sales_data.iloc[product_rows].copy()
                print(f"Satış verisi satır sayısı: {len(filtered_data)}")
                return filtered_data
            else:
                print("Ürün satırı bulunamadı!")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Satış verisi çıkarma hatası: {str(e)}")
            return pd.DataFrame()
    
    def clean_and_convert_data(self, sales_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Excel verisini temizle ve bizim formata dönüştür"""
        processed_data = []
        
        print("Veri dönüştürme başlıyor...")
        
        # DARA Excel formatı analizi:
        # Sütun 0: Ürün adı (AÇIKLAMA)
        # Sütun 7: Miktar 
        # Sütun 11: Tutar (fiyat)
        
        total_quantity = 0
        total_amount = 0
        items = []
        
        for index, row in sales_data.iterrows():
            try:
                # Ürün adı (Sütun 0)
                product_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                
                if not product_name or len(product_name) < 2:
                    continue
                
                # Toplam satırlarını filtrele (GENEL YEKUN, GENEL TOPLAM, vb.)
                product_name_upper = product_name.upper()
                if any(keyword in product_name_upper for keyword in ["GENEL YEKUN", "GENEL TOPLAM", "TOPLAM", "YEKUN", "SATIŞ RAPORU", "AÇIKLAMA", "MİKTAR", "TUTAR"]):
                    continue
                
                # Miktar (Sütun 7)
                quantity = 0.0
                if pd.notna(row.iloc[7]):
                    try:
                        quantity = float(row.iloc[7])
                    except:
                        quantity = 0.0
                
                # Tutar (Sütun 11)
                amount = 0.0
                if pd.notna(row.iloc[11]):
                    try:
                        amount = float(row.iloc[11])
                    except:
                        amount = 0.0
                
                # Birim fiyat hesapla
                unit_price = amount / quantity if quantity > 0 else 0.0
                
                # Veri toplama
                total_quantity += quantity
                total_amount += amount
                
                item_data = {
                    "product": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": amount
                }
                items.append(item_data)
                
                print(f"  {product_name}: {quantity} adet, {amount:.2f} TL")
                
            except Exception as e:
                print(f"Satır {index} işleme hatası: {str(e)}")
                continue
        
        if items:
            # Günlük toplam kaydı oluştur (mevcut sütunlarla uyumlu)
            daily_record = {
                "date": self.date_from_file,
                "total_sales": total_amount,
                "items_sold": json.dumps({
                    "total_quantity": total_quantity,
                    "items": items,
                    "transaction_id": f"DARA_EXCEL_{self.date_from_file.replace('-', '')}",
                    "order_no": f"DARA_{self.date_from_file.replace('-', '')}",
                    "source": "dara_excel_import",
                    "import_date": datetime.now().isoformat(),
                    "file_date": self.date_from_file,
                    "total_items": len(items),
                    "processing_method": "dara_excel_processor_v1"
                }, ensure_ascii=False)
            }
            
            processed_data.append(daily_record)
            
            print(f"Toplam: {total_quantity} adet, {total_amount:.2f} TL")
            print(f"İşlenen ürün sayısı: {len(items)}")
        
        return processed_data
    
    def save_to_supabase(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """İşlenmiş veriyi Supabase'e kaydet"""
        saved_count = 0
        errors = []
        
        for data in processed_data:
            try:
                # Önce aynı tarih ile kayıt var mı kontrol et
                items_data = json.loads(data["items_sold"])
                transaction_id = items_data.get("transaction_id", "")
                
                existing = self.supabase.client.table("sales_history").select("*").eq("date", data["date"]).execute()
                
                # Aynı transaction_id ile kayıt var mı kontrol et
                existing_with_same_id = False
                for existing_record in existing.data:
                    existing_items = json.loads(existing_record.get("items_sold", "{}"))
                    existing_transaction_id = existing_items.get("transaction_id", "")
                    if existing_transaction_id == transaction_id:
                        existing_with_same_id = True
                        break
                
                if existing_with_same_id:
                    print(f"Kayıt zaten mevcut: {transaction_id} - Güncelleniyor...")
                    # Mevcut kaydı güncelle
                    update_result = self.supabase.client.table("sales_history").update(data).eq("date", data["date"]).execute()
                    if update_result.data:
                        saved_count += 1
                        print(f"DARA Excel verisi güncellendi: {transaction_id}")
                    continue
                
                result = self.supabase.client.table("sales_history").insert(data).execute()
                
                if result.data:
                    saved_count += 1
                    print(f"DARA Excel verisi kaydedildi: {transaction_id}")
                else:
                    errors.append(f"Insert failed for {transaction_id}")
                    
            except Exception as e:
                error_msg = f"Error saving {transaction_id}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        return {
            "saved_count": saved_count,
            "errors": errors
        }
    
    def get_sales_summary(self, date: str = None) -> Dict[str, Any]:
        """Belirli bir tarih için satış özeti al"""
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Supabase'den o tarihteki DARA Excel verilerini al
            result = self.supabase.client.table("sales_history").select("*").eq("date", date).execute()
            
            if result.data:
                total_sales = sum(float(record.get("total_sales", 0)) for record in result.data)
                
                # items_sold'dan total_quantity çıkar
                total_quantity = 0
                for record in result.data:
                    items_sold = record.get("items_sold", "{}")
                    try:
                        items_data = json.loads(items_sold)
                        total_quantity += float(items_data.get("total_quantity", 0))
                    except:
                        pass
                
                return {
                    "date": date,
                    "total_sales": total_sales,
                    "total_quantity": total_quantity,
                    "record_count": len(result.data),
                    "source": "DARA Excel Import"
                }
            else:
                return {
                    "date": date,
                    "total_sales": 0,
                    "total_quantity": 0,
                    "record_count": 0,
                    "source": "DARA Excel Import"
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "date": date,
                "source": "DARA Excel Import"
            }

# Test fonksiyonu
def test_dara_excel_processor():
    """DARA Excel işleyiciyi test et"""
    try:
        from supabase_service import SupabaseService
        
        print("DARA Excel Processor Test")
        print("=" * 40)
        
        # Supabase servisini başlat
        supabase = SupabaseService()
        processor = DaraExcelProcessor(supabase)
        
        # Excel dosyasını işle
        result = processor.process_dara_excel("../5.10.2025.xls")
        
        print(f"\nİşlem Sonucu:")
        print(f"Başarılı: {result['success']}")
        
        if result['success']:
            print(f"İşlenen: {result['processed_count']}")
            print(f"Kaydedilen: {result['saved_count']}")
            print(f"Tarih: {result['date']}")
            
            if result['errors']:
                print(f"Hatalar: {len(result['errors'])}")
                for error in result['errors'][:3]:
                    print(f"  - {error}")
        else:
            print(f"Hata: {result['error']}")
        
        # Satış özeti al
        if result['success'] and result['date']:
            summary = processor.get_sales_summary(result['date'])
            print(f"\nSatış Özeti ({summary['date']}):")
            print(f"Toplam Satış: {summary['total_sales']:.2f} TL")
            print(f"Toplam Miktar: {summary['total_quantity']} adet")
            print(f"Kayıt Sayısı: {summary['record_count']}")
        
    except Exception as e:
        print(f"Test hatası: {str(e)}")

if __name__ == "__main__":
    test_dara_excel_processor()
