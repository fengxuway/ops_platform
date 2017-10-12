#!/bin/bash

set -e
#cd /opt/ops_platform

#git stash
#git pull origin python3:python3
#
#pip3 install -r requirements.txt


: ${DB_HOST:=127.0.0.1}
if [ -n "$DB_HOST" ]; then
    sed -i "s@#DB_HOST#@$DB_HOST@g" ntdeploy/settings.py.template
fi

: ${DB_NAME:=ntdeploy}
if [ -n "$DB_NAME" ]; then
    sed -i "s@#DB_NAME#@$DB_NAME@g" ntdeploy/settings.py.template
fi

: ${DB_USER:=ntdeploy}
if [ -n "$DB_USER" ]; then
    sed -i "s@#DB_USER#@$DB_USER@g" ntdeploy/settings.py.template
fi

: ${DB_PASSWORD:=ntdeploy}
if [ -n "$DB_PASSWORD" ]; then
    sed -i "s@#DB_PASSWORD#@$DB_PASSWORD@g" ntdeploy/settings.py.template
fi

: ${DB_PORT:=3306}
if [ -n "$DB_PORT" ]; then
    sed -i "s@#DB_PORT#@$DB_PORT@g" ntdeploy/settings.py.template
fi

: ${REDIS_SERVER:=127.0.0.1}
if [ -n "$REDIS_SERVER" ]; then
    sed -i "s@#REDIS_SERVER#@$REDIS_SERVER@g" ntdeploy/celery.py.template
fi

: ${REDIS_PORT:=6379}
if [ -n "$REDIS_PORT" ]; then
    sed -i "s@#REDIS_PORT#@$REDIS_PORT@g" ntdeploy/celery.py.template
fi

: ${REDIS_DBNUM:=1}
if [ -n "$REDIS_DBNUM" ]; then
    sed -i "s@#REDIS_DBNUM#@$REDIS_DBNUM@g" ntdeploy/celery.py.template
fi

if [ -n "$REDIS_PASSWORD" ]; then
    sed -i "s|#REDIS_PASSWORD#|:$REDIS_PASSWORD@|g" ntdeploy/celery.py.template
else
    sed -i "s|#REDIS_PASSWORD#||g" ntdeploy/celery.py.template
fi


mv ntdeploy/settings.py.template ntdeploy/settings.py
mv ntdeploy/celery.py.template ntdeploy/celery.py

exec "$@"
