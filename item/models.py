import os
from django.db import models

from receipts.models import Receipts


class Item(models.Model):
    """
    An Item from a receipt that contains a name, it's price, tax, category and important dates
    """
    receipt_id = models.IntegerField()
    # category_id = models.ForeignKey(Categories, related_name='categories', on_delete=models.DO_NOTHING)
    # transaction = models.ForeignKey(Transactions, related_name='transactions', on_delete=models.CASCADE)
    tax = models.FloatField(blank=True, null=True)
    name = models.CharField(max_length=36)
    price = models.FloatField()
    important_dates = models.DateField(blank=True, null=True)