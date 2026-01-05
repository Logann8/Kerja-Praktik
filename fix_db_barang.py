import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'app.db')

def fix_database_barang():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(barang)")
        columns_info = cursor.fetchall()
        existing_columns = [info[1] for info in columns_info]
        print(f"Existing columns in 'barang': {existing_columns}")
        
        # Columns to check and add if missing
        # Format: (column_name, definition)
        columns_to_add = [
            ('stok', 'INTEGER DEFAULT 0'),
            ('satuan', 'VARCHAR(20) DEFAULT "Pcs"'),
            ('harga_beli', 'NUMERIC(15, 2) DEFAULT 0.00'),
            # created_at and updated_at might exist, but good to check others if needed.
            # Based on error only stok was explicitly mentioned, but let's be safe.
        ]

        for col_name, col_def in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding '{col_name}' column to 'barang' table...")
                try:
                    cursor.execute(f"ALTER TABLE barang ADD COLUMN {col_name} {col_def}")
                    print(f"Successfully added '{col_name}'.")
                except Exception as e:
                    print(f"Failed to add '{col_name}': {e}")
            else:
                print(f"Column '{col_name}' already exists.")
        
        conn.commit()
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_barang()
