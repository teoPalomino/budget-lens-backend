from django.urls import path
from . import views

urlpatterns = [
    path('api/merchant/', views.AddAndListMerchantView.as_view(), name='add_and_list_merchant'),
]
