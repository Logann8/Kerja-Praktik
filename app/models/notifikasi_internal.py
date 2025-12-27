from datetime import datetime

from app import db


class NotifikasiInternal(db.Model):
    __tablename__ = 'notifikasi_internal'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipe = db.Column(db.String(50), nullable=False)
    judul = db.Column(db.String(255), nullable=False)
    pesan = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
