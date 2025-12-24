# QUICKSTART  Kısa Başlangıç Rehberi

Bu dosya projeyi hızlıca çalıştırmak için en temel adımları içerir.

Özet: lib_ms, Django + DRF ile yazılmış bir kütüphane yönetim sistemidir. Aşağıdaki adımlar development ortamını ayağa kaldırır.

## Hızlı Adımlar

- Ortam bağımlılıklarını yükleyin:

```bash
pip install -r requirements.txt
```

- Migrasyonları uygula:

```bash
python manage.py migrate
```

- Yönetici oluştur:

```bash
python manage.py createsuperuser
```

- (İsteğe bağlı) Örnek veri yükle:

```bash
python manage.py load_books
```

- Sunucuyu başlat:

```bash
python manage.py runserver
```

Erişimler:

- Web: http://localhost:8000
- Admin: http://localhost:8000/admin
- API kökü: http://localhost:8000/api

## Önemli Komutlar

- Testleri çalıştır: `python manage.py test`
- Özel komutlar: `load_books`, `import_external_books`, `recalc_book_ratings`

## Kısa API Özeti

- Kitaplar: `GET /api/books/`, `GET /api/books/{id}/`, `POST /api/books/` (admin)
- Rezervasyonlar: `GET /api/reservations/`, `POST /api/reservations/`
- Topluluk: `GET /api/community/`, `POST /api/community/`
- Auth: token alma `POST /api/auth/user-token/`, token yenileme `/api/auth/token/refresh/`

## Production Önerileri (kısa)

- `.env` ile `DJANGO_DEBUG=0` ayarla ve güçlü `DJANGO_SECRET_KEY` kullan.
- PostgreSQL ve uygun `ALLOWED_HOSTS` yapılandır.
- `python manage.py collectstatic --noinput` ve migrate.

İhtiyacınız varsa daha da kısaltabilirim veya belirli bölümleri (ör. sadece deploy adımları) ayrı bir dosyaya taşıyabilirim.
