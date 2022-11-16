import os
from django.db import models

from receipts.models import Receipts


class Item(models.Model):
    """
    An Item from a receipt that contains a name, it's price, tax, category and important dates
    """
    receipt = models.ForeignKey(Receipts, related_name='receipts', on_delete=models.CASCADE)
    # category_id = models.ForeignKey(Categories, related_name='categories', on_delete=models.DO_NOTHING)
    tax = models.FloatField(blank=True, null=True)
    name = models.CharField(max_length=36)
    price = models.FloatField()
    important_dates = models.DateField(blank=True, null=True)