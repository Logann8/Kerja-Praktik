from datetime import datetime
from decimal import Decimal
from app import db


class DetailPembelian(db.Model):
    """Model untuk tabel detail_pembelian"""
    __tablename__ = 'detail_pembelian'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pembelian_id = db.Column(db.Integer, db.ForeignKey('pembelian.id', ondelete='CASCADE'), nullable=False)
    barang_id = db.Column(db.Integer, db.ForeignKey('barang.id', ondelete='RESTRICT'), nullable=False)
    qty = db.Column(db.Numeric(10, 2), nullable=False)
    harga = db.Column(db.Numeric(15, 2), nullable=False)
    subtotal = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<DetailPembelian {self.id}: {self.qty} x {self.harga} = {self.subtotal}>'
    
    def to_dict(self):
        """Mengkonversi model ke dictionary"""
        return {
            'id': self.id,
            'pembelian_id': self.pembelian_id,
            'barang_id': self.barang_id,
            'barang': self.barang.to_dict() if self.barang else None,
            'qty': float(self.qty) if self.qty else 0.0,
            'harga': float(self.harga) if self.harga else 0.0,
            'subtotal': float(self.subtotal) if self.subtotal else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_subtotal(self):
        """Menghitung subtotal dari qty dan harga"""
        self.subtotal = Decimal(str(self.qty)) * Decimal(str(self.harga))
        return self.subtotal

