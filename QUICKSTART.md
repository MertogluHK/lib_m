# 🚀 LIB_MS Projesi - Başlangıç Rehberi

## Proje Hakkında

**lib_ms** (Library Management System) Django 5.0 ile yazılmış bir kütüphane yönetim sistemidir. REST API ile kitap yönetimi, rezervasyonlar, incelemeler ve topluluk özelliklerini sağlar.

---

## 🎯 Proje Durumu

✅ **Durum:** Tamamen fonksiyonel ve test edilmiş  
✅ **Hata:** Yok  
✅ **Uyarılar:** Sadece development ortamı notları  
✅ **Hazır:** Geliştirmeye başlamaya hazır

---

## 📦 Teknoloji Stack

- **Backend:** Django 5.0.6
- **API:** Django REST Framework 3.15.2
- **Auth:** JWT (djangorestframework-simplejwt)
- **Database:** SQLite3 (PostgreSQL ready)
- **Image Processing:** Pillow
- **CORS:** django-cors-headers

---

## 🏃 Hızlı Başlangıç

### 1. Veritabanını Hazırla
```bash
python manage.py migrate
```

### 2. Admin Kullanıcısı Oluştur
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: [choose strong password]
```

### 3. Sample Verisi Yükle (İsteğe Bağlı)
```bash
python manage.py load_books
```

### 4. Development Server Başlat
```bash
python manage.py runserver
```

### 5. Uygulamayı Ziyaret Et
- **Web:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **API:** http://localhost:8000/api

---

## 📚 API Endpoints

### Books (Kitaplar)
```
GET    /api/books/                    - Kitaplar listesi
GET    /api/books/{id}/              - Kitap detayı
POST   /api/books/                    - Yeni kitap ekle (admin)
PUT    /api/books/{id}/              - Kitap güncelle (admin)
DELETE /api/books/{id}/              - Kitap sil (admin)

GET    /api/books/filters/            - Filter seçenekleri
GET    /api/books/suggest/            - Autocomplete
POST   /api/books/{id}/reviews        - İnceleme ekle
GET    /api/books/{id}/reviews        - İnceleme listesi
POST   /api/books/{id}/upload_cover   - Kapak görseli yükle
```

### Reservations (Rezervasyonlar)
```
GET    /api/reservations/              - Rezervasyon listesi
POST   /api/reservations/              - Yeni rezervasyon
GET    /api/reservations/{id}/        - Detaylar
POST   /api/reservations/{id}/pickup  - Kitap al
POST   /api/reservations/{id}/cancel  - İptal et
POST   /api/reservations/{id}/return  - İade et
```

### Community (Topluluk)
```
GET    /api/community/                 - Gönderiler
POST   /api/community/                 - Yeni gönderi
GET    /api/community/my_posts         - Benim gönderilerim
POST   /api/community/{id}/comments    - Yorum ekle
DELETE /api/community/{id}/comments/{comment_id}  - Yorum sil
```

### Authentication (Kimlik Doğrulama)
```
POST   /api/auth/user-token/          - Kullanıcı girişi
POST   /api/auth/admin-token/         - Admin girişi
POST   /api/auth/token/refresh/       - Token yenile
POST   /api/users/register/           - Yeni hesap
GET    /api/users/me/                 - Profil bilgisi
PATCH  /api/users/me/                 - Profil güncelle
```

---

## 🔐 Kimlik Doğrulama

### Token Alma
```bash
# User login
curl -X POST http://localhost:8000/api/auth/user-token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Response:
{
  "refresh": "eyJ0...",
  "access": "eyJ0...",
  "role": "admin",
  "username": "admin"
}
```

### Token Kullanma
```bash
# Authenticated request
curl -X GET http://localhost:8000/api/books/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Token Yenileme
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

---

## 📊 Proje Yapısı

```
lib_ms/
├── books/                    # Kitap yönetimi
│   ├── models.py            # Book, Review modelleri
│   ├── views.py             # BookViewSet
│   ├── serializers.py       # Serializers
│   ├── urls.py              # API routes
│   └── management/commands/ # Django commands
│
├── reservations/             # Rezervasyon sistemi
│   ├── models.py            # Reservation modeli
│   ├── views.py             # ReservationViewSet
│   └── serializers.py       # Serializers
│
├── community/                # Topluluk özellikleri
│   ├── models.py            # Post, Comment modelleri
│   ├── views.py             # CommunityPostViewSet
│   └── serializers.py       # Serializers
│
├── users/                    # Kullanıcı yönetimi
│   ├── views.py             # Register, Auth views
│   └── serializers.py       # User serializers
│
├── frontend/                 # Web arayüzü
│   ├── views.py             # Template views
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, Görüntüler
│
├── lib_ms/                   # Project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Ana URL router
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
│
├── manage.py                 # Django management
├── db.sqlite3               # Database
└── requirements.txt         # Python packages
```

---

## 🧪 Testleri Çalıştırma

### Sistem Kontrolü
```bash
python manage.py check
```

### Migrasyonları Doğrula
```bash
python manage.py showmigrations
python manage.py migrate --dry-run
```

### Özel Test Scriptlerini Çalıştır
```bash
# Basic health check
python test_project.py

# Comprehensive tests
python test_comprehensive.py
```

### Django Test Suite
```bash
python manage.py test
```

---

## 🛠️ Özel Django Commands

### Kitap Yükleme
```bash
# 250+ kitap, 700+ kopya yükle
python manage.py load_books

# Custom sayılar ile
python manage.py load_books --min_distinct=100 --min_total=500
```

### Harici Kitap İçe Aktarma
```bash
python manage.py import_external_books
```

### Rating Yeniden Hesapla
```bash
python manage.py recalc_book_ratings
```

---

## 🔧 Environment Variables (İsteğe Bağlı)

`.env` dosyası oluştur:
```env
# Django
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=sqlite    # veya postgres
POSTGRES_DB=book_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# CORS
DJANGO_CORS_ALLOW_ALL=1

# Authentication
JWT_ALGORITHM=HS256
```

---

## 📝 İlk Adımlar

### 1. Admin Paneline Gir
```
URL: http://localhost:8000/admin
Username: admin
Password: [you created earlier]
```

### 2. Test Kitabı Ekle
```bash
python manage.py shell

# Python shell'de:
from books.models import Book
Book.objects.create(
    isbn='978-1234567890',
    title='My First Book',
    author='Test Author',
    stock=3
)
```

### 3. API Test Et
```bash
curl http://localhost:8000/api/books/
```

### 4. Frontend'i Ziyaret Et
```
http://localhost:8000/books/
```

---

## 🚨 Sık Sorunlar ve Çözümleri

### Problem: "ModuleNotFoundError"
**Çözüm:**
```bash
pip install -r requirements.txt
```

### Problem: "Database connection refused"
**Çözüm:**
```bash
python manage.py migrate
rm db.sqlite3
python manage.py migrate
```

### Problem: "Static files not loading"
**Çözüm:**
```bash
python manage.py collectstatic
```

### Problem: "No such table" hatasıe
**Çözüm:**
```bash
python manage.py migrate --verbosity=2
```

---

## 📈 Production Deployment

### 1. Environment Ayarla
```env
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=generate-strong-random-key
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=postgres
POSTGRES_DB=production_db
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=strong-password
```

### 2. Settings Güncelle
```bash
# Production check
python manage.py check --deploy
```

### 3. Static Files
```bash
python manage.py collectstatic --noinput
```

### 4. Database Migrate
```bash
python manage.py migrate --noinput
```

### 5. WSGI Server (Gunicorn example)
```bash
pip install gunicorn
gunicorn lib_ms.wsgi:application --bind 0.0.0.0:8000
```

---

## 📞 Destek

### Kontrol Noktaları
- ✅ Django health: `python manage.py check`
- ✅ Database: Admin panelde kontrol et
- ✅ API: `http://localhost:8000/api/`
- ✅ Static files: `http://localhost:8000/static/`

### Logları İncele
```bash
# Django runserver ile çalışan sunucu otomatik log gösterir
# Production'da LOGGING yapılandırması uygulanmalı
```

---

## 📚 Kaynaklar

- [Django Dokumentasyonu](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Kimlik Doğrulama](https://django-rest-framework-simplejwt.readthedocs.io/)

---

## 🎓 Sonraki Adımlar

1. ✅ Geliştirmeye başla
2. ✅ Test yazabilirsiniz
3. ✅ Features ekle
4. ✅ Frontend geliştir
5. ✅ Production'a deploy et

---

**Happy Coding! 🚀**

İlk sunucuyu başlatmak için:
```bash
python manage.py runserver
```

Tarayıcınızda açın: http://localhost:8000
