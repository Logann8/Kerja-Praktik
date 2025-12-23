from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, HiddenField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, Length, NumberRange


class OrderForm(FlaskForm):
    konsumen_id = HiddenField(validators=[DataRequired(message='Konsumen wajib dipilih')])

    tanggal_order = DateField(
        'Tanggal Order',
        validators=[DataRequired(message='Tanggal Order wajib diisi')],
        render_kw={'class': 'form-control', 'type': 'date'},
    )

    deskripsi = StringField(
        'Nama Barang / Deskripsi',
        validators=[
            DataRequired(message='Nama Barang / Deskripsi wajib diisi'),
            Length(max=255, message='Deskripsi maksimal 255 karakter'),
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan nama barang / deskripsi'},
    )

    jumlah = IntegerField(
        'Jumlah',
        validators=[
            DataRequired(message='Jumlah wajib diisi'),
            NumberRange(min=1, message='Jumlah minimal 1'),
        ],
        render_kw={'class': 'form-control', 'min': 1, 'step': 1},
    )

    harga_satuan = DecimalField(
        'Harga Satuan',
        places=2,
        validators=[
            DataRequired(message='Harga Satuan wajib diisi'),
            NumberRange(min=0, message='Harga Satuan tidak boleh negatif'),
        ],
        render_kw={'class': 'form-control', 'min': 0, 'step': '0.01'},
    )

    status = SelectField(
        'Status',
        choices=[('Pending', 'Pending'), ('Proses', 'Proses'), ('Selesai', 'Selesai')],
        default='Pending',
        validators=[DataRequired(message='Status wajib dipilih')],
        render_kw={'class': 'form-select'},
    )
