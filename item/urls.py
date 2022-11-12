from django.urls import path
from . import views

urlpatterns = [
    path('item/', views.AddItemAPI.as_view(), name='item'),
]
