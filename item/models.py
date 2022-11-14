from django.db import models
from receipts.models import Receipts
from category.models import Category, SubCategory

# Create your models here.


class Item(models.Model):
    """
    The parent category models
    """
    name = models.CharField(max_length=30)
    price = models.FloatField(default=0.0)
    receipt_id = models.ForeignKey(Receipts, on_delete=models.DO_NOTHING)
    category_id = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    sub_category_id = models.ForeignKey(SubCategory, on_delete=models.DO_NOTHING)
