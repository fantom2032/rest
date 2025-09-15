#!/bin/bash

echo "Применяем миграции..."
python manage.py migrate

echo "Собираем статику"
# python manage.py collectstatic

# Не выполнять! это нужно запускать в двух разных терминалах

# # Команда для запуска celery beat
# celery -A settings.celery_app beat --loglevel=INFO

# # Команда для запуска celery worker
# celery -A settings.celery_app worker --loglevel=INFO
exec daphne settings.asgi:application -b 0.0.0.0 -p 8000