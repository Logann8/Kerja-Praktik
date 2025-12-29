from flask import Blueprint, redirect, render_template, request, url_for
from datetime import datetime, timedelta, time
from sqlalchemy import case, func, literal

from app import db
from app.models import Konsumen, Order, Setting


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
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

    total_order, pending_count, produksi_count, selesai_count = (
        db.session.query(
            func.count(Order.id),
            func.sum(case((Order.status == 'Pending', 1), else_=0)),
            func.sum(case((Order.status == 'Proses', 1), else_=0)),
            func.sum(case((Order.status == 'Selesai', 1), else_=0)),
        )
        .filter(Order.tanggal_order.between(start_date, end_date))
        .one()
    )

    total_order = int(total_order or 0)
    status_summary = {
        'Pending': int(pending_count or 0),
        'Produksi': int(produksi_count or 0),
        'Selesai': int(selesai_count or 0),
    }

    latest_orders = (
        db.session.query(Order, Konsumen)
        .join(Konsumen, Konsumen.id == Order.konsumen_id)
        .filter(Order.tanggal_order.between(start_date, end_date))
        .order_by(Order.tanggal_order.desc())
        .limit(5)
        .all()
    )

    aktivitas_pelanggan = (
        db.session.query(Konsumen.nama, func.count(Order.id))
        .join(Order, Order.konsumen_id == Konsumen.id)
        .filter(Order.tanggal_order.between(start_date, end_date))
        .group_by(Konsumen.id, Konsumen.nama)
        .order_by(func.count(Order.id).desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        range=range_param,
        start_date=start_date,
        end_date=end_date,
        order_pending=status_summary['Pending'],
        order_produksi=status_summary['Produksi'],
        order_selesai=status_summary['Selesai'],
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

    tab = (request.args.get('tab', 'all') or 'all').strip().lower()
    if tab not in ('all', 'inactive', 'never'):
        tab = 'all'

    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    per_page = request.args.get('per_page', 10, type=int)
    if per_page not in (5, 10, 20, 50):
        per_page = 10

    cutoff = datetime.utcnow().date() - timedelta(days=7)

    last_order_sq = (
        db.session.query(
            Order.konsumen_id.label('konsumen_id'),
            func.max(Order.tanggal_order).label('last_order'),
        )
        .group_by(Order.konsumen_id)
        .subquery()
    )

    inactive_q = (
        db.session.query(
            Konsumen.id.label('konsumen_id'),
            Konsumen.nama.label('nama'),
            last_order_sq.c.last_order.label('last_order'),
            literal('Tidak Order 7 Hari').label('status'),
            last_order_sq.c.last_order.label('sort_date'),
        )
        .join(last_order_sq, last_order_sq.c.konsumen_id == Konsumen.id)
        .filter(last_order_sq.c.last_order < cutoff)
    )

    never_q = (
        db.session.query(
            Konsumen.id.label('konsumen_id'),
            Konsumen.nama.label('nama'),
            literal(None).label('last_order'),
            literal('Belum Pernah Order').label('status'),
            Konsumen.created_at.label('sort_date'),
        )
        .outerjoin(last_order_sq, last_order_sq.c.konsumen_id == Konsumen.id)
        .filter(last_order_sq.c.last_order.is_(None))
    )

    if tab == 'inactive':
        base_q = inactive_q
    elif tab == 'never':
        base_q = never_q
    else:
        base_q = inactive_q.union_all(never_q)

    total_items = int(db.session.query(func.count()).select_from(base_q.subquery()).scalar() or 0)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages

    notif_rows = (
        base_q.order_by(db.desc('sort_date'))
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    return render_template(
        'notifikasi/index.html',
        inactive_customer_7_days=bool(setting.value),
        tab=tab,
        notif_rows=notif_rows,
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
    )


@dashboard_bp.route('/kelola-notifikasi')
def kelola_notifikasi_alias():
    return redirect(url_for('dashboard.kelola_notifikasi'))
