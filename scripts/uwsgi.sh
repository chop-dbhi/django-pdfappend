#!/bin/bash

APP_DIR=/opt/app/

cd $APP_DIR

exec /usr/local/bin/uwsgi --enable-threads --die-on-term --http-socket :8000 -p 4 -b 32768 -T --master --max-requests 5000 --static-map /static=/opt/app/_site/static --module wsgi:application
