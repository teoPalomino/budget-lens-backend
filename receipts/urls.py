from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('addReceiptsEndpoint/', views.AddReceiptsAPI.as_view(), name='add_receipts')
] + static(settings.RECEIPT_IMAGES_URL, document_root=settings.RECEIPT_IMAGES_ROOT)