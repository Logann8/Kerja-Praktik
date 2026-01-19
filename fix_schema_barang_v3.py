import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'app.db')

def fix_schema_barang_v3():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Starting Barang schema migration...")

        # 1. Rename existing table
        cursor.execute("ALTER TABLE barang RENAME TO barang_old")
        print("Renamed 'barang' to 'barang_old'.")

        # 2. Create new table with requested schema
        create_table_sql = """
        CREATE TABLE barang (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_barang VARCHAR(20) UNIQUE NOT NULL,
            nama_barang VARCHAR(100) NOT NULL,
            kategori VARCHAR(50),
            stok INTEGER NOT NULL DEFAULT 0,
            unit VARCHAR(20),
            minimum INTEGER,
            status VARCHAR(20),
            harga_beli INTEGER,
            harga_jual INTEGER,
            last_sync_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)
        print("Created new 'barang' table.")

        # 3. Copy data from old table
        # Map: kode -> kode_barang, nama -> nama_barang, stok -> stok, harga_beli -> harga_beli
        # satuan -> unit
        # Set default for others
        cursor.execute("SELECT id, kode, nama, stok, satuan, harga_beli, created_at, updated_at FROM barang_old")
        old_rows = cursor.fetchall()

        for row in old_rows:
            id_val, kode, nama, stok, satuan, harga_beli, created, updated = row
            
            # Convert harga_beli to integer (as requested)
            try:
                hb_int = int(float(harga_beli))
            except:
                hb_int = 0

            cursor.execute("""
                INSERT INTO barang (id, kode_barang, nama_barang, stok, unit, harga_beli, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_val, kode, nama, stok, satuan, hb_int, created, updated))
        
        print(f"Migrated {len(old_rows)} records.")
        
        conn.commit()
        print("Migration successful.")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema_barang_v3()
