from django.urls import path
from . import views

urlpatterns = [
    path('friend/', views.FriendsAPI.as_view(), name='friends'),
    path('friend/<int:friend_id>/', views.FriendsAPI.as_view(), name='friends'),
    path('friend/request/', views.FriendRequestAPI.as_view(), name='friend_requests'),
    path('friend/request/<int:friend_id>/<int:answer>/', views.FriendRequestAPI.as_view(),
         name='friend_requests'),
    path('friend/invite/', views.InviteFriendsAPI.as_view(), name='invite_friends'),
]
