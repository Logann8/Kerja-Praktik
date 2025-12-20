import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Konfigurasi dasar aplikasi"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # ==============================
    # DEFAULT: SQLITE (AMAN UNTUK TESTING)
    # ==============================
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Pagination
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """Konfigurasi untuk development (MySQL Laragon)"""
    DEBUG = True

    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'pembelian_db'

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Konfigurasi untuk production"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Konfigurasi untuk testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Dictionary untuk memilih konfigurasi
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}
