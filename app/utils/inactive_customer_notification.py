from app.utils.notification_service import generate_inactive_customer_notifications


def inactive_customer_notification():
    generate_inactive_customer_notifications(days=7)
