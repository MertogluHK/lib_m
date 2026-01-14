# Kütüphane Yönetim Sistemi

Bu proje, Django web çatısı kullanılarak geliştirilmiş bir **Kütüphane Yönetim Sistemi**dir.  
Proje, bir bitirme ödevi kapsamında geliştirilmiş olup kitap yönetimi, kullanıcı değerlendirmeleri ve rezervasyon süreçlerini kapsamaktadır.

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

```

lib_ms/
├── books/ # Kitap ve değerlendirme işlemleri
├── reservations/ # Rezervasyon (ödünç alma) işlemleri
├── users/ # Kullanıcı işlemleri ve yetkilendirme
├── community/ # Topluluk / etkileşim modülü
├── frontend/ # Arayüz ve statik dosyalar
├── lib_ms/ # Proje ayarları
└── manage.py

````

## Kurulum

1. Depoyu klonlayın:


```

git clone https://github.com/MertogluHK/lib_m.git
cd lib_ms

```

2. Sanal ortam oluşturun ve etkinleştirin:


```

python -m venv venv
venv\Scripts\activate

```

3. Gerekli paketleri yükleyin:


```

python -m pip install requirements.txt

```

4. Ortam değişkenlerini ayarlayın:


```

DB_ENGINE=postgres
POSTGRES_DB=book_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=*****
DJANGO_SECRET_KEY=*****

```


