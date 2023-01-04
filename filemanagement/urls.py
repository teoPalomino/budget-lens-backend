from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'file'

router = DefaultRouter()
router.register(r'upload', FilesViewset, basename='upload')

urlpatterns = [

] + router.urls
