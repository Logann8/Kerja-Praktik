from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_, func
from decimal import Decimal
import csv
import io
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


@bp.route('/<int:id>/detail_json')
def detail_json(id):
    """Mengembalikan detail barang dalam format JSON"""
    barang = Barang.query.get_or_404(id)
    return {
        'id': barang.id,
        'kode': barang.kode,
        'nama': barang.nama,
        'satuan': barang.satuan,
        'stok': barang.stok,
        'harga_beli': float(barang.harga_beli)
    }


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


@bp.route('/import', methods=['POST'])
def import_csv():
    """Import data barang dari CSV"""
    if 'file' not in request.files:
        flash('Tidak ada file yang diupload', 'danger')
        return redirect(url_for('barang.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Tidak ada file yang dipilih', 'danger')
        return redirect(url_for('barang.index'))
    
    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.DictReader(stream)
            
            # Validasi header minimal yang sering digunakan
            # Sesuaikan dengan format CSV User: kode,nama,satuan,stok,harga_beli
            
            success_count = 0
            updated_count = 0
            
            for row in csv_input:
                # Normalisasi keys (lower case dan strip whitespace)
                row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                
                kode = row.get('kode')
                if not kode: 
                    continue
                    
                nama = row.get('nama', '')
                satuan = row.get('satuan', 'Pcs')
                
                # Parse stok
                try:
                    stok = int(row.get('stok', 0))
                except ValueError:
                    stok = 0
                    
                # Parse harga_beli
                try:
                    # Hapus Rp dan format ribuan jika ada
                    harga_raw = row.get('harga_beli', '0').replace('Rp', '').replace(',', '').replace('.', '')
                    if not harga_raw: harga_raw = '0'
                    harga_beli = Decimal(harga_raw)
                except Exception:
                    harga_beli = Decimal('0.00')
                    
                # Cek existing barang
                barang = Barang.query.filter_by(kode=kode.upper()).first()
                
                if barang:
                    # Update
                    # Hanya update jika ada data, atau update paksa stok?
                    # Sesuai diagram: Update Harga/Stok
                    if nama: barang.nama = nama
                    barang.stok = stok 
                    barang.harga_beli = harga_beli
                    if satuan: barang.satuan = satuan
                    updated_count += 1
                else:
                    # Create New
                    new_barang = Barang(
                        kode=kode.upper(),
                        nama=nama if nama else f"Barang {kode}",
                        satuan=satuan,
                        stok=stok,
                        harga_beli=harga_beli
                    )
                    db.session.add(new_barang)
                    success_count += 1
            
            db.session.commit()
            flash(f'Import berhasil! {success_count} barang baru, {updated_count} barang diupdate.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat import CSV: {str(e)}', 'danger')
            
    else:
        flash('Format file harus CSV', 'danger')
        
    return redirect(url_for('barang.index'))



