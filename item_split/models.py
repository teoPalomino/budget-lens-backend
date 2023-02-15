from django.db import models
from item.models import Item


class ItemSplit(models.Model):
    """
    Model for Splitting a single item across many users.
    """

    item = models.OneToOneField(Item, related_name='item_id', on_delete=models.CASCADE)
    shared_user_ids = models.CharField(max_length=100)
    is_shared_with_item_user = models.BooleanField(default=False)
    shared_amount = models.CharField(max_length=100)
