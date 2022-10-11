from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


def upload_to(filename, user):
    user_token = User.objects.get(username=user).auth_token.key
    return 'https://api.budgetlens.tech/receipts/{user_token}/{filename}'.format(user_token=user_token, filename=filename)


class Receipts(models.Model):
    """A Receipts model with a user model"""
    user = models.ForeignKey(User, related_name='receipts', on_delete=models.CASCADE)
    scan_date = models.DateField(default=datetime.now)
    receipt_image_url = models.TextField()
