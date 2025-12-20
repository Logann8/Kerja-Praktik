from datetime import datetime
from app import db


class Vendor(db.Model):
    """Model untuk tabel vendor"""
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kode = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=True)
    telepon = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relasi one-to-many dengan Pembelian
    pembelians = db.relationship('Pembelian', backref='vendor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Vendor {self.kode}: {self.nama}>'
    
    def to_dict(self):
        """Mengkonversi model ke dictionary"""
        return {
            'id': self.id,
            'kode': self.kode,
            'nama': self.nama,
            'alamat': self.alamat,
            'telepon': self.telepon,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

