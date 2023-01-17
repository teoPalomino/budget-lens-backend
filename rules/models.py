from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

from category.models import Category


class Rule(models.Model):
    user = models.ForeignKey(User, related_name='rule_user', on_delete=models.CASCADE)
    regex = models.CharField(max_length=36)
    category = models.ForeignKey(Category, related_name='rule_category', null=True, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
