from django.urls import path
from . import views

urlpatterns = [
    path('api/category/', views.AddCategoryView.as_view(), name='add_category'),
    path('api/subcategory/', views.AddSubCategoryView.as_view(), name='add_subcategory'),
    path('api/subcategory/subCategoryName=<subCategoryName>', views.DeleteSubCategoryView.as_view(), name='delete_subcategory'),
    path('api/subcategory/', views.DeleteSubCategoryView.as_view(), name='toggle_star_subcategory'),
    path('api/allcategories/', views.ListCategoriesAndSubCategoriesView.as_view(), name='list_all_categories'),

]
