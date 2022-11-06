from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/receipts/', views.PostReceiptsAPIView.as_view(), name='create_receipts'),
    path('api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/', views.DefaultReceiptPaginationAPIListView.as_view(), name='list_paged_receipts'),
    path('api/receipts/<int:receipt_id>/', views.DetailReceiptsAPIView.as_view(), name='detail_receipts'),
    path('parse/', views.ParseReceiptsAPIView.as_view(), name='parse'),
] + static(settings.RECEIPT_IMAGES_URL, document_root=settings.RECEIPT_IMAGES_ROOT)
