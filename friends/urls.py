from django.urls import path
from . import views

urlpatterns = [
    path('friend/', views.FriendsAPI.as_view(), name='get_friends'),
    path('friend/<int:user_id>', views.FriendsAPI.as_view(), name='get_friends'),
    path('friend/add', views.AddFriendsAPI.as_view(), name='add_friends'),
    path('friend/requestResponse/<int:friend_id>/<int:requestResponse>', views.FriendRequestResponseAPI.as_view(),
         name='friend_request_response'),
    path('friend/invite', views.InviteFriendsAPI.as_view(), name='invite_friends'),
    path('friend/remove/<int:friend_id>', views.RemoveFriendsAPI.as_view(), name='remove_friends'),
    path('friend/requests', views.FriendRequestsAPI.as_view(), name='friend_requests'),
]
