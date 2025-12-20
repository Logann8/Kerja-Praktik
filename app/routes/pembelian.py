from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import or_, func
from decimal import Decimal
from datetime import date
from app import db
from app.models import Pembelian, DetailPembelian, Vendor, Barang
from app.forms.pembelian_form import PembelianForm

bp = Blueprint('pembelian', __name__)


@bp.route('/')
def index():
    """Menampilkan daftar semua pembelian"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Search functionality
    search = request.args.get('search', '')
    query = Pembelian.query
    
    if search:
        search_pattern = f'%{search}%'
        query = query.join(Vendor).filter(
            or_(
                func.lower(Pembelian.no_faktur).like(func.lower(search_pattern)),
                func.lower(Vendor.nama).like(func.lower(search_pattern))
            )
        )
    
    pembelians = query.order_by(Pembelian.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('pembelian/index.html', pembelians=pembelians, search=search)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    """Membuat transaksi pembelian baru"""
    form = PembelianForm()
    
    # Populate vendor choices
    vendors = Vendor.query.order_by(Vendor.nama).all()
    form.vendor_id.choices = [(v.id, f"{v.kode} - {v.nama}") for v in vendors]
    
    if request.method == 'POST':
        # Validasi form header
        if not form.validate():
            flash('Mohon lengkapi data pembelian!', 'danger')
            barangs = Barang.query.order_by(Barang.nama).all()
            return render_template('pembelian/create.html', form=form, vendors=vendors, barangs=barangs)
        
        # Ambil data detail dari form
        detail_data = request.form.getlist('detail_barang_id[]')
        detail_qty = request.form.getlist('detail_qty[]')
        detail_harga = request.form.getlist('detail_harga[]')
        
        # Validasi detail pembelian
        if not detail_data or len(detail_data) == 0:
            flash('Minimal harus ada 1 item barang!', 'danger')
            barangs = Barang.query.order_by(Barang.nama).all()
            return render_template('pembelian/create.html', form=form, vendors=vendors, barangs=barangs)
        
        # Cek apakah no_faktur sudah ada
        existing_pembelian = Pembelian.query.filter_by(no_faktur=form.no_faktur.data.strip()).first()
        if existing_pembelian:
            flash('No. faktur sudah digunakan. Silakan gunakan nomor faktur lain.', 'danger')
            barangs = Barang.query.order_by(Barang.nama).all()
            return render_template('pembelian/create.html', form=form, vendors=vendors, barangs=barangs)
        
        try:
            # Buat pembelian baru
            pembelian = Pembelian(
                no_faktur=form.no_faktur.data.strip(),
                vendor_id=form.vendor_id.data,
                tanggal=form.tanggal.data,
                keterangan=form.keterangan.data.strip() if form.keterangan.data else None,
                total=Decimal('0.00')
            )
            
            db.session.add(pembelian)
            db.session.flush()  # Untuk mendapatkan ID pembelian
            
            # Buat detail pembelian
            total = Decimal('0.00')
            for i, barang_id in enumerate(detail_data):
                if not barang_id or not detail_qty[i] or not detail_harga[i]:
                    continue
                
                try:
                    qty = Decimal(str(detail_qty[i]))
                    harga = Decimal(str(detail_harga[i]))
                    
                    if qty <= 0 or harga < 0:
                        raise ValueError('Qty dan harga harus lebih dari 0')
                    
                    subtotal = qty * harga
                    
                    detail = DetailPembelian(
                        pembelian_id=pembelian.id,
                        barang_id=int(barang_id),
                        qty=qty,
                        harga=harga,
                        subtotal=subtotal
                    )
                    
                    db.session.add(detail)
                    total += subtotal
                except (ValueError, TypeError) as e:
                    db.session.rollback()
                    flash(f'Data detail pembelian tidak valid: {str(e)}', 'danger')
                    barangs = Barang.query.order_by(Barang.nama).all()
                    return render_template('pembelian/create.html', form=form, vendors=vendors, barangs=barangs)
            
            # Update total pembelian
            pembelian.total = total
            
            db.session.commit()
            flash('Transaksi pembelian berhasil disimpan!', 'success')
            return redirect(url_for('pembelian.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    # Populate barang choices
    barangs = Barang.query.order_by(Barang.nama).all()
    
    return render_template('pembelian/create.html', form=form, vendors=vendors, barangs=barangs)


@bp.route('/<int:id>')
def detail(id):
    """Menampilkan detail pembelian"""
    pembelian = Pembelian.query.get_or_404(id)
    return render_template('pembelian/detail.html', pembelian=pembelian)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Menghapus pembelian"""
    pembelian = Pembelian.query.get_or_404(id)
    
    try:
        db.session.delete(pembelian)
        db.session.commit()
        flash('Pembelian berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('pembelian.index'))


@bp.route('/api/barang/<int:barang_id>')
def get_barang(barang_id):
    """API untuk mendapatkan data barang"""
    barang = Barang.query.get_or_404(barang_id)
    return jsonify({
        'id': barang.id,
        'kode': barang.kode,
        'nama': barang.nama,
        'satuan': barang.satuan,
        'harga_beli': float(barang.harga_beli) if barang.harga_beli else 0.0
    })


@bp.route('/laporan')
def laporan():
    """Halaman laporan pembelian dengan filter tanggal"""
    from datetime import datetime
    
    # Ambil parameter filter
    tanggal_mulai = request.args.get('tanggal_mulai', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    
    # Query dasar
    query = Pembelian.query
    
    # Filter berdasarkan tanggal
    if tanggal_mulai:
        try:
            tanggal_mulai_obj = datetime.strptime(tanggal_mulai, '%Y-%m-%d').date()
            query = query.filter(Pembelian.tanggal >= tanggal_mulai_obj)
        except ValueError:
            flash('Format tanggal mulai tidak valid!', 'danger')
            tanggal_mulai = ''
    
    if tanggal_akhir:
        try:
            tanggal_akhir_obj = datetime.strptime(tanggal_akhir, '%Y-%m-%d').date()
            query = query.filter(Pembelian.tanggal <= tanggal_akhir_obj)
        except ValueError:
            flash('Format tanggal akhir tidak valid!', 'danger')
            tanggal_akhir = ''
    
    # Jika tidak ada filter, tampilkan semua data
    pembelians = query.order_by(Pembelian.tanggal.desc(), Pembelian.created_at.desc()).all()
    
    # Hitung total
    total_keseluruhan = sum(float(p.total) for p in pembelians)
    jumlah_transaksi = len(pembelians)
    
    return render_template(
        'pembelian/laporan.html',
        pembelians=pembelians,
        tanggal_mulai=tanggal_mulai,
        tanggal_akhir=tanggal_akhir,
        total_keseluruhan=total_keseluruhan,
        jumlah_transaksi=jumlah_transaksi
    )
