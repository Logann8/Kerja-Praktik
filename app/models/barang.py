from datetime import datetime
from decimal import Decimal
from app import db


class Barang(db.Model):
    """Model untuk tabel barang"""
    __tablename__ = 'barang'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kode = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama = db.Column(db.String(100), nullable=False)
    satuan = db.Column(db.String(20), nullable=False)
    harga_beli = db.Column(db.Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relasi one-to-many dengan DetailPembelian
    detail_pembelians = db.relationship('DetailPembelian', backref='barang', lazy=True)
    
    def __repr__(self):
        return f'<Barang {self.kode}: {self.nama}>'
    
    def to_dict(self):
        """Mengkonversi model ke dictionary"""
        return {
            'id': self.id,
            'kode': self.kode,
            'nama': self.nama,
            'satuan': self.satuan,
            'harga_beli': float(self.harga_beli) if self.harga_beli else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

