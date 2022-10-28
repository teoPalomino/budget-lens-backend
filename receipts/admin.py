from django.contrib import admin
from .models import Receipts


@admin.register(Receipts)
class ReceiptsAdmin(admin.ModelAdmin):
    '''To view receipts in django admin page'''
    pass
