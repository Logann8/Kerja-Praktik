from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField
from wtforms.validators import DataRequired


class StatusOrderForm(FlaskForm):
    next = HiddenField()

    status = SelectField(
        'Status',
        choices=[('Pending', 'Pending'), ('Proses', 'Produksi'), ('Selesai', 'Selesai')],
        validators=[DataRequired(message='Status wajib dipilih')],
        render_kw={'class': 'form-select'},
    )
