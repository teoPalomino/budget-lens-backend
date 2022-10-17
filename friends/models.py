from django.db import models
from django.contrib.auth.models import User

class Friends(models.Model):
    """
    A friends profile
    """
    main_user = models.ForeignKey(User, related_name='main_user', on_delete=models.CASCADE)
    friend_user = models.ForeignKey(User, related_name='friend_user', on_delete=models.CASCADE, null=True)
    confirmed = models.BooleanField(default=False)
    temp_email = models.EmailField(max_length=254, null=True)