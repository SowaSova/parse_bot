#!/bin/sh

# # echo "Установка зависимостей..."
# # poetry run playwright install chromium --with-deps

# echo "Применение миграций..."
# # python manage.py makemigrations
# python manage.py migrate

# echo "Сбор статических файлов..."
# python manage.py collectstatic --noinput

# echo "Загрузка начальных данных..."
# python manage.py loaddata fixtures/db.json


exec "$@"
