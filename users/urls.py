from django.urls import path
from . import views

urlpatterns = [
    path('registerEndpoint/', views.RegisterAPI.as_view(), name='register_user'),
    path('loginEndpoint/', views.LoginAPI.as_view(), name='login_user'),
    path('userEndpoint/', views.UserAPI.as_view(), name='user_data'),
    path('userprofile/', views.UserProfileAPI.as_view(), name='user_profile'),
    path('logoutEndpoint/', views.LogoutAPI.as_view(), name='logout_user'),
    path('friend/', views.GetFriendsAPI.as_view(), name='get_friends'),
    path('friend/<int:user_id>', views.GetFriendsAPI.as_view(), name='get_friends'),
    path('friend/add', views.AddFriendsAPI.as_view(), name='add_friends'),
    path('friend/requestResponse/<int:friend_id>/<int:requestResponse>', views.FriendRequestResponseAPI.as_view(), name='friend_request_response'),
    path('friend/invite', views.InviteFriendsAPI.as_view(), name='invite_friends'),
    path('friend/remove/<int:friend_id>', views.RemoveFriendsAPI.as_view(), name='remove_friends')
]
