import os
from app import create_app

# Ambil konfigurasi dari environment.
# Default dibuat aman untuk running lokal (SQLite) tanpa perlu MySQL.
config_name = os.environ.get('FLASK_CONFIG') or os.environ.get('FLASK_ENV') or 'default'

# Buat aplikasi menggunakan app factory
app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

