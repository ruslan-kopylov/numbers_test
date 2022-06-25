# numbers_test
Тестовое задание на позицию python разработчика в компанию Numbers

В файле orders/table/main_script.py:
Строка 33 - добавить абсолютный путь до файла с credentials для доступа к google api

В папке главной папке проекта (где файл settings.py) создать файл .env и добавить в него:
DB_ENGINE='django.db.backends.postgresql'
DB_NAME = '<название БД>'
POSTGRES_USER = '<логин от БД>'
POSTGRES_PASSWORD = '<пароль от БД>'
DB_HOST = '127.0.0.1'
DB_PORT = '5432'
