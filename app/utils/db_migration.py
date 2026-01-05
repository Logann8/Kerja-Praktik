from app import create_app, db
from sqlalchemy import text

def run_migration():
    app = create_app()
    with app.app_context():
        print("Starting migration...")
        
        # 1. Add stok to barang
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE barang ADD COLUMN stok INTEGER NOT NULL DEFAULT 0"))
                conn.commit()
            print("Successfully added 'stok' column to 'barang' table.")
        except Exception as e:
            print(f"Error adding 'stok' column (might already exist): {e}")

        # 2. Add barang_id to orders
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE orders ADD COLUMN barang_id INTEGER REFERENCES barang(id)"))
                conn.commit()
            print("Successfully added 'barang_id' column to 'orders' table.")
        except Exception as e:
            print(f"Error adding 'barang_id' column (might already exist): {e}")

        print("Migration completed.")

if __name__ == "__main__":
    run_migration()
