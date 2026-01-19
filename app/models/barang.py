from datetime import datetime
from decimal import Decimal
from app import db


class Barang(db.Model):
    """Model untuk tabel barang (CSV Mirror)"""
    __tablename__ = 'barang'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Fields sesuai permintaan user
    kode_barang = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama_barang = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50))
    stok = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(20))
    minimum = db.Column(db.Integer)
    status = db.Column(db.String(20))
    harga_beli = db.Column(db.Integer, default=0)
    harga_jual = db.Column(db.Integer, default=0)
    
    last_sync_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Aliases for backward compatibility (if needed by Order)
    @property
    def kode(self):
        return self.kode_barang
    
    @property
    def nama(self):
        return self.nama_barang
        
    @property
    def satuan(self):
        return self.unit
    
    # Relasi one-to-many dengan DetailPembelian (jika ada)
    # detail_pembelians = db.relationship('DetailPembelian', backref='barang', lazy=True)
    
    def __repr__(self):
        return f'<Barang {self.kode_barang}: {self.nama_barang}>'
    
    def to_dict(self):
        """Mengkonversi model ke dictionary"""
        return {
            'id': self.id,
            'kode_barang': self.kode_barang,
            'nama_barang': self.nama_barang,
            'kategori': self.kategori,
            'stok': self.stok,
            'unit': self.unit,
            'minimum': self.minimum,
            'status': self.status,
            'harga_beli': self.harga_beli,
            'harga_jual': self.harga_jual,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None
        }
