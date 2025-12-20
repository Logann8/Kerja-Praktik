from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Inisialisasi ekstensi
db = SQLAlchemy()


def create_app(config_name='default'):
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
    from app.routes import pembelian, vendor, barang, laporan
    
    app.register_blueprint(pembelian.bp, url_prefix='/pembelian')
    app.register_blueprint(vendor.bp, url_prefix='/vendor')
    app.register_blueprint(barang.bp, url_prefix='/barang')
    app.register_blueprint(laporan.bp)
    
    # Root route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('vendor.index'))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

