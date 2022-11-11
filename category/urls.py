from django.urls import path
from . import views

urlpatterns = [
    path('api/category/', views.CategoryView.as_view(), name='category'),
    path('api/subcategory/', views.SubCategoryView.as_view(), name='subcategory'),
]
