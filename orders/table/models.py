from django.db import models


class Orders(models.Model):
    number = models.IntegerField()
    order_num = models.IntegerField(primary_key=True)
    price_usd = models.IntegerField()
    price_rub = models.FloatField()
    delivery = models.CharField(max_length=200)
