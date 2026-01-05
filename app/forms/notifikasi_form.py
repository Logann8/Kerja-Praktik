from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField


class NotifikasiSettingForm(FlaskForm):
    inactive_customer_7_days = BooleanField(
        'Aktifkan notifikasi konsumen tidak order ≥ 7 hari',
        render_kw={'class': 'form-check-input', 'role': 'switch'},
    )

    submit = SubmitField('Simpan', render_kw={'class': 'btn btn-primary'})
