# Kütüphane Yönetim Sistemi

Bu proje, Django web çatısı kullanılarak geliştirilmiş bir **Kütüphane Yönetim Sistemi**dir.  
Proje, bir bitirme ödevi kapsamında geliştirilmiş olup kitap yönetimi, kullanıcı değerlendirmeleri ve rezervasyon süreçlerini kapsamaktadır.

## Anasayfa

<img width="1000" height="479" alt="image" src="https://github.com/user-attachments/assets/d959b28f-6100-45c0-8a23-d9b36e79ae40" />

## Yönetim

<img width="1000" height="728" alt="image" src="https://github.com/user-attachments/assets/8b4475d1-b903-4a1e-bd05-edfc2bce32ed" />

## Özellikler

- Kitap ekleme, güncelleme, silme ve listeleme
- Kitaplar için kullanıcı değerlendirme (puan ve yorum) sistemi
- Kitap rezervasyon yönetimi
- Rezervasyon durum takibi (beklemede, teslim alındı, iptal, iade)
- Rol bazlı yetkilendirme (yönetici / kullanıcı)
- REST API mimarisi
- JWT tabanlı kimlik doğrulama
- PostgreSQL veritabanı desteği

## Kullanılan Teknolojiler

- **Backend:** Django 5.0.6
- **API:** Django REST Framework
- **Veritabanı:** PostgreSQL
- **ORM:** Django ORM
- **Kimlik Doğrulama:** JWT (SimpleJWT)
- **Frontend:** Django Template Engine, HTML, CSS, JavaScript

## Proje Yapısı

lib_ms/
├── books/ # Kitap ve değerlendirme işlemleri
├── reservations/ # Rezervasyon (ödünç alma) işlemleri
├── users/ # Kullanıcı işlemleri ve yetkilendirme
├── community/ # Topluluk / etkileşim modülü
├── frontend/ # Arayüz ve statik dosyalar
├── lib_ms/ # Proje ayarları
└── manage.py


## Kurulum

1. Depoyu klonlayın:

```bash
git clone https://github.com/MertogluHK/lib_m.git
cd lib_ms
```

2. Sanal ortam oluşturun ve etkinleştirin

```bash
python -m venv venv
venv\Scripts\activate
```

3. Gerekli paketleri yükleyin

```bash
python -m pip install -r requirements.txt
```

4. Ortam değişkenlerini ayarlayın

DB_ENGINE=postgres
POSTGRES_DB=book_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=*****
DJANGO_SECRET_KEY=*****

5. Migration işlemlerini uygulayın

```bash
python manage.py migrate
```

6. Sunucuyu başlatın

```bash
python manage.py runserver
```

