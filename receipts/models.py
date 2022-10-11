from datetime import datetime
from email.policy import default
from django.db import models
from django.contrib.auth.models import User


def upload_to(instance, filename):
    # user_token = User.objects.get(username=user).auth_token.key
    return 'receipt_images/{filename}'.format(filename=filename)


class Receipts(models.Model):
    """A Receipts model with a user model"""
    user = models.ForeignKey(User, related_name='receipts', on_delete=models.CASCADE)
    scan_date = models.DateField(default=datetime.now)
    receipt_image = models.ImageField(default=None, upload_to=upload_to)
