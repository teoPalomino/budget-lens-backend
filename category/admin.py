from django.contrib import admin
from .models import Category

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''To view Categories in Django admin page'''
    pass


# @admin.register(SubCategory)
# class SubCategoryAdmin(admin.ModelAdmin):
#     '''To view SubCategories in Django admin page'''
#     pass
