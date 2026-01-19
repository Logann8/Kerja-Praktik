from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from sqlalchemy import func
from app import db
from app.models import Barang
import csv
import io
from datetime import datetime

bp = Blueprint('barang', __name__)

@bp.route('/')
@login_required
def index():
    """Menampilkan daftar barang (Read Only)"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = request.args.get('q', '')
    
    barang_query = Barang.query
    
    if query:
        search = f"%{query}%"
        barang_query = barang_query.filter(
            (Barang.nama_barang.like(search)) |
            (Barang.kode_barang.like(search)) |
            (Barang.kategori.like(search))
        )
    
    barang_pagination = barang_query.order_by(Barang.nama_barang.asc()).paginate(
        page=page, per_page=per_page
    )
    
    # Statistics
    stats = {
        'total_items': Barang.query.count(),
        'low_stock': Barang.query.filter(Barang.stok <= Barang.minimum).count(),
        'total_asset_value': db.session.query(func.sum(Barang.stok * Barang.harga_beli)).scalar() or 0,
        'total_stock_volume': db.session.query(func.sum(Barang.stok)).scalar() or 0
    }

    return render_template(
        'barang/index.html',
        barangs=barang_pagination.items,
        pagination=barang_pagination,
        search_query=query,
        stats=stats
    )

@bp.route('/import', methods=['POST'])
@login_required
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
            
            # Expected Headers:
            # "Kode Barang","Nama Barang","Kategori","Stok","Unit","Minimum","Status","Harga Beli","Harga Jual"
            
            success_count = 0
            skip_count = 0
            
            for row in csv_input:
                # Normalize keys (strip spaces, though csv reader usually handles header if quoted well)
                # We assume correct caching of headers by DictReader
                
                # Retrieve fields
                kode = row.get('Kode Barang')
                if not kode: 
                    continue
                
                # Check for existing
                existing = Barang.query.filter_by(kode_barang=kode).first()
                if existing:
                    # Update existing
                    existing.nama_barang = row.get('Nama Barang', existing.nama_barang)
                    existing.kategori = row.get('Kategori', existing.kategori)
                    existing.stok = int(row.get('Stok', existing.stok) or 0)
                    existing.unit = row.get('Unit', existing.unit)
                    existing.minimum = int(row.get('Minimum', existing.minimum) or 0)
                    existing.status = row.get('Status', existing.status)
                    existing.harga_beli = int(row.get('Harga Beli', existing.harga_beli) or 0)
                    existing.harga_jual = int(row.get('Harga Jual', existing.harga_jual) or 0)
                    existing.last_sync_at = datetime.utcnow()
                    skip_count += 1 # Count as updated/skipped for new insert count
                else:
                    # Insert new
                    new_barang = Barang(
                        kode_barang=kode,
                        nama_barang=row.get('Nama Barang', ''),
                        kategori=row.get('Kategori', 'Umum'),
                        stok=int(row.get('Stok', 0) or 0),
                        unit=row.get('Unit', 'Pcs'),
                        minimum=int(row.get('Minimum', 0) or 0),
                        status=row.get('Status', 'Aktif'),
                        harga_beli=int(row.get('Harga Beli', 0) or 0),
                        harga_jual=int(row.get('Harga Jual', 0) or 0),
                        last_sync_at=datetime.utcnow()
                    )
                    db.session.add(new_barang)
                    success_count += 1
            
            db.session.commit()
            flash(f'Import berhasil: {success_count} data baru ditambahkan. {skip_count} data dilewati (sudah ada).', 'success')
            
        except Exception as e:
            flash(f'Terjadi kesalahan saat import: {str(e)}', 'danger')
            
    else:
        flash('Format file harus CSV', 'danger')
        
    return redirect(url_for('barang.index'))

@bp.route('/<int:id>/detail_json')
@login_required
def detail_json(id):
    """API untuk mengambil detail barang (dipakai di form Order)"""
    barang = Barang.query.get_or_404(id)
    return jsonify(barang.to_dict())
