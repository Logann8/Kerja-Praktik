from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.forms.order_form import OrderForm
from app.forms.status_order_form import StatusOrderForm
from app.models.order import Order

bp = Blueprint('order', __name__)


@bp.route('/create', methods=['POST'])
def create():
    form = OrderForm()

    try:
        print('[ORDER.CREATE] called')
        print(f"[ORDER.CREATE] db_url={db.engine.url}")
        print(f"[ORDER.CREATE] form_data={form.data}")
    except Exception:
        pass

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
            try:
                print(f"[ORDER.CREATE] DB EXCEPTION: {repr(e)}")
            except Exception:
                pass
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    else:
        try:
            print(f"[ORDER.CREATE] form_errors={form.errors}")
        except Exception:
            pass
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


@bp.route('/<int:order_id>/status', methods=['GET', 'POST'])
def update_status(order_id):
    order = Order.query.get_or_404(order_id)

    try:
        print(f"[ORDER.STATUS] method={request.method}")
    except Exception:
        pass

    if request.method == 'GET':
        return_to_konsumen_id = request.args.get('konsumen_id', type=int) or order.konsumen_id
        form = StatusOrderForm(obj=order)
        db_to_form = {'Pending': 'pending', 'Proses': 'produksi', 'Selesai': 'selesai'}
        form.status.data = db_to_form.get(order.status, '')
        return render_template('order/status.html', order=order, konsumen_id=return_to_konsumen_id, form=form)

    form = StatusOrderForm()
    is_valid = form.validate_on_submit()
    if not is_valid:
        if 'csrf_token' not in request.form:
            form = StatusOrderForm(meta={'csrf': False})
            is_valid = form.validate()

    try:
        print(f"[ORDER.STATUS] form_status_data={form.status.data!r}")
    except Exception:
        pass

    if not is_valid:
        first_error = None
        for field_errors in form.errors.values():
            if field_errors:
                first_error = field_errors[0]
                break
        flash(first_error or 'Status wajib dipilih.', 'danger')
        return redirect(request.referrer or url_for('konsumen.index'))

    status = (form.status.data or '').strip()
    status_map = {
        'pending': 'Pending',
        'produksi': 'Proses',
        'selesai': 'Selesai',
        'Pending': 'Pending',
        'Proses': 'Proses',
        'Selesai': 'Selesai',
    }
    if status not in status_map:
        flash('Status tidak valid.', 'danger')
        return redirect(request.referrer or url_for('konsumen.index'))

    new_status = status_map[status]

    try:
        try:
            print(f"[ORDER.STATUS] before_commit order_status={order.status!r} -> new_status={new_status!r}")
        except Exception:
            pass
        order.status = new_status
        db.session.commit()
        try:
            print(f"[ORDER.STATUS] after_commit order_status={order.status!r}")
        except Exception:
            pass
        flash('Status order berhasil diupdate!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    next_url = (form.next.data or '').strip()
    if next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)

    return redirect(request.referrer or url_for('konsumen.index'))


@bp.route('/<int:order_id>/status/ajax', methods=['POST'])
def update_status_ajax(order_id):
    order = Order.query.get_or_404(order_id)

    status = (request.form.get('status') or '').strip()
    allowed_status = {'Pending', 'Proses', 'Selesai'}

    if not status:
        flash('Status wajib dipilih.', 'danger')
        return konsumen(order.konsumen_id), 400

    if status not in allowed_status:
        flash('Status tidak valid.', 'danger')
        return konsumen(order.konsumen_id), 400

    try:
        order.status = status
        db.session.commit()
        flash('Status order berhasil diupdate!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return konsumen(order.konsumen_id), 500

    return konsumen(order.konsumen_id)
