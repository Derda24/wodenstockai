# 🚀 Supabase Migration Setup Guide

Bu rehber, Woden AI Stock Management sistemini JSON dosyalarından Supabase veritabanına geçirmeniz için hazırlanmıştır.

## 📋 Ön Gereksinimler

- Supabase hesabı (ücretsiz)
- Python 3.9+ ve pip
- Mevcut JSON veri dosyalarınız

## 🔧 Adım 1: Supabase Projesi Oluşturma

### 1.1 Supabase'e Giriş
- [supabase.com](https://supabase.com) adresine gidin
- GitHub ile giriş yapın
- "New Project" butonuna tıklayın

### 1.2 Proje Ayarları
- **Organization**: Kendi organizasyonunuzu seçin
- **Name**: `woden-ai-stock` (veya istediğiniz isim)
- **Database Password**: Güçlü bir şifre belirleyin (not edin!)
- **Region**: `Central Europe (Frankfurt)` seçin (Türkiye'ye yakın)
- **Pricing Plan**: Free tier seçin

### 1.3 Proje Oluşturma
- "Create new project" butonuna tıklayın
- Proje oluşturulana kadar bekleyin (2-3 dakika)

## 🗄️ Adım 2: Veritabanı Şeması Oluşturma

### 2.1 SQL Editor'a Erişim
- Proje dashboard'unda sol menüden "SQL Editor" seçin
- "New query" butonuna tıklayın

### 2.2 Şema Oluşturma
- `backend/supabase_schema.sql` dosyasının içeriğini kopyalayın
- SQL Editor'a yapıştırın
- "Run" butonuna tıklayın

### 2.3 Tabloları Kontrol Etme
- Sol menüden "Table Editor" seçin
- Aşağıdaki tabloların oluştuğunu doğrulayın:
  - `stock_items`
  - `stock_transactions`
  - `manual_updates`
  - `daily_usage_config`
  - `recipes`
  - `sales_history`

## 🔑 Adım 3: API Anahtarlarını Alma

### 3.1 Project Settings
- Sol menüden "Settings" → "API" seçin

### 3.2 Anahtarları Kopyalama
- **Project URL**: `https://your-project-ref.supabase.co`
- **anon public**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## ⚙️ Adım 4: Environment Variables Ayarlama

### 4.1 .env Dosyası Oluşturma
`backend/` klasöründe `.env` dosyası oluşturun:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database Configuration (Supabase Postgres)
DATABASE_URL=postgresql://postgres.your_project_ref:your_password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# Environment
ENVIRONMENT=development
DEBUG=true

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
```

### 4.2 Değişkenleri Doldurma
- `SUPABASE_URL`: Project URL'den
- `SUPABASE_ANON_KEY`: anon public key'den
- `SUPABASE_SERVICE_ROLE_KEY`: service_role key'den (gerekirse)
- `DATABASE_URL`: Connection string'den (Settings → Database)

## 📊 Adım 5: Veri Migrasyonu

### 5.1 Migrasyon Script'ini Çalıştırma
```bash
cd backend
python migrate_to_supabase.py
```

### 5.2 Migrasyon Onayı
- Script size kaç item'ın migrate edileceğini gösterecek
- "yes" yazarak onaylayın
- Migrasyon tamamlanana kadar bekleyin

### 5.3 Sonuçları Kontrol Etme
- Supabase Table Editor'da verilerin geldiğini doğrulayın
- `stock_items` tablosunda tüm malzemelerin olduğunu kontrol edin

## 🔄 Adım 6: Backend'i Supabase'e Geçirme

### 6.1 Stock Manager Güncelleme
`backend/app/stock_manager.py` dosyasını Supabase kullanacak şekilde güncelleyin:

```python
from app.services.supabase_service import SupabaseService

class StockManager:
    def __init__(self):
        self.supabase_service = SupabaseService()
    
    def get_stock_list(self):
        return self.supabase_service.get_stock_list()
    
    def update_stock_manually(self, material_id, new_stock, reason):
        return self.supabase_service.update_stock_manually(material_id, new_stock, reason)
    
    def apply_daily_consumption(self):
        return self.supabase_service.apply_daily_consumption()
```

### 6.2 API Endpoint'leri Güncelleme
`main.py`'de yeni endpoint'leri ekleyin:

```python
@app.get("/api/stock/supabase-test")
async def test_supabase_connection():
    try:
        supabase_service = SupabaseService()
        result = supabase_service.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🧪 Adım 7: Test Etme

### 7.1 Bağlantı Testi
```bash
curl http://localhost:8000/api/stock/supabase-test
```

### 7.2 Stock List Testi
```bash
curl http://localhost:8000/api/stock/list
```

### 7.3 Stock Update Testi
```bash
curl -X POST http://localhost:8000/api/stock/update \
  -F "material_id=cay_urunleri_Yeşil_Çay" \
  -F "new_stock=300" \
  -F "reason=test_update"
```

## 🚨 Önemli Notlar

### Güvenlik
- `.env` dosyasını asla GitHub'a push etmeyin
- `.gitignore`'a `.env` ekleyin
- Production'da environment variables kullanın

### Performans
- Supabase Free tier: 500MB database, 2GB bandwidth
- Row Level Security (RLS) şimdilik kapalı
- İhtiyaç halinde RLS aktif edilebilir

### Backup
- JSON dosyalarınızı yedekleyin
- Supabase'de otomatik backup var
- Manuel backup için Table Editor'dan export yapabilirsiniz

## 🔧 Sorun Giderme

### Bağlantı Hatası
```
Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set
```
**Çözüm**: `.env` dosyasını kontrol edin, değişkenleri doğru doldurun

### Tablo Bulunamadı
```
relation "stock_items" does not exist
```
**Çözüm**: `supabase_schema.sql`'i SQL Editor'da çalıştırın

### Migrasyon Hatası
```
Error: Migration failed
```
**Çözüm**: 
1. Supabase bağlantısını test edin
2. Tabloların oluştuğunu kontrol edin
3. JSON dosyalarının formatını kontrol edin

## 📞 Destek

Sorun yaşarsanız:
1. Supabase logs'ları kontrol edin (Settings → Logs)
2. Python console'da hata mesajlarını inceleyin
3. Supabase Discord community'ye katılın

## 🎯 Sonraki Adımlar

1. **Frontend Güncelleme**: StockList.tsx'i Supabase realtime ile güncelleyin
2. **Authentication**: Supabase Auth entegrasyonu ekleyin
3. **Storage**: Supabase Storage ile dosya yönetimi ekleyin
4. **Functions**: Edge Functions ile serverless logic ekleyin

---

**🎉 Tebrikler!** Artık Woden AI Stock Management sisteminiz Supabase üzerinde çalışıyor!
