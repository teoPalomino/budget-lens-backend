from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.GetItemsAPI.as_view(), name='get_items'),  # Get items list
    path('items/add/', views.AddItemAPI.as_view(), name='create_item'),  # Add an item
    path('items/<int:item_id>/', views.ItemDetailAPIView.as_view(), name='item_details'),  # Observe details of an item
    path('items/delete/<int:item_id>/', views.DeleteItemAPI.as_view(), name='delete_item'),  # Delete an item
    path('items/totalPrice/', views.GetItemTotalCostView.as_view(), name='total_cost'),
]
