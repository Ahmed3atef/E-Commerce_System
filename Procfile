release: python manage.py migrate
web: gunicorn ECOMMERCE.wsgi:application --bind 0.0.0.0:$PORT
