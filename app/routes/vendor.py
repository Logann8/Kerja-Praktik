from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_, func
from app import db
from app.models import Vendor
from app.forms.vendor_form import VendorForm

bp = Blueprint('vendor', __name__)


@bp.route('/')
def index():
    """Menampilkan daftar semua vendor"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Search functionality
    search = request.args.get('search', '')
    query = Vendor.query
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                func.lower(Vendor.kode).like(func.lower(search_pattern)),
                func.lower(Vendor.nama).like(func.lower(search_pattern))
            )
        )
    
    vendors = query.order_by(Vendor.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('vendor/index.html', vendors=vendors, search=search)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    """Membuat vendor baru"""
    form = VendorForm()
    
    if form.validate_on_submit():
        # Cek apakah kode sudah ada
        existing_vendor = Vendor.query.filter_by(kode=form.kode.data).first()
        if existing_vendor:
            flash('Kode vendor sudah digunakan. Silakan gunakan kode lain.', 'danger')
            return render_template('vendor/create.html', form=form)
        
        # Buat vendor baru
        vendor = Vendor(
            kode=form.kode.data.strip().upper(),
            nama=form.nama.data.strip(),
            alamat=form.alamat.data.strip() if form.alamat.data else None,
            telepon=form.telepon.data.strip() if form.telepon.data else None,
            email=form.email.data.strip() if form.email.data else None
        )
        
        try:
            db.session.add(vendor)
            db.session.commit()
            flash('Vendor berhasil ditambahkan!', 'success')
            return redirect(url_for('vendor.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('vendor/create.html', form=form)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Mengedit vendor"""
    vendor = Vendor.query.get_or_404(id)
    form = VendorForm(obj=vendor)
    
    if form.validate_on_submit():
        # Cek apakah kode sudah digunakan vendor lain
        existing_vendor = Vendor.query.filter(
            Vendor.kode == form.kode.data.strip().upper(),
            Vendor.id != id
        ).first()
        
        if existing_vendor:
            flash('Kode vendor sudah digunakan. Silakan gunakan kode lain.', 'danger')
            return render_template('vendor/edit.html', form=form, vendor=vendor)
        
        # Update vendor
        vendor.kode = form.kode.data.strip().upper()
        vendor.nama = form.nama.data.strip()
        vendor.alamat = form.alamat.data.strip() if form.alamat.data else None
        vendor.telepon = form.telepon.data.strip() if form.telepon.data else None
        vendor.email = form.email.data.strip() if form.email.data else None
        
        try:
            db.session.commit()
            flash('Vendor berhasil diupdate!', 'success')
            return redirect(url_for('vendor.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('vendor/edit.html', form=form, vendor=vendor)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Menghapus vendor"""
    vendor = Vendor.query.get_or_404(id)
    
    # Cek apakah vendor memiliki pembelian
    if vendor.pembelians:
        flash('Vendor tidak dapat dihapus karena masih memiliki data pembelian!', 'danger')
        return redirect(url_for('vendor.index'))
    
    try:
        db.session.delete(vendor)
        db.session.commit()
        flash('Vendor berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('vendor.index'))
