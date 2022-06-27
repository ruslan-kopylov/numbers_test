import datetime as dt
import logging
from logging.handlers import RotatingFileHandler
import os
import time
from typing import List, Tuple

import psycopg2
from telegram import Bot, TelegramError


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s',
    handlers=[
        RotatingFileHandler(
            filename='deliveries_to_telegram.log',
            maxBytes=50000000,
            backupCount=5),
    ]
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
RETRY_TIME = 60 * 60 * 12


def send_message(bot: Bot, message: str) -> None:
    """Функция для отправки сообщения ботом."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except TelegramError:
        logger.exception('Cбой при отправке сообщения')


def dates_checker() -> Tuple[List[str], List[str]]:
    """Функция для проверки дат."""
    connection = psycopg2.connect(
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT'),
        database=os.environ.get('DB_NAME')
    )
    cursor = connection.cursor()
    query = 'SELECT * FROM table_orders'
    cursor.execute(query)
    alerts, today = [], []
    for row in cursor.fetchall():
        date = row[-1].split('.')
        date = dt.date(int(date[2]), int(date[1]), int(date[0]))
        if date == dt.date.today():
            today.append(row)
        if date < dt.date.today():
            alerts.append(row)
    return today, alerts


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            today, alerts = dates_checker()
            for order in today:
                message = f'Заказ номер {order[1]} поступит сегодня'
                send_message(bot, message)
                time.sleep(2)
            for order in alerts:
                message = (
                    f'Заказ номер {order[1]} '
                    f'должен был поступить {order[-1]}'
                )
                send_message(bot, message)
                time.sleep(2)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)


if __name__ == '__main__':
    main()
