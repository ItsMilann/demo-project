echo "running migrations and collecting static files"
# python manage.py collectstatic
python manage.py migrate
# uWSGI for better performance and production ready
uwsgi --ini uwsgi.ini --py-autoreload 1