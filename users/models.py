from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """A User Profile with a phone number and a user model
    """
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    telephone_number = models.PositiveBigIntegerField()
    one_time_code = models.PositiveBigIntegerField()
