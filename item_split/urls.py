from django.urls import path
from . import views

urlpatterns = [
    path('api/itemsplit/', views.AddItemSplitAPI.as_view(), name='add_item_split'),
    path('api/itemsplit/sharedUsers/item_id=<item_id>/', views.GetSharedUsersList.as_view(), name='get_user_list'),
    path('api/itemsplit/sharedAmount/item_id=<item_id>/', views.GetSharedAmount.as_view(), name='get_shared_amount'),
]
