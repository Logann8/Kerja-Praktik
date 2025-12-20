# Aplikasi Pembelian Barang dari Vendor

Aplikasi Flask untuk mengelola pembelian barang dari vendor.

## Struktur Proyek

```
.
├── app/
│   ├── __init__.py          # App factory
│   ├── models/              # Database models
│   ├── routes/              # Blueprint routes
│   ├── forms/               # Form handling
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Utility functions
├── config.py                # Konfigurasi aplikasi
├── run.py                   # Entry point aplikasi
└── requirements.txt         # Dependencies

```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Database MySQL (Laragon)

1. Pastikan Laragon sudah berjalan
2. Buat database baru di phpMyAdmin atau MySQL:
   ```sql
   CREATE DATABASE pembelian_db;
   ```

### 3. Konfigurasi Environment

Buat file `.env` di root project (copy dari `.env.example`):

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=pembelian_db
SQLALCHEMY_ECHO=False
```

### 4. Jalankan Aplikasi

```bash
python run.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## Fitur

- ✅ Modul Pembelian Barang dari Vendor
- ✅ Manajemen Vendor
- ❌ Modul Penjualan (tidak termasuk)
- ❌ Modul Pengelolaan Stok (tidak termasuk)

## Teknologi

- Flask 3.0.0
- SQLAlchemy (MySQL)
- PyMySQL

