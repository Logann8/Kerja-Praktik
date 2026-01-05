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

    barang_id = SelectField(
        'Nama Barang',
        coerce=int,
        validators=[DataRequired(message='Barang wajib dipilih')],
        render_kw={'class': 'form-select', 'id': 'order_barang_id'},
    )

    # Deskripsi disimpan untuk backward compatibility atau catatan tambahan
    deskripsi = HiddenField('Deskripsi')

    jumlah = IntegerField(
        'Jumlah',
        validators=[
            DataRequired(message='Jumlah wajib diisi'),
            NumberRange(min=1, message='Jumlah minimal 1'),
        ],
        render_kw={'class': 'form-control', 'min': 1, 'step': 1, 'readonly': True, 'id': 'order_jumlah'},
    )

    harga_satuan = DecimalField(
        'Harga Satuan',
        places=2,
        validators=[
            DataRequired(message='Harga Satuan wajib diisi'),
            NumberRange(min=0, message='Harga Satuan tidak boleh negatif'),
        ],
        render_kw={'class': 'form-control', 'min': 0, 'step': '0.01', 'id': 'order_harga_satuan'},
    )

    status = SelectField(
        'Status',
        choices=[('Pending', 'Pending'), ('Proses', 'Proses'), ('Selesai', 'Selesai')],
        default='Pending',
        validators=[DataRequired(message='Status wajib dipilih')],
        render_kw={'class': 'form-select'},
    )
