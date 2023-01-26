from django.contrib import admin
from .models import ReceiptSplit


@admin.register(ReceiptSplit)
class ReceiptAdmin(admin.ModelAdmin):
    """To view ReceiptSplit models in django admin page"""
    pass
