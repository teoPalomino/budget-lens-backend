from django.db import models

#from receipts.models import Receipts
import receipts.models
from category.models import Category
from django.contrib.auth.models import User


class Item(models.Model):
    """
    An Item from a receipt that contains a name, it's price, category and important dates
    """
    user = models.ForeignKey(User, related_name='item_user', on_delete=models.CASCADE)
    receipt = models.ForeignKey(receipts.models.Receipts, related_name='receipts', on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, related_name='category', null=True, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=36)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    important_dates = models.DateField(blank=True, null=True)
