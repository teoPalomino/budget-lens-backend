from django.urls import path
from . import views

urlpatterns = [
    # GET: load friend page
    path('friend/', views.FriendsAPI.as_view(), name='friends'),
    # GET: load individiual friend page, DELETE: remove friend
    path('friend/<int:friend_id>/', views.FriendsAPI.as_view(), name='friends'),
    # GET: load friend page with requests filter on, POST: Add friend
    path('friend/request/', views.FriendRequestAPI.as_view(), name='friend_requests'),
    # PUT: accept/reject friend request
    path('friend/request/<int:friend_id>/', views.FriendRequestAPI.as_view(),
         name='friend_requests'),
    # POST: send an email invite when user tries to add an email not corresponding to an existing user
    path('friend/invite/', views.InviteFriendsAPI.as_view(), name='invite_friends'),
]
