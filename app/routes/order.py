from datetime import datetime
import csv
import io

from flask import Blueprint, flash, redirect, render_template, request, url_for, Response
from flask_login import login_required

from app import db
from app.forms.order_form import OrderForm
from app.forms.status_order_form import StatusOrderForm
from app.models.order import Order

bp = Blueprint('order', __name__)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    form = OrderForm()
    # Populate choices for barang_id
    from app.models import Barang
    form.barang_id.choices = [(b.id, f"{b.kode} - {b.nama} (Stok: {b.stok})") for b in Barang.query.all()]

    try:
        print('[ORDER.CREATE] called')
        print(f"[ORDER.CREATE] db_url={db.engine.url}")
        print(f"[ORDER.CREATE] form_data={form.data}")
    except Exception:
        pass

    if form.validate_on_submit():
        # Otomatis set tanggal order ke waktu sekarang
        tanggal_dt = datetime.now()
        
        # Get selected barang for description
        barang = Barang.query.get(form.barang_id.data)
        deskripsi_barang = f"{barang.kode} - {barang.nama}" if barang else "Item Unknown"

        if int(form.jumlah.data) > barang.stok:
            flash(f'Stok tidak mencukupi! Tersedia: {barang.stok}', 'danger')
            return redirect(url_for('konsumen.index'))

        order = Order(
            konsumen_id=int(form.konsumen_id.data),
            barang_id=int(form.barang_id.data),
            tanggal_order=tanggal_dt,
            deskripsi=deskripsi_barang, # Use proper Item Name
            jumlah=int(form.jumlah.data),
            harga_satuan=barang.harga_jual, # Force use DB price
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
@login_required
def konsumen(konsumen_id):
    orders = Order.query.filter_by(konsumen_id=konsumen_id).order_by(Order.tanggal_order.desc()).all()
    
    total_keseluruhan = sum(order.jumlah * order.harga_satuan for order in orders)
    
    return render_template('order/detail_modal_body.html', 
                         orders=orders, 
                         total_keseluruhan=total_keseluruhan)


@bp.route('/<int:order_id>/status', methods=['GET', 'POST'])
@login_required
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
        # Update stok barang logic
        if order.status != new_status:
            from app.models.barang import Barang
            barang = Barang.query.get(order.barang_id)
            
            if barang:
                if new_status == 'Selesai' and order.status != 'Selesai':
                    # Kurangi stok jika status berubah jadi Selesai
                    barang.stok -= order.jumlah
                elif order.status == 'Selesai' and new_status != 'Selesai':
                    # Kembalikan stok jika status batal dari Selesai
                    barang.stok += order.jumlah

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
@login_required
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
        # Update stok barang logic
        if order.status != status:
            from app.models.barang import Barang
            barang = Barang.query.get(order.barang_id)
            
            if barang:
                if status == 'Selesai' and order.status != 'Selesai':
                    # Kurangi stok jika status berubah jadi Selesai
                    barang.stok -= order.jumlah
                elif order.status == 'Selesai' and status != 'Selesai':
                    # Kembalikan stok jika status batal dari Selesai
                    barang.stok += order.jumlah
        
        order.status = status
        db.session.commit()
        flash('Status order berhasil diupdate!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return konsumen(order.konsumen_id), 500

    return konsumen(order.konsumen_id)


@bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Hanya bisa batalkan Pending atau Proses
    if order.status not in ['Pending', 'Proses']:
        flash('Hanya order dengan status Pending atau Proses yang dapat dibatalkan.', 'danger')
        return redirect(request.referrer or url_for('konsumen.orders', id=order.konsumen_id))

    try:
        order.status = 'Dibatalkan'
        db.session.commit()
        flash('Order berhasil dibatalkan.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan saat membatalkan order: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('konsumen.orders', id=order.konsumen_id))


@bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete(order_id):
    order = Order.query.get_or_404(order_id)
    konsumen_id = order.konsumen_id
    
    # Restrict delete: Hanya status Selesai yang boleh dihapus
    if order.status != 'Selesai':
        flash('Hanya order dengan status "Selesai" yang dapat dihapus.', 'danger')
        return redirect(url_for('konsumen.orders', id=konsumen_id))

    try:
        db.session.delete(order)
        db.session.commit()
        flash('Order berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan saat menghapus order: {str(e)}', 'danger')

    return redirect(url_for('konsumen.orders', id=konsumen_id))


@bp.route('/export', methods=['GET'])
@login_required
def export_csv():
    """Export data penjualan ke CSV"""
    # Import needed models locally to avoid circular imports if any
    from app.models import Barang, Konsumen
    
    # Query all orders joined with Konsumen and Barang
    # Note: If relationships are not explicitly defined, we might need explicit joins
    # or just iterate. For simplicity and safety given current knowledge, we iterate.
    orders = Order.query.order_by(Order.tanggal_order.desc()).all()
    
    # Prepare CSV output
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'ID Order', 'Tanggal', 'Nama Konsumen', 'Kode Barang', 'Nama Barang', 
        'Jumlah', 'Harga Satuan', 'Total', 'Status', 'Deskripsi'
    ])
    
    for order in orders:
        # Fetch related data if not available via relationship
        # Safely get konsumen
        konsumen_nama = "Unknown"
        if order.konsumen_id:
            k = Konsumen.query.get(order.konsumen_id)
            if k: konsumen_nama = k.nama
            
        # Safely get barang
        barang_kode = "-"
        barang_nama = "-"
        if order.barang_id:
            b = Barang.query.get(order.barang_id)
            if b: 
                barang_kode = b.kode
                barang_nama = b.nama
        
        writer.writerow([
            order.id,
            order.tanggal_order.strftime('%Y-%m-%d'),
            konsumen_nama,
            barang_kode,
            barang_nama,
            order.jumlah,
            order.harga_satuan,
            order.jumlah * order.harga_satuan,
            order.status,
            order.deskripsi
        ])
        
    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=CSV_Data_Penjualan.csv"}
    )
