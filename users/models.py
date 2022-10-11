from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """A User Profile with a phone number and a user model
    """
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    telephone_number = models.PositiveBigIntegerField()


class Friends(models.Model):
    """
    A friends profile
    """
    main_user = models.ForeignKey(User, related_name='main_user', on_delete=models.CASCADE)
    friend_user = models.ForeignKey(User, related_name='friend_user', on_delete=models.CASCADE, null=True)
    confirmed = models.BooleanField(default=False)
    temp_email = models.EmailField(max_length=254, null=True)
