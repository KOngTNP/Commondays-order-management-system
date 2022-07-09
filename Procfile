web: gunicorn Commondaysshop.wsgi:application --log-file - --log-level debug
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate