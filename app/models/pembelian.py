from datetime import datetime, date
from decimal import Decimal
from app import db


class Pembelian(db.Model):
    """Model untuk tabel pembelian"""
    __tablename__ = 'pembelian'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    no_faktur = db.Column(db.String(50), unique=True, nullable=False, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id', ondelete='RESTRICT'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False, default=date.today)
    total = db.Column(db.Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    keterangan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relasi one-to-many dengan DetailPembelian
    detail_pembelians = db.relationship('DetailPembelian', backref='pembelian', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Pembelian {self.no_faktur}: {self.total}>'
    
    def to_dict(self):
        """Mengkonversi model ke dictionary"""
        return {
            'id': self.id,
            'no_faktur': self.no_faktur,
            'vendor_id': self.vendor_id,
            'vendor': self.vendor.to_dict() if self.vendor else None,
            'tanggal': self.tanggal.isoformat() if self.tanggal else None,
            'total': float(self.total) if self.total else 0.0,
            'keterangan': self.keterangan,
            'detail_pembelians': [dp.to_dict() for dp in self.detail_pembelians] if self.detail_pembelians else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_total(self):
        """Menghitung ulang total dari detail pembelian"""
        total = Decimal('0.00')
        for detail in self.detail_pembelians:
            total += detail.subtotal
        self.total = total
        return total

