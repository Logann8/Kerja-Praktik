from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import exists, func, or_

from app import db
from app.forms.konsumen_form import KonsumenForm
from app.forms.order_form import OrderForm
from app.forms.status_order_form import StatusOrderForm
from app.models import Konsumen, Order

bp = Blueprint('konsumen', __name__)


@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)

    form = KonsumenForm()
    order_form = OrderForm()
    # Populate choices for initial render
    from app.models import Barang
    all_barang = Barang.query.order_by(Barang.nama_barang.asc()).all()
    # PENTING: Choices tetap diisi agar validasi form (validate_on_submit) berhasil
    order_form.barang_id.choices = [(b.id, b.nama_barang) for b in all_barang]
    
    status_form = StatusOrderForm()

    q = request.args.get('q', '')
    filter_value = request.args.get('filter', '')
    query = Konsumen.query

    if q:
        search_pattern = f'%{q}%'
        query = query.filter(
            or_(
                func.lower(Konsumen.nama).like(func.lower(search_pattern)),
                func.lower(func.coalesce(Konsumen.telepon, '')).like(func.lower(search_pattern)),
            )
        )

    if filter_value == 'memiliki_order':
        query = query.filter(
            exists().where(Order.konsumen_id == Konsumen.id)
        )
    elif filter_value == 'belum_order':
        query = query.filter(
            ~exists().where(Order.konsumen_id == Konsumen.id)
        )

    konsumen = query.order_by(Konsumen.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return render_template('konsumen/index.html', konsumen=konsumen, q=q, filter=filter_value, form=form, order_form=order_form, status_form=status_form, all_barang=all_barang)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    form = KonsumenForm()

    if form.validate_on_submit():
        konsumen = Konsumen(
            nama=form.nama.data.strip(),
            alamat=form.alamat.data.strip() if form.alamat.data else None,
            telepon=form.telepon.data.strip() if form.telepon.data else None,
            email=form.email.data.strip() if form.email.data else None,
        )

        try:
            db.session.add(konsumen)
            db.session.commit()
            flash('Konsumen berhasil ditambahkan!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')

        return redirect(url_for('konsumen.index'))

    first_error = None
    for field_errors in form.errors.values():
        if field_errors:
            first_error = field_errors[0]
            break
    flash(first_error or 'Data konsumen tidak valid', 'danger')
    return redirect(url_for('konsumen.index'))


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    konsumen = Konsumen.query.get_or_404(id)
    form = KonsumenForm(obj=konsumen)

    if form.validate_on_submit():
        konsumen.nama = form.nama.data.strip()
        konsumen.alamat = form.alamat.data.strip() if form.alamat.data else None
        konsumen.telepon = form.telepon.data.strip() if form.telepon.data else None
        konsumen.email = form.email.data.strip() if form.email.data else None

        try:
            db.session.commit()
            flash('Konsumen berhasil diupdate!', 'success')
            return redirect(url_for('konsumen.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return render_template('konsumen/edit.html', form=form, konsumen=konsumen)


@bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    konsumen = Konsumen.query.get_or_404(id)
    form = KonsumenForm()

    if form.validate_on_submit():
        konsumen.nama = form.nama.data.strip()
        konsumen.alamat = form.alamat.data.strip() if form.alamat.data else None
        konsumen.telepon = form.telepon.data.strip() if form.telepon.data else None
        konsumen.email = form.email.data.strip() if form.email.data else None

        try:
            db.session.commit()
            flash('Konsumen berhasil diupdate!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')

        return redirect(url_for('konsumen.index'))

    first_error = None
    for field_errors in form.errors.values():
        if field_errors:
            first_error = field_errors[0]
            break
    flash(first_error or 'Data konsumen tidak valid', 'danger')
    return redirect(url_for('konsumen.index'))


@bp.route('/<int:id>/orders', methods=['GET'])
@login_required
def orders(id):
    konsumen = Konsumen.query.get_or_404(id)
    orders = Order.query.filter_by(konsumen_id=id).order_by(Order.tanggal_order.desc()).all()
    return render_template('konsumen/orders.html', konsumen=konsumen, orders=orders)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    konsumen = Konsumen.query.get_or_404(id)

    order_count = Order.query.filter_by(konsumen_id=id).count()
    print("[DELETE KONSUMEN]", konsumen.id, "order:", order_count)

    if order_count > 0:
        flash('Konsumen tidak dapat dihapus karena masih memiliki order', 'danger')
        return redirect(request.referrer or url_for('konsumen.index'))

    try:
        db.session.delete(konsumen)
        db.session.commit()
        flash('Konsumen berhasil dihapus', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan saat menghapus konsumen: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('konsumen.index'))
