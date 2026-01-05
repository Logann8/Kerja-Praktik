from datetime import datetime
from decimal import Decimal

from app import db


class Pembelian(db.Model):
    __tablename__ = 'pembelian'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    no_faktur = db.Column(db.String(50), unique=True, nullable=False, index=True)
    tanggal = db.Column(db.DateTime, nullable=False, index=True)
    konsumen_id = db.Column(db.Integer, db.ForeignKey('konsumen.id', ondelete='RESTRICT'), nullable=False)
    keterangan = db.Column(db.Text, nullable=True)
    total = db.Column(db.Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    details = db.relationship(
        'DetailPembelian',
        backref='pembelian',
        lazy=True,
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self):
        return f'<Pembelian {self.no_faktur}>'
