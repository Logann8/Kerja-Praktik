# Desain Database - Modul Pembelian

Dokumen ini menjelaskan struktur tabel database yang dibutuhkan untuk modul pembelian.

## 1. Tabel `vendor`

Tabel untuk menyimpan data vendor/supplier.

| Nama Kolom | Tipe Data | Constraints | Keterangan |
|------------|-----------|-------------|------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | ID unik vendor |
| kode | VARCHAR(20) | UNIQUE, NOT NULL | Kode vendor (unik) |
| nama | VARCHAR(100) | NOT NULL | Nama vendor |
| alamat | TEXT | NULL | Alamat vendor |
| telepon | VARCHAR(20) | NULL | Nomor telepon |
| email | VARCHAR(100) | NULL | Email vendor |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Waktu pembuatan record |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Waktu update terakhir |

**Index:**
- PRIMARY KEY: `id`
- UNIQUE: `kode`

---

## 2. Tabel `barang`

Tabel untuk menyimpan data barang/produk.

| Nama Kolom | Tipe Data | Constraints | Keterangan |
|------------|-----------|-------------|------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | ID unik barang |
| kode | VARCHAR(20) | UNIQUE, NOT NULL | Kode barang (unik) |
| nama | VARCHAR(100) | NOT NULL | Nama barang |
| satuan | VARCHAR(20) | NOT NULL | Satuan (pcs, kg, liter, dll) |
| harga_beli | DECIMAL(15,2) | NOT NULL, DEFAULT 0 | Harga beli standar |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Waktu pembuatan record |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Waktu update terakhir |

**Index:**
- PRIMARY KEY: `id`
- UNIQUE: `kode`

---

## 3. Tabel `pembelian`

Tabel untuk menyimpan data transaksi pembelian.

| Nama Kolom | Tipe Data | Constraints | Keterangan |
|------------|-----------|-------------|------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | ID unik pembelian |
| no_faktur | VARCHAR(50) | UNIQUE, NOT NULL | Nomor faktur pembelian |
| vendor_id | INT | FOREIGN KEY, NOT NULL | ID vendor (relasi ke tabel vendor) |
| tanggal | DATE | NOT NULL | Tanggal pembelian |
| total | DECIMAL(15,2) | NOT NULL, DEFAULT 0 | Total pembelian |
| keterangan | TEXT | NULL | Keterangan tambahan |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Waktu pembuatan record |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Waktu update terakhir |

**Index:**
- PRIMARY KEY: `id`
- UNIQUE: `no_faktur`
- FOREIGN KEY: `vendor_id` REFERENCES `vendor(id)` ON DELETE RESTRICT

---

## 4. Tabel `detail_pembelian`

Tabel untuk menyimpan detail item barang dalam setiap transaksi pembelian.

| Nama Kolom | Tipe Data | Constraints | Keterangan |
|------------|-----------|-------------|------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | ID unik detail pembelian |
| pembelian_id | INT | FOREIGN KEY, NOT NULL | ID pembelian (relasi ke tabel pembelian) |
| barang_id | INT | FOREIGN KEY, NOT NULL | ID barang (relasi ke tabel barang) |
| qty | DECIMAL(10,2) | NOT NULL | Jumlah/kuantitas barang |
| harga | DECIMAL(15,2) | NOT NULL | Harga per unit saat pembelian |
| subtotal | DECIMAL(15,2) | NOT NULL | Subtotal (qty × harga) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Waktu pembuatan record |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Waktu update terakhir |

**Index:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `pembelian_id` REFERENCES `pembelian(id)` ON DELETE CASCADE
- FOREIGN KEY: `barang_id` REFERENCES `barang(id)` ON DELETE RESTRICT

---

## Relasi Antar Tabel

```
vendor (1) ────< (N) pembelian
barang (1) ────< (N) detail_pembelian
pembelian (1) ────< (N) detail_pembelian
```

**Penjelasan Relasi:**
- Satu vendor dapat memiliki banyak pembelian (one-to-many)
- Satu pembelian dapat memiliki banyak detail pembelian (one-to-many)
- Satu barang dapat muncul di banyak detail pembelian (one-to-many)

---

## Catatan Penting

1. **Tipe Data DECIMAL**: Digunakan untuk menyimpan nilai uang dengan presisi 2 digit di belakang koma
2. **ON DELETE CASCADE**: Pada `detail_pembelian.pembelian_id` - jika pembelian dihapus, detail pembelian juga ikut terhapus
3. **ON DELETE RESTRICT**: Pada foreign key lainnya - mencegah penghapusan jika masih ada relasi
4. **Timestamps**: Setiap tabel memiliki `created_at` dan `updated_at` untuk audit trail
5. **Kode Unik**: Kolom `kode` pada `vendor` dan `barang` harus unik untuk menghindari duplikasi

