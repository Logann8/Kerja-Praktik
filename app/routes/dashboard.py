from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import func

from app import db
from app.models import Konsumen, Order, Setting


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    total_konsumen = Konsumen.query.count()
    total_order = Order.query.count()

    latest_orders = (
        db.session.query(Order, Konsumen)
        .join(Konsumen, Konsumen.id == Order.konsumen_id)
        .order_by(Order.tanggal_order.desc())
        .limit(5)
        .all()
    )

    aktivitas_pelanggan = (
        db.session.query(Konsumen.nama, func.count(Order.id))
        .join(Order, Order.konsumen_id == Konsumen.id)
        .group_by(Konsumen.id, Konsumen.nama)
        .order_by(func.count(Order.id).desc())
        .limit(5)
        .all()
    )

    raw_status_counts = dict(
        db.session.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )

    status_summary = {
        'Pending': int(raw_status_counts.get('Pending', 0) or 0),
        'Produksi': int(raw_status_counts.get('Proses', 0) or 0),
        'Selesai': int(raw_status_counts.get('Selesai', 0) or 0),
    }

    return render_template(
        "dashboard/index.html",
        total_konsumen=total_konsumen,
        total_order=total_order,
        latest_orders=latest_orders,
        aktivitas_pelanggan=aktivitas_pelanggan,
        status_summary=status_summary,
    )


@dashboard_bp.route("/notifikasi", methods=["GET", "POST"])
def kelola_notifikasi():
    setting = Setting.query.filter_by(key='inactive_customer_7_days').first()
    if not setting:
        setting = Setting(key='inactive_customer_7_days', value=True)
        db.session.add(setting)
        db.session.commit()

    if request.method == 'POST':
        is_active = request.form.get('inactive_customer_7_days') == 'on'
        setting.value = bool(is_active)
        db.session.commit()
        return redirect(url_for('dashboard.kelola_notifikasi'))

    return render_template(
        'notifikasi/index.html',
        inactive_customer_7_days=bool(setting.value),
    )
