from django.shortcuts import render
from os import getenv

from dotenv import load_dotenv
from .models import Orders
from . import main_script
import psycopg2

load_dotenv()


def index(request):
    connection = psycopg2.connect(user=getenv('POSTGRES_USER'),
                                  password=getenv('POSTGRES_PASSWORD'),
                                  host=getenv('DB_HOST'),
                                  port=getenv('DB_PORT'),
                                  database=getenv('DB_NAME')
                                  )
    cursor = connection.cursor()
    query = '''SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public' AND table_type='BASE TABLE'
        '''
    cursor.execute(query)
    if ('table_orders',) not in cursor.fetchall():
        cursor.execute('''CREATE TABLE TABLE_ORDERS
            (NUMBER INT,
            ORDER_NUM INT PRIMARY KEY,
            PRICE_USD INT,
            PRICE_RUB FLOAT4,
            DELIVERY TEXT);''')
        connection.commit()
    cursor.close()
    connection.close()
    new_data = main_script.get_data()
    data = []
    qset = Orders.objects.all()
    for q in qset:
        data.append([
            str(q.number), str(q.order_num),
            str(q.price_usd),
            q.delivery
        ])
    if data != new_data:
        deleting = (d for d in data if d not in new_data)
        adding = (a for a in new_data if a not in data)
        main_script.making_changes_to_the_database(adding, deleting)
    orders = Orders.objects.all()
    return render(request, 'index.html', {'orders': orders})
