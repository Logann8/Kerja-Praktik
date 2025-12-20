from flask import Blueprint, render_template, request
from datetime import datetime
from app.models import Pembelian

bp = Blueprint('laporan', __name__, url_prefix='/laporan')


@bp.route('/pembelian', methods=['GET'])
def pembelian():
    tanggal_awal = request.args.get('tanggal_awal')
    tanggal_akhir = request.args.get('tanggal_akhir')
    
    query = Pembelian.query
    
    if tanggal_awal:
        tanggal_awal_obj = datetime.strptime(tanggal_awal, '%Y-%m-%d').date()
        query = query.filter(Pembelian.tanggal >= tanggal_awal_obj)
    
    if tanggal_akhir:
        tanggal_akhir_obj = datetime.strptime(tanggal_akhir, '%Y-%m-%d').date()
        query = query.filter(Pembelian.tanggal <= tanggal_akhir_obj)
    
    pembelians = query.all()
    
    grand_total = sum(float(p.total) for p in pembelians)
    
    return render_template('laporan/pembelian.html', 
                         tanggal_awal=tanggal_awal, 
                         tanggal_akhir=tanggal_akhir,
                         pembelians=pembelians,
                         grand_total=grand_total)

