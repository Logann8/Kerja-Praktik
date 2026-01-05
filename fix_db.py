import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'app.db')

def fix_database():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column exists to avoid error if run multiple times
        cursor.execute("PRAGMA table_info(orders)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'barang_id' in columns:
            print("Column 'barang_id' already exists in 'orders' table.")
        else:
            print("Adding 'barang_id' column to 'orders' table...")
            cursor.execute("ALTER TABLE orders ADD COLUMN barang_id INTEGER")
            conn.commit()
            print("Successfully added 'barang_id' column.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()
