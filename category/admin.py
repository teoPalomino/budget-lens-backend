from django.contrib import admin
from .models import Category, SubCategory

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''To view Categories in Django admin page'''
    pass


@admin.register(SubCategory)
class CategoryAdmin(admin.ModelAdmin):
    '''To view SubCategories in Django admin page'''
    pass