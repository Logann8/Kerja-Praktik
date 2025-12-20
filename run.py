import os
from app import create_app

# Ambil environment dari variabel environment atau default ke 'development'
config_name = os.environ.get('FLASK_ENV', 'development')

# Buat aplikasi menggunakan app factory
app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

