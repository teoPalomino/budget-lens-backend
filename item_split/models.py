from django.db import models
from item.models import Item


class ItemSplit(models.Model):
    """
    Model for Splitting a single item accross many users.
    """

    item = models.OneToOneField(Item, related_name='item_user', on_delete=models.DO_NOTHING)
    shared_user_ids = models.CharField(max_length=100)
    is_shared_with_item_user = models.BooleanField(default=False)
    shared_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
