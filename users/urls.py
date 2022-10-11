from django.urls import path
from . import views

urlpatterns = [
    path('registerEndpoint/', views.RegisterAPI.as_view(), name='register_user'),
    path('loginEndpoint/', views.LoginAPI.as_view(), name='login_user'),
    path('userEndpoint/', views.UserAPI.as_view(), name='user_data'),
    path('logoutEndpoint/', views.LogoutAPI.as_view(), name='logout_user'),
    path('friend/add', views.AddFriendsAPI.as_view(), name='add_friends'),
    path('friend/invite', views.InviteFriendsAPI.as_view(), name='invite_friends')

]
