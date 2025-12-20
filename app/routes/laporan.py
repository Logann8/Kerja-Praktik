from flask import Blueprint, render_template, request

bp = Blueprint('laporan', __name__, url_prefix='/laporan')


@bp.route('/pembelian', methods=['GET'])
def pembelian():
    tanggal_awal = request.args.get('tanggal_awal')
    tanggal_akhir = request.args.get('tanggal_akhir')
    return render_template('laporan/pembelian.html')

