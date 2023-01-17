from django.contrib import admin
from .models import ItemSplit


@admin.register(ItemSplit)
class ItemAdmin(admin.ModelAdmin):
    '''To view ItemSplit models in django admin page'''
    pass
