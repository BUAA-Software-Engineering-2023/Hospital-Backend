python manage.py makemigrations&&
python manage.py migrate&&
uwsgi --ini /project/app/uwsgi.ini