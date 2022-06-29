# [Тестовое] задание на позицию python разработчика в компанию Numbers
***
Проект получает данные из [Google таблицы]. Добавляет к ним стоимость в рублях по курсу ЦБ, хранит в БД и выводит на веб-страницу.
Отдельный скрипт отправляет оповещения в телеграм.
***
## Установка
***
Клонировать репозиторий.
```
git clone git@github.com:ruslan-kopylov/numbers_test.git
```

В папке ```/numbers_test/``` создать файл .env.dev и добавить в него:
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
В папке ```/numbers_test/main_script/```  разместить файл "credentials.json" с данными от google api.

Запустить docker-compose из директории ```/numbers_test/``` - полученные данные будут доступны по адресу http://0.0.0.0:8000/:
```
sudo docker-compose up -d
```
***
## Бесконечный скрипт.
В отдельном контейнере запускается скрипт, который будет отслеживать изменения в google таблице и вносить правки в базу данных.
Код скрипта находится в ```numbers_test/main_scroipt/script.py```
***
## Телеграм бот:
Еще в одном контейнере запустится телеграм бот, который присылает сообщения о наступивших и прошедших датах поставки.
Код бота ```numbers_test/alert/alert.py```
Бот стартует через 10 секунд после запуска всех контейнеров.

[Google таблицы]:https://docs.google.com/spreadsheets/d/18t77XoaDLCmCUPfNm1TD3itBy1hFvcc0S3JG7wlJYvI/edit#gid=0

[Тестовое]:https://soldigital.notion.site/soldigital/developer-5b79683045a64129a2625a19bfb0c944
