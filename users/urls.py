from django.urls import path
from rest_framework import routers
from . import views

urlpatterns = [
    path('registerEndpoint/', views.RegisterAPI.as_view(), name='register_user'),
    path('loginEndpoint/', views.LoginAPI.as_view(), name='login_user'),

]
