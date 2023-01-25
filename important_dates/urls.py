from django.urls import path
from . import views

urlpatterns = [
    path('important_dates/', views.RetrieveUpdateImportantDates.as_view(), name='important_dates'),
    path('important_dates/<int:item_id>/', views.RetrieveUpdateImportantDates.as_view(),
         name='get_important_dates'),
    path('important_dates/delete/<int:important_date_id>/', views.DeleteImportantDate.as_view(),
         name='delete_important_dates'),
]
