from django.urls import path
from rest_framework import routers
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('', include(router.urls), name='router'),
    # For user
    path('registerEndpoint/', views.RegisterAPI.as_view(), name='register_user'),
    path('loginEndpoint/', views.LoginAPI.as_view(), name='login_user'),
    
]