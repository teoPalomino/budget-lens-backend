from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(models.Model):
    """A User Profile with a phone number, a user model, and an email to forward receipts
    """
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    telephone_number = PhoneNumberField(null=False, blank=False, unique=True)
    one_time_code = models.PositiveBigIntegerField(default=0)
    forwardingEmail = models.EmailField(max_length=254, null=True)
