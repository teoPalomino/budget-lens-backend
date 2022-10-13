from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(models.Model):
    """A User Profile with a phone number and a user model
    """
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    telephone_number = PhoneNumberField(null=False, blank=False, unique=True)


class Friends(models.Model):
    """
    A friends profile
    """
    main_user = models.ForeignKey(User, related_name='main_user', on_delete=models.CASCADE)
    friend_user = models.ForeignKey(User, related_name='friend_user', on_delete=models.CASCADE, null=True)
    confirmed = models.BooleanField(default=False)
    temp_email = models.EmailField(max_length=254, null=True)
