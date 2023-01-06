from django.urls import path
from . import views

urlpatterns = [
    # Use the DELETE method for deleting a sub category, Use the PUT method for toggling the star of any category
    path('api/category/categoryName=<categoryName>', views.DeleteAndToggleStarCategoryView.as_view(), name='delete_and_toggle_category'),

    # Use the POST method to add a new category. Use the GET method to return the list of all categoryies with each category having there child categories
    path('api/category/', views.AddAndListCategoryView.as_view(), name='add_and_list_category'),

# Use the PUT method to edit category name
    path('api/category/<str:categoryName>/', views.EditCategoryAPIView.as_view(), name='edit_category'),

    path('api/category/costs/', views.GetCategoryCostsView.as_view(), name='get_category_costs'),
]
