from django.shortcuts import render
import os

import psycopg2

from .models import Orders
from . import main_script




def index(request):
    check_table()
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
        updating = main_script.find_updated_rows(data, new_data)
        keys = [k for k in updating.keys()]
        deleting = [d for d in data if (
            d[1] not in keys and d not in new_data)]
        adding = [a for a in new_data if (
            a[1] not in keys and a not in data)]
        main_script.making_changes_to_the_database(adding, deleting, updating)
    orders = Orders.objects.all()
    return render(request, 'index.html', {'orders': orders})


def check_table() -> None:
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
