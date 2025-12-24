import csv
from io import BytesIO, StringIO

from flask import Blueprint, Response, render_template, send_file
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app import db
from app.models import Konsumen, Order

bp = Blueprint('laporan', __name__, url_prefix='/laporan')


@bp.route('/konsumen', methods=['GET'])
def konsumen():
    konsumen = Konsumen.query.order_by(Konsumen.created_at.desc()).all()
    return render_template('laporan/konsumen.html', konsumen=konsumen)


@bp.route('/konsumen/csv', methods=['GET'])
def konsumen_csv():
    konsumen = Konsumen.query.order_by(Konsumen.created_at.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'nama', 'no_hp', 'alamat', 'created_at'])

    for k in konsumen:
        writer.writerow(
            [
                k.id,
                k.nama or '',
                k.telepon or '',
                k.alamat or '',
                k.created_at.isoformat() if getattr(k, 'created_at', None) else '',
            ]
        )

    filename = f"konsumen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
        },
    )


@bp.route('/cetak', methods=['GET'])
def cetak():
    konsumen_list = Konsumen.query.order_by(Konsumen.created_at.desc()).all()
    orders = Order.query.order_by(Order.tanggal_order.desc()).all()

    orders_by_konsumen = {}
    for o in orders:
        orders_by_konsumen.setdefault(o.konsumen_id, []).append(o)

    rows = []
    no = 0
    for k in konsumen_list:
        konsumen_orders = orders_by_konsumen.get(k.id) or []

        if not konsumen_orders:
            no += 1
            rows.append(
                {
                    'no': no,
                    'konsumen': k,
                    'order': None,
                }
            )
            continue

        for o in konsumen_orders:
            no += 1
            rows.append(
                {
                    'no': no,
                    'konsumen': k,
                    'order': o,
                }
            )

    return render_template(
        'laporan/cetak.html',
        tanggal_cetak=datetime.now(),
        rows=rows,
        total_konsumen=len(konsumen_list),
    )


@bp.route('/order/csv', methods=['GET'])
def order_csv():
    rows = (
        db.session.query(Order, Konsumen)
        .join(Konsumen, Konsumen.id == Order.konsumen_id)
        .order_by(Order.tanggal_order.desc())
        .all()
    )

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'konsumen_id', 'nama_konsumen', 'tanggal_order', 'status', 'jumlah', 'harga_satuan'])

    for o, k in rows:
        writer.writerow(
            [
                o.id,
                o.konsumen_id,
                k.nama or '',
                o.tanggal_order.isoformat() if o.tanggal_order else '',
                o.status or '',
                o.jumlah,
                str(o.harga_satuan) if o.harga_satuan is not None else '',
            ]
        )

    filename = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
        },
    )


@bp.route('/konsumen/pdf', methods=['GET'])
def konsumen_pdf():
    konsumen = Konsumen.query.order_by(Konsumen.created_at.desc()).all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
        title='Laporan Data Konsumen',
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph('Laporan Data Konsumen', styles['Title']))
    story.append(Spacer(1, 12))

    data = [['No', 'Nama', 'No HP', 'Alamat']]
    for i, k in enumerate(konsumen, start=1):
        data.append([
            str(i),
            (k.nama or ''),
            (k.telepon or '-'),
            (k.alamat or '-'),
        ])

    table = Table(data, colWidths=[30, 170, 120, 220], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(table)

    doc.build(story)
    buffer.seek(0)

    filename = f"laporan_konsumen_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf',
    )


@bp.route('/order/pdf', methods=['GET'])
def order_pdf():
    rows = (
        db.session.query(Order, Konsumen)
        .join(Konsumen, Konsumen.id == Order.konsumen_id)
        .order_by(Order.tanggal_order.desc())
        .all()
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
        title='Laporan Data Order Konsumen',
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph('Laporan Data Order Konsumen', styles['Title']))
    story.append(Spacer(1, 12))

    data = [['No', 'Nama Konsumen', 'Tanggal Order', 'Status', 'Jumlah']]
    for i, (o, k) in enumerate(rows, start=1):
        data.append(
            [
                str(i),
                (k.nama or ''),
                o.tanggal_order.strftime('%d-%m-%Y') if o.tanggal_order else '',
                (o.status or ''),
                str(o.jumlah),
            ]
        )

    table = Table(data, colWidths=[30, 180, 110, 90, 60], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(table)

    doc.build(story)
    buffer.seek(0)

    filename = f"laporan_order_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf',
    )

