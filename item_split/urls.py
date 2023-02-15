from django.urls import path
from . import views

urlpatterns = [
    path('api/itemsplitAmount/', views.AddItemSplitAmountAPI.as_view(), name='add_item_split_amount'),
    path('api/itemsplitPercentage/', views.AddItemSplitAmountAPI.as_view(), name='add_item_split_percentage'),
    path('api/itemsplit/sharedUsers/item_id=<item_id>/', views.GetSharedUsersList.as_view(), name='get_user_list'),
    path('api/itemsplit/sharedAmount/item_id=<item_id>/', views.GetSharedAmount.as_view(), name='get_shared_amount'),
]
