from django.urls import path
from . import views

urlpatterns = [
    path('api/itemsplit/', views.AddItemSplitAPI.as_view(), name='add_item_split'),
    path('api/itemsplit/sharedUsers/itemsplit_id=<itemsplit_id>/', views.GetSharedUsersList.as_view(), name='get_user_list'),
    path('api/itemsplit/sharedAmount/itemsplit_id=<itemsplit_id>/', views.GetSharedAmount.as_view(), name='get_shared_amount'),
]
