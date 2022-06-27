# Тестовое задание на позицию python разработчика в компанию Numbers
***
Проект получает данные из Google таблицы. Модифицирует их, хранит в БД и выводит на веб-страницу.
Отдельный скрипт отправляет оповещения в телеграм.
***
## Установка
***
Клонировать репозиторий.
```
git clone git@github.com:ruslan-kopylov/numbers_test.git
```

В папке ```/numbers_test/orders/``` создать файл .env.dev и добавить в него:
```
1. DB_ENGINE='django.db.backends.postgresql'
2. DB_NAME = 'postgres''
3. POSTGRES_USER = 'postgres'
4. POSTGRES_PASSWORD = 'postgres'
5. DB_HOST = 'db'
6. DB_PORT = '5432'
7. TELEGRAM_CHAT_ID = '<чат ID куда бот будет отправлять оповещения>'
8. TELEGRAM_TOKEN = '<токен от бота>'
```
В папке ```/orders/table/```  разместить файл "credentials.json" с данными от google api.

Запустить docker-compose:
```
docker-compose up -d
```
Для доступа к консоли ввести:
```
docker exec -it orders-web-1 /bin/bash
```
***
## Бесконечный скрипт.
Файл ```/orders/table/main_script.py``` можно запустить самостоятельно. Он будет отслеживать изменения в google таблице и вносить правки в базу данных.
***
## Телеграм бот:
Скрипт ```delivery_alert.py``` находится в корневой директори.
