from datetime import datetime
from app import db


class Konsumen(db.Model):
    __tablename__ = 'konsumen'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False, index=True)
    alamat = db.Column(db.Text, nullable=True)
    telepon = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Konsumen {self.id}: {self.nama}>'

    @property
    def nama_konsumen(self):
        return self.nama

    @nama_konsumen.setter
    def nama_konsumen(self, value):
        self.nama = value

    @property
    def no_hp(self):
        return self.telepon

    @no_hp.setter
    def no_hp(self, value):
        self.telepon = value

    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'nama_konsumen': self.nama,
            'alamat': self.alamat,
            'telepon': self.telepon,
            'no_hp': self.telepon,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
