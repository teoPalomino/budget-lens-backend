from django.db import models

# Create your models here.
class Category(models.Model):
    """
    The parent category models
    """
    category_name = models.CharField(max_length=30, blank=True, default='')
    category_toggle_star = models.BooleanField(default=False)


class SubCategory(models.Model):
    """
    The child category models (subcategories of parent).
    TODO: Make sure this structure provides a Many to one relationship
    """
    
    parent_category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    sub_category_name = models.CharField(max_length=30, blank=True, default='')
    sub_category_toggle_star = models.BooleanField(default=False)
