from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import func, or_

from app import db
from app.forms.konsumen_form import KonsumenForm
from app.models import Konsumen

bp = Blueprint('konsumen', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    search = request.args.get('search', '')
    query = Konsumen.query

    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                func.lower(Konsumen.nama).like(func.lower(search_pattern)),
                func.lower(func.coalesce(Konsumen.email, '')).like(func.lower(search_pattern)),
                func.lower(func.coalesce(Konsumen.telepon, '')).like(func.lower(search_pattern)),
            )
        )

    konsumen = query.order_by(Konsumen.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return render_template('konsumen/index.html', konsumen=konsumen, search=search)


@bp.route('/create', methods=['GET', 'POST'])
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
            return redirect(url_for('konsumen.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return render_template('konsumen/create.html', form=form)


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


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    konsumen = Konsumen.query.get_or_404(id)

    try:
        db.session.delete(konsumen)
        db.session.commit()
        flash('Konsumen berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return redirect(url_for('konsumen.index'))
