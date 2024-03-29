from django.db import models
from receipts.models import Receipts


class ReceiptSplit(models.Model):
    """
    Model for splitting a single receipt across many users.
    """

    receipt = models.ForeignKey(Receipts, related_name='receipt_user', on_delete=models.DO_NOTHING)
    shared_user_ids = models.CharField(max_length=100)
    is_shared_with_receipt_owner = models.BooleanField(default=False)
    shared_amount = models.CharField(max_length=100)
