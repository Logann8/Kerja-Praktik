from flask import Blueprint, render_template, send_file
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.models import Konsumen

bp = Blueprint('laporan', __name__, url_prefix='/laporan')


@bp.route('/konsumen', methods=['GET'])
def konsumen():
    konsumen = Konsumen.query.order_by(Konsumen.created_at.desc()).all()
    return render_template('laporan/konsumen.html', konsumen=konsumen)


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
    story.append(Paragraph('Aplikasi Pendataan Konsumen Internal Perusahaan', styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Tanggal cetak: {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 12))

    data = [['No', 'Nama Konsumen', 'Alamat', 'No Telepon', 'Email']]
    for i, k in enumerate(konsumen, start=1):
        data.append([
            str(i),
            (k.nama or ''),
            (k.alamat or '-'),
            (k.telepon or '-'),
            (k.email or '-'),
        ])

    table = Table(data, colWidths=[30, 130, 160, 95, 110], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 10))
    story.append(Paragraph(f'Total data tersimpan: {len(konsumen)} konsumen', styles['Normal']))

    doc.build(story)
    buffer.seek(0)

    filename = f"laporan_konsumen_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf',
    )

