from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """
    The parent category models
    """
    category_name = models.CharField(max_length=30, blank=True, default='')
    category_toggle_star = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_category_id = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "category_name")

    def get_category_name(self):
        return self.category_name
