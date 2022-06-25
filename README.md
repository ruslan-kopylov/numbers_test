# Тестовое задание на позицию python разработчика в компанию Numbers
***
Проект получает данные из Google таблицы. Модифицирует их, хранит в БД и выводит на веб-страницу.
Отдельный скрипт отправляет оповещения в телеграм.
***
## Установка.
***
Клонировать репозиторий и перейтив него в командной строке.
```
git clone git@github.com:ruslan-kopylov/numbers_test.git

cd numbers_test
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv

source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```
В основной папке проекта (где settings.py) создать файл .env и добавить в него:
```
1. DB_ENGINE='django.db.backends.postgresql'
2. DB_NAME = '<название БД>'
3. POSTGRES_USER = '<логин от БД>'
4. POSTGRES_PASSWORD = '<пароль от БД>'
5. DB_HOST = '127.0.0.1'
6. DB_PORT = '5432'
6. TELEGRAM_CHAT_ID = '<ID чата, куда боту отправлять сообщения>'
7. TELEGRAM_TOKEN = '<Токен от телеграм бота>'
8. CREDENTIALS = '<абсолютный путь>' - путь к файлу с credentials для доступа к google api.
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
***
## Бесконечный скрипт.
Файл ```/orders/table/main_script.py``` можно запустить самостоятельно. Он будет отслеживать изменения в google таблице и вносить правки в базу данных.
***
## Телеграм бот:
Скрипт ```delivery_alert.py``` находится в корневой директори.
