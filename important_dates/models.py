from django.db import models

from django.contrib.auth.models import User
from item.models import Item


class ImportantDates(models.Model):
    """
    An Important Date for an item
    """
    user = models.ForeignKey(User, related_name='important_date_user', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='important_date_item', on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=36, blank=True, null=True)
