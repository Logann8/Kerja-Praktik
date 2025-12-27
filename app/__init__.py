from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Inisialisasi ekstensi
db = SQLAlchemy()


def create_app(config_name='development'):
    """
    App Factory Pattern untuk membuat instance Flask
    
    Args:
        config_name: Nama konfigurasi yang digunakan (development, production, testing)
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Load konfigurasi
    app.config.from_object(config[config_name])
    
    # Inisialisasi ekstensi dengan app
    db.init_app(app)
    
    # Register blueprints
    from app.routes import laporan, dashboard, konsumen, order
    
    app.register_blueprint(konsumen.bp, url_prefix='/konsumen')
    app.register_blueprint(order.bp, url_prefix='/order')
    app.register_blueprint(laporan.bp)
    app.register_blueprint(dashboard.dashboard_bp)
    
    # Root route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('konsumen.index'))
    
    # Create database tables
    with app.app_context():
        db.create_all()

        from app.models import Setting

        if not Setting.query.filter_by(key='inactive_customer_7_days').first():
            db.session.add(Setting(key='inactive_customer_7_days', value=True))
            db.session.commit()

    @app.context_processor
    def inject_unread_notifications():
        from app.models import NotifikasiInternal
        from app.utils.notification_service import generate_inactive_customer_notifications

        generate_inactive_customer_notifications()

        unread_notifications = (
            NotifikasiInternal.query.filter_by(is_read=False)
            .order_by(NotifikasiInternal.created_at.desc())
            .limit(5)
            .all()
        )
        unread_notifications_count = (
            NotifikasiInternal.query.filter_by(is_read=False).count()
        )

        return {
            'unread_notifications': unread_notifications,
            'unread_notifications_count': unread_notifications_count,
        }
    
    return app

