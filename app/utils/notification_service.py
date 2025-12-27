from datetime import datetime

from sqlalchemy import func

from app import db
from app.models import AppSetting, NotifikasiInternal
from app.utils.notifications import get_inactive_customers


def generate_inactive_customer_notifications(days=7):
    setting = AppSetting.query.filter_by(key='inactive_customer_7_days').first()
    if not setting or not bool(setting.value):
        return

    today = datetime.utcnow().date()
    existing = (
        NotifikasiInternal.query.filter_by(tipe='inactive_customer')
        .filter(func.date(NotifikasiInternal.created_at) == today)
        .first()
    )
    if existing:
        return

    candidates = get_inactive_customers(days=days)
    total = len(candidates)
    if total <= 0:
        return

    notif = NotifikasiInternal(
        tipe='inactive_customer',
        judul='Konsumen Tidak Aktif',
        pesan=f'Terdapat {total} konsumen yang tidak melakukan order lebih dari {int(days)} hari',
        is_read=False,
    )
    db.session.add(notif)
    db.session.commit()
