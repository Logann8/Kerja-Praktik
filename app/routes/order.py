from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, url_for

from app import db
from app.forms.order_form import OrderForm
from app.models.order import Order

bp = Blueprint('order', __name__)


@bp.route('/create', methods=['POST'])
def create():
    form = OrderForm()

    if form.validate_on_submit():
        tanggal = form.tanggal_order.data
        tanggal_dt = datetime.combine(tanggal, datetime.min.time())

        order = Order(
            konsumen_id=int(form.konsumen_id.data),
            tanggal_order=tanggal_dt,
            deskripsi=form.deskripsi.data.strip(),
            jumlah=int(form.jumlah.data),
            harga_satuan=form.harga_satuan.data,
            status=form.status.data or 'Pending',
        )

        try:
            db.session.add(order)
            db.session.commit()
            flash('Order berhasil ditambahkan!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    else:
        first_error = None
        for field_errors in form.errors.values():
            if field_errors:
                first_error = field_errors[0]
                break
        flash(first_error or 'Data order tidak valid', 'danger')

    return redirect(url_for('konsumen.index'))


@bp.route('/konsumen/<int:konsumen_id>')
def konsumen(konsumen_id):
    orders = Order.query.filter_by(konsumen_id=konsumen_id).order_by(Order.tanggal_order.desc()).all()
    
    total_keseluruhan = sum(order.jumlah * order.harga_satuan for order in orders)
    
    return render_template('order/detail_modal_body.html', 
                         orders=orders, 
                         total_keseluruhan=total_keseluruhan)
