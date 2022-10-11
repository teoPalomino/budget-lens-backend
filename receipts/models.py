from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


def upload_to(filename):
    return 'receipt_images/{filename}'.format(filename=filename)


class Receipts(models.Model):
    """A Receipts model with a user model"""
    user = models.ForeignKey(User, related_name='receipts', on_delete=models.CASCADE)
    scan_date = models.DateTimeField(default=datetime.now)
    receipt_image_url = models.ImageField(upload_to=upload_to, blank=True, null=True)
