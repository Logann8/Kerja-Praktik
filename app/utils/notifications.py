from datetime import date, timedelta

from sqlalchemy import func, or_

from app import db
from app.models import Konsumen, Order, Setting


def get_inactive_customers(days=7):
    setting = Setting.query.filter_by(key='inactive_customer_7_days').first()
    if not setting or not bool(setting.value):
        return []

    cutoff = date.today() - timedelta(days=int(days))

    last_order_sq = (
        db.session.query(
            Order.konsumen_id.label('konsumen_id'),
            func.max(Order.tanggal_order).label('last_order'),
        )
        .group_by(Order.konsumen_id)
        .subquery()
    )

    rows = (
        db.session.query(Konsumen)
        .outerjoin(last_order_sq, last_order_sq.c.konsumen_id == Konsumen.id)
        .filter(
            or_(
                last_order_sq.c.last_order.is_(None),
                last_order_sq.c.last_order < cutoff,
            )
        )
        .all()
    )

    return rows
