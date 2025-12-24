from flask import Blueprint, render_template
from sqlalchemy import func

from app import db
from app.models import Konsumen, Order


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    total_konsumen = db.session.query(func.count(Konsumen.id)).scalar() or 0
    total_order = db.session.query(func.count(Order.id)).scalar() or 0

    latest_orders = (
        db.session.query(Order, Konsumen)
        .join(Konsumen, Konsumen.id == Order.konsumen_id)
        .order_by(Order.tanggal_order.desc())
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
        status_summary=status_summary,
    )
