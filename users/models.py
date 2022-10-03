from django.db import models
from django.contrib.auth.models import User


# class CustomUser(User):
#     User.first_name = models.CharField(max_length=150, blank=False)
#     User.last_name = models.CharField(max_length=150, blank=False)
#     User.email = models.EmailField(blank=False)
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['USERNAME']


class UserProfile(models.Model):
    """A User Profile with a phone number and a user model
    """
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    telephone_number = models.PositiveBigIntegerField()
