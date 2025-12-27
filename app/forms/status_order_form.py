from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField
from wtforms.validators import DataRequired


class StatusOrderForm(FlaskForm):
    next = HiddenField()

    status = SelectField(
        'Status',
        choices=[('pending', 'Pending'), ('produksi', 'Produksi'), ('selesai', 'Selesai')],
        validators=[DataRequired(message='Status wajib dipilih')],
        render_kw={'class': 'form-select'},
    )
