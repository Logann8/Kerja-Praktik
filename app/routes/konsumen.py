from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy import exists, func, or_

from app import db
from app.forms.konsumen_form import KonsumenForm
from app.forms.order_form import OrderForm
from app.forms.status_order_form import StatusOrderForm
from app.models import Konsumen, Order

bp = Blueprint('konsumen', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)

    form = KonsumenForm()
    order_form = OrderForm()
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

    return render_template('konsumen/index.html', konsumen=konsumen, q=q, filter=filter_value, form=form, order_form=order_form, status_form=status_form)


@bp.route('/create', methods=['POST'])
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
def orders(id):
    konsumen = Konsumen.query.get_or_404(id)
    orders = Order.query.filter_by(konsumen_id=id).order_by(Order.tanggal_order.desc()).all()
    return render_template('konsumen/orders.html', konsumen=konsumen, orders=orders)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    konsumen = Konsumen.query.get_or_404(id)

    has_order = db.session.query(exists().where(Order.konsumen_id == Konsumen.id)).filter(Konsumen.id == id).scalar()
    if has_order:
        flash('Konsumen tidak dapat dihapus karena masih memiliki order.', 'danger')
        return redirect(url_for('konsumen.index'))

    try:
        db.session.delete(konsumen)
        db.session.commit()
        flash('Konsumen berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return redirect(url_for('konsumen.index'))
