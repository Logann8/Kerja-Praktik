from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import date


class PembelianForm(FlaskForm):
    """Form untuk header pembelian"""
    no_faktur = StringField(
        'No. Faktur',
        validators=[
            DataRequired(message='No. faktur wajib diisi'),
            Length(max=50, message='No. faktur maksimal 50 karakter')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Masukkan nomor faktur'}
    )
    
    vendor_id = SelectField(
        'Vendor',
        validators=[DataRequired(message='Vendor wajib dipilih')],
        coerce=int,
        render_kw={'class': 'form-select'}
    )
    
    tanggal = DateField(
        'Tanggal Pembelian',
        validators=[DataRequired(message='Tanggal wajib diisi')],
        default=date.today,
        render_kw={'class': 'form-control', 'type': 'date'}
    )
    
    keterangan = TextAreaField(
        'Keterangan',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'placeholder': 'Keterangan tambahan (opsional)', 'rows': 3}
    )

