from django.urls import path
from . import views

urlpatterns = [
    path('api/itemsplit/', views.AddItemSplitAPI.as_view(), name='item_split'),
]
