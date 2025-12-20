from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Optional


class VendorForm(FlaskForm):
    """Form untuk create dan edit vendor"""
    kode = StringField(
        'Kode Vendor',
        validators=[
            DataRequired(message='Kode vendor wajib diisi'),
            Length(max=20, message='Kode vendor maksimal 20 karakter')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan kode vendor'}
    )
    
    nama = StringField(
        'Nama Vendor',
        validators=[
            DataRequired(message='Nama vendor wajib diisi'),
            Length(max=100, message='Nama vendor maksimal 100 karakter')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan nama vendor'}
    )
    
    alamat = TextAreaField(
        'Alamat',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan alamat vendor', 'rows': 3}
    )
    
    telepon = StringField(
        'Telepon',
        validators=[
            Optional(),
            Length(max=20, message='Nomor telepon maksimal 20 karakter')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan nomor telepon'}
    )
    
    email = StringField(
        'Email',
        validators=[
            Optional(),
            Email(message='Format email tidak valid'),
            Length(max=100, message='Email maksimal 100 karakter')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan email vendor', 'type': 'email'}
    )

