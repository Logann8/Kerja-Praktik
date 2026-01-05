from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp


class KonsumenForm(FlaskForm):
    nama = StringField(
        'Nama Konsumen',
        validators=[
            DataRequired(message='Nama Konsumen wajib diisi'),
            Length(max=100, message='Nama Konsumen maksimal 100 karakter'),
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan nama konsumen', 'required': True},
    )

    alamat = TextAreaField(
        'Alamat',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan alamat konsumen', 'rows': 3},
    )

    telepon = StringField(
        'No Telepon',
        validators=[
            Optional(),
            Regexp(
                r'^[0-9+()\-\s]*$',
                message='No Telepon hanya boleh berisi angka dan karakter +() -',
            ),
            Length(max=20, message='No Telepon maksimal 20 karakter'),
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan nomor telepon'},
    )

    email = StringField(
        'Email',
        validators=[
            Optional(),
            Email(message='Format email tidak valid'),
            Length(max=100, message='Email maksimal 100 karakter'),
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan email', 'type': 'email'},
    )
