from django.urls import path
from . import views

urlpatterns = [
    path('api/item/', views.ItemView.as_view(), name='item'),
]
