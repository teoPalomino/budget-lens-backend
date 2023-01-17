from django.db import models
from item.models import Item


class ItemSplit(models.Model):
    """
    Model for Splitting a single item accross many users.
    """

    item = models.ForeignKey(Item, related_name='item_user', on_delete=models.DO_NOTHING)
    shared_user_ids = models.CharField(max_length=100)
