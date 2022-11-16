from django.urls import path
from . import views

urlpatterns = [
    # For Category class
    # path('api/category/', views.AddCategoryView.as_view(), name='add_category'),
    path('api/category/categoryName=<categoryName>', views.DeleteAndToggleStarCategoryView.as_view(), name='delete_and_toggle_category'),
    path('api/category/', views.AddAndListCategoryView.as_view(), name='add_and_list_category'),

    # path('api/category/categoryName=<categoryName>', views.ToggleStarCategoryView.as_view(), name='toggle_category'),
    # path('api/category/costs/', views.GetCategoryCostsView.as_view(), name='get_category_costs'),

    # For SubCategory class
    # path('api/subcategory/', views.AddSubCategoryView.as_view(), name='add_subcategory'),
    # path('api/subcategory/subCategoryName=<subCategoryName>', views.DeleteAndToggleStarSubCategoryView.as_view(), name='delete_and_toggle_subcategory'),

    # For both classes
    # path('api/allcategories/', views.ListCategoriesAndSubCategoriesView.as_view(), name='list_all_categories'),

]
