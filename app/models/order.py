from datetime import datetime

from app import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    konsumen_id = db.Column(db.Integer, db.ForeignKey('konsumen.id'), nullable=False)
    barang_id = db.Column(db.Integer, db.ForeignKey('barang.id'), nullable=True) # Initially nullable for migration, but logic should enforce it
    tanggal_order = db.Column(db.DateTime, nullable=False)
    deskripsi = db.Column(db.String(255), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    harga_satuan = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Order {self.id} konsumen_id={self.konsumen_id}>'
