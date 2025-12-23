 # Desain Database - Pendataan Konsumen
 
 Dokumen ini menjelaskan struktur tabel database yang dibutuhkan untuk aplikasi pendataan konsumen internal perusahaan.
 
 ## 1. Tabel `konsumen`
 
 Tabel untuk menyimpan data konsumen.
 
 | Nama Kolom | Tipe Data | Constraints | Keterangan |
 |------------|-----------|-------------|------------|
 | id | INT | PRIMARY KEY, AUTO_INCREMENT | ID unik konsumen |
 | nama | VARCHAR(100) | NOT NULL | Nama konsumen |
 | alamat | TEXT | NULL | Alamat konsumen |
 | telepon | VARCHAR(20) | NULL | Nomor telepon konsumen |
 | email | VARCHAR(100) | NULL | Email konsumen |
 | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Waktu pembuatan record |
 | updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Waktu update terakhir |
 
 **Index:**
 - PRIMARY KEY: `id`
 - INDEX: `nama`
 - INDEX: `email`

