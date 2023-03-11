from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.GetItemsAPI.as_view(), name='items'),  # Get items list and total cost
    path('items/add/', views.AddItemAPI.as_view(), name='add_item'),  # Add an item
    path('items/<int:item_id>/', views.ItemDetailAPIView.as_view(), name='item_details'),  # Observe details of an item
    path('items/delete/<int:item_id>/', views.DeleteItemAPI.as_view(), name='delete_item'),  # Delete an item
    path('items/pageNumber=<pageNumber>&pageSize=<pageSize>/', views.PaginateFilterItemsView.as_view(),
         name='list_paged_items'),
    path('items/category/costs/', views.GetCategoryCostsView.as_view(), name='get_category_costs'),
    path('items/<int:item_id>/date/days=<int:days>/', views.GetItemFrequencyByDateView.as_view(), name='get_item_frequency_date'),
    path('items/category/costs/date/days=<int:days>/', views.GetCategoryCostAndFrequencyByDateAndStarredCategoryView.as_view(), name='get_category_costs_frequency_date')
]
