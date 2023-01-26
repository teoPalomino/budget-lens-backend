from django.urls import path
from . import views

urlpatterns = [
    path('api/receiptsplit/', views.AddReceiptSplitAPI.as_view(), name='add_receipt_split'),
    path('api/receiptsplit/sharedUsers/receipt_id=<receipt_id>/', views.GetSharedUsersList.as_view(), name='get_user_list'),
    path('api/receiptsplit/sharedAmount/receipt_id=<receipt_id>/', views.GetSharedAmount.as_view(), name='get_shared_amount'),
]
