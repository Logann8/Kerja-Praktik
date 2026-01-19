from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from datetime import datetime, timedelta, time
from sqlalchemy import case, func, literal

from app import db
from app.models import Konsumen, Order

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    range_param = (request.args.get("range", "month") or "month").strip().lower()
    if range_param not in ("today", "week", "month"):
        range_param = "month"

    today = datetime.now().date()
    if range_param == "today":
        start_date = datetime.combine(today, time.min)
        end_date = datetime.combine(today, time.max)
    elif range_param == "week":
        start_date = datetime.combine(today - timedelta(days=6), time.min)
        end_date = datetime.combine(today, time.max)
    else:
        first_day = today.replace(day=1)
        start_date = datetime.combine(first_day, time.min)
        end_date = datetime.combine(today, time.max)

    total_konsumen = Konsumen.query.count()
    total_order = Order.query.count()

    latest_orders = (
        db.session.query(Order, Konsumen)
        .join(Konsumen, Konsumen.id == Order.konsumen_id)
        .order_by(Order.tanggal_order.desc())
        .limit(5)
        .all()
    )

    latest_consumers = (
        Konsumen.query.order_by(Konsumen.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        range=range_param,
        total_konsumen=total_konsumen,
        total_order=total_order,
        latest_orders=latest_orders,
        latest_consumers=latest_consumers,
    )


