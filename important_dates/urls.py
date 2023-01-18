from django.urls import path
from . import views

urlpatterns = [
    path('important_dates/', views.GetImportantDates.as_view(), name='get_important_dates'),
    path('important_dates/<int:item_id>/', views.GetImportantDates.as_view(), name='get_important_dates'),
    path('important_dates/add/', views.AddImportantDate.as_view(), name='add_important_date'),
    path('important_dates/delete/<int:important_date_id>/', views.DeleteImportantDate.as_view(),
         name='delete_important_date'),
]
