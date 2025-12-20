from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class BarangForm(FlaskForm):
    """Form untuk create dan edit barang"""
    kode = StringField(
        'Kode Barang',
        validators=[
            DataRequired(message='Kode barang wajib diisi'),
            Length(max=20, message='Kode barang maksimal 20 karakter')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan kode barang'}
    )
    
    nama = StringField(
        'Nama Barang',
        validators=[
            DataRequired(message='Nama barang wajib diisi'),
            Length(max=100, message='Nama barang maksimal 100 karakter')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan nama barang'}
    )
    
    satuan = StringField(
        'Satuan',
        validators=[
            DataRequired(message='Satuan wajib diisi'),
            Length(max=20, message='Satuan maksimal 20 karakter')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Contoh: pcs, kg, liter, dll'}
    )
    
    harga_beli = DecimalField(
        'Harga Beli',
        validators=[
            DataRequired(message='Harga beli wajib diisi'),
            NumberRange(min=0, message='Harga beli tidak boleh negatif')
        ],
        places=2,
        render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}
    )


