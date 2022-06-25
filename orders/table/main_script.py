import logging
from logging.handlers import RotatingFileHandler
from os import getenv
from random import randint
from time import sleep
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
import psycopg2
from psycopg2 import Error
import requests


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s',
    handlers=[
        RotatingFileHandler(
            filename='main_script.log',
            maxBytes=50000000,
            backupCount=5),
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

SHEET_ID = '18t77XoaDLCmCUPfNm1TD3itBy1hFvcc0S3JG7wlJYvI'
CREDENTIALS = getenv('CREDENTIALS')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
QUOTES = 'http://www.cbr.ru/scripts/XML_daily.asp'


def get_credentials():
    """Получаем credentials из файла для service account."""
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS, scopes=SCOPES)
    return creds


def get_data():
    """Получаем данные из онлайн таблицы."""
    creds = get_credentials()
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='A:D',
            majorDimension="ROWS").execute()
        sheet = sheet['values']
        sheet.pop(0)
        return [row for row in sheet if row != []]
    except Exception as err:
        logger.exception(err)


def creating_table():
    """В заранее подготовленной базе данных создаю таблицу."""
    try:
        connection = psycopg2.connect(user=getenv('POSTGRES_USER'),
                                      password=getenv('POSTGRES_PASSWORD'),
                                      host=getenv('DB_HOST'),
                                      port=getenv('DB_PORT'),
                                      database=getenv('DB_NAME')
                                      )
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE TABLE_ORDERS
            (NUMBER INT,
            ORDER_NUM INT PRIMARY KEY,
            PRICE_USD INT,
            PRICE_RUB FLOAT4,
            DELIVERY TEXT);''')
        connection.commit()
    except (Exception, Error) as error:
        logger.exception("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()


def exchange_rate():
    """Получаю курс доллара с cbr.ru"""
    try:
        tree = ET.fromstring(requests.get(url=QUOTES).content)
        rate = tree.find('.*[@ID="R01235"]').find('Value').text.split(',')
        rate = float(".".join(rate))
    except HTTPError as err:
        logger.exception(err)
    return rate


def making_changes_to_the_database(add=None, delete=None):
    """Вношу изменения в БД."""
    try:
        connection = psycopg2.connect(user=getenv('POSTGRES_USER'),
                                      password=getenv('POSTGRES_PASSWORD'),
                                      host=getenv('DB_HOST'),
                                      port=getenv('DB_PORT'),
                                      database=getenv('DB_NAME')
                                      )
        cursor = connection.cursor()
        if delete:
            query = "DELETE FROM table_orders WHERE order_num = %s"
            for record in delete:
                cursor.execute(query, (record[1],))
        if add:
            rate = exchange_rate()
            query = '''INSERT INTO table_orders (number, order_num,
                price_usd, price_rub, delivery)
                VALUES (%s,%s,%s,%s,%s)'''
            for order in add:
                price_rub = f'{(int(order[2]) * rate):.2f}'
                order = (
                    order[0], order[1],
                    order[2], float(price_rub), order[3]
                )
                cursor.execute(query, order)
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()


def main():
    # creating_table()
    data = get_data()
    making_changes_to_the_database(add=data)
    print('Скрипт запущен')
    while True:
        sleep(randint(5, 20))
        new_data = get_data()
        if data != new_data:
            deleting = (d for d in data if d not in new_data)
            adding = (a for a in new_data if a not in data)
            making_changes_to_the_database(adding, deleting)
            print('В базу данных внесены изменения')
        data = new_data


if __name__ == '__main__':
    main()
