from django.contrib import admin
from .models import Receipts


@admin.register(Receipts)
class ReceiptsAdmin(admin.ModelAdmin):
    pass
