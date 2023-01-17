from django.urls import path
from . import views

urlpatterns = [
    path('api/itemsplit/', views.AddItemSplitAPI.as_view(), name='add_item_split'),
]
