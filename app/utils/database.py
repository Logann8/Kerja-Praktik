from app import db


def init_db():
    """Inisialisasi database dan membuat semua tabel"""
    db.create_all()
    print("Database initialized successfully!")


def drop_db():
    """Menghapus semua tabel dari database"""
    db.drop_all()
    print("All tables dropped successfully!")

