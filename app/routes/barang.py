from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_, func
from decimal import Decimal
from app import db
from app.models import Barang
from app.forms.barang_form import BarangForm

bp = Blueprint('barang', __name__)


@bp.route('/')
def index():
    """Menampilkan daftar semua barang"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Search functionality
    search = request.args.get('search', '')
    query = Barang.query
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                func.lower(Barang.kode).like(func.lower(search_pattern)),
                func.lower(Barang.nama).like(func.lower(search_pattern))
            )
        )
    
    barangs = query.order_by(Barang.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('barang/index.html', barangs=barangs, search=search)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    """Membuat barang baru"""
    form = BarangForm()
    
    if form.validate_on_submit():
        # Cek apakah kode sudah ada
        existing_barang = Barang.query.filter_by(kode=form.kode.data).first()
        if existing_barang:
            flash('Kode barang sudah digunakan. Silakan gunakan kode lain.', 'danger')
            return render_template('barang/create.html', form=form)
        
        # Buat barang baru
        barang = Barang(
            kode=form.kode.data.strip().upper(),
            nama=form.nama.data.strip(),
            satuan=form.satuan.data.strip(),
            harga_beli=Decimal(str(form.harga_beli.data)) if form.harga_beli.data else Decimal('0.00')
        )
        
        try:
            db.session.add(barang)
            db.session.commit()
            flash('Barang berhasil ditambahkan!', 'success')
            return redirect(url_for('barang.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('barang/create.html', form=form)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Mengedit barang"""
    barang = Barang.query.get_or_404(id)
    form = BarangForm(obj=barang)
    
    if form.validate_on_submit():
        # Cek apakah kode sudah digunakan barang lain
        existing_barang = Barang.query.filter(
            Barang.kode == form.kode.data.strip().upper(),
            Barang.id != id
        ).first()
        
        if existing_barang:
            flash('Kode barang sudah digunakan. Silakan gunakan kode lain.', 'danger')
            return render_template('barang/edit.html', form=form, barang=barang)
        
        # Update barang
        barang.kode = form.kode.data.strip().upper()
        barang.nama = form.nama.data.strip()
        barang.satuan = form.satuan.data.strip()
        barang.harga_beli = Decimal(str(form.harga_beli.data)) if form.harga_beli.data else Decimal('0.00')
        
        try:
            db.session.commit()
            flash('Barang berhasil diupdate!', 'success')
            return redirect(url_for('barang.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('barang/edit.html', form=form, barang=barang)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Menghapus barang"""
    barang = Barang.query.get_or_404(id)
    
    # Cek apakah barang memiliki detail pembelian
    if barang.detail_pembelians:
        flash('Barang tidak dapat dihapus karena masih digunakan dalam transaksi pembelian!', 'danger')
        return redirect(url_for('barang.index'))
    
    try:
        db.session.delete(barang)
        db.session.commit()
        flash('Barang berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('barang.index'))

