import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from random import randint
from time import sleep
from typing import List, Dict, Union
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

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
BASE_DIR = Path(__file__).parent
SHEET_ID = '18t77XoaDLCmCUPfNm1TD3itBy1hFvcc0S3JG7wlJYvI'
CREDENTIALS = f'{BASE_DIR}/credentials.json'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
QUOTES = 'http://www.cbr.ru/scripts/XML_daily.asp'


def get_credentials() -> service_account.Credentials:
    """Получаем credentials из файла для service account."""
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS, scopes=SCOPES)
    return creds


def get_data() -> List[List[str]]:
    """Получаем данные из онлайн таблицы."""
    creds = get_credentials()
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='A:D',
            majorDimension="ROWS").execute()
        sheet = sheet['values']
        sheet.pop(0)
    except Exception as err:
        logger.exception(err)
    return [row for row in sheet if row != []]


def creating_table() -> None:
    """В заранее подготовленной базе данных создаю таблицу."""
    try:
        connection = psycopg2.connect(user=os.environ.get('POSTGRES_USER'),
                                      password=os.environ.get('POSTGRES_PASSWORD'),
                                      host=os.environ.get('DB_HOST'),
                                      port=os.environ.get('DB_PORT'),
                                      database=os.environ.get('DB_NAME')
                                      )
        cursor = connection.cursor()
        query = '''SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE'
            '''
        cursor.execute(query)
        if ('orders',) not in cursor.fetchall():
            cursor.execute('''CREATE TABLE ORDERS
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


def exchange_rate() -> float:
    """Получаю курс доллара с cbr.ru"""
    try:
        tree = ET.fromstring(requests.get(url=QUOTES).content)
        rate = tree.find('.*[@ID="R01235"]').find('Value').text.split(',')
        rate = float(".".join(rate))
    except HTTPError as err:
        logger.exception(err)
    return rate


def making_changes_to_the_database(
        add: List[List[str]] = None,
        delete: List[List[str]] = None,
        update: Dict[str, Dict[str, str]] = None,
        table_name: str = 'table_orders') -> None:
    """Вношу изменения в БД."""
    try:
        connection = psycopg2.connect(user=os.environ.get('POSTGRES_USER'),
                                      password=os.environ.get('POSTGRES_PASSWORD'),
                                      host=os.environ.get('DB_HOST'),
                                      port=os.environ.get('DB_PORT'),
                                      database=os.environ.get('DB_NAME')
                                      )
        cursor = connection.cursor()
        if update:
            for key, value in update.items():
                for param in value.keys():
                    query = """Update {} set {} = %s where
                        order_num = %s""".format(table_name, param)
                    cursor.execute(query, (value[param], key))
        if delete:
            query = "DELETE FROM {} WHERE order_num = %s".format(table_name)
            for record in delete:
                cursor.execute(query, (record[1],))
        if add:
            rate = exchange_rate()
            query = '''INSERT INTO {} (number, order_num, price_usd,
                price_rub, delivery)
                VALUES (%s,%s,%s,%s,%s)'''.format(table_name)
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


def find_updated_rows(
        data: List[List[str]],
        new_data: List[List[str]]
        ) -> Union[Dict[str, Dict[str, str]], dict]:
    updating: dict = {}
    columns = {
        0: 'number',
        1: 'order_num',
        2: 'price_usd',
        3: 'delivery'
    }
    old = [row for row in data if row not in new_data]
    new = [row for row in new_data if row not in data]
    for row in old:
        for new_row in new:
            if row[1] == new_row[1]:
                updating[row[1]] = {}
                for index, value in enumerate(row):
                    if value != new_row[index]:
                        updating[row[1]][columns[index]] = new_row[index]
                        if index == 2:
                            price_rub = f'''{(int(new_row[index]) *
                                 exchange_rate()):.2f}'''
                            updating[row[1]]['price_rub'] = price_rub
    return updating


def main():
    creating_table()
    data = get_data()
    making_changes_to_the_database(add=data, table_name='orders')
    print('Скрипт запущен')
    while True:
        sleep(randint(3, 5))
        new_data = get_data()
        if data != new_data:
            updating = find_updated_rows(data, new_data)
            keys = [k for k in updating.keys()]
            deleting = [d for d in data if (
                d[1] not in keys and d not in new_data)]
            adding = [a for a in new_data if (
                a[1] not in keys and a not in data)]
            making_changes_to_the_database(
                adding, deleting, updating, table_name='orders')
            print('В базу данных внесены изменения')
        data = new_data


if __name__ == '__main__':
    main()
