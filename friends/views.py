
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Friends
from .serializers import FriendSerializer
from users.serializers import UserSerializer
from django.contrib.auth.models import User
from utility.sendEmail import sendEmail


class AddFriendsAPI(generics.GenericAPIView):
    """
    API for adding a new friend
    Sends a friend request if the email is valid, and the user is not already a friend
    """
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def post(self, request, *args, **kwargs):

        friend_user = User.objects.filter(email=request.data.get('email')).values().first()

        if friend_user:
            response = self.validateFriendRequest(UserSerializer(request.user).data, friend_user)
            if response:
                return Response(response, status=HTTP_400_BAD_REQUEST)

            # Friend user email exists in database
            else:
                # Create entry in FRIENDS database for friend request
                serializer = self.get_serializer(data={
                    "friend_user": friend_user.get('id'),
                    "main_user": request.user.id,
                    "confirmed": False,
                    "temp_email": None
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({"response": "Friend request sent successfully"}, status=HTTP_200_OK)

        return Response({"response": "The user does not exist"}, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def validateFriendRequest(request_user, friend_user):
        """Validate that we can send a friend request to the user"""
        try:
            validate_email(friend_user.get('email'))
        except ValidationError:
            return {"response": "Invalid email address"}

        if request_user.get('id') == friend_user.get('id'):
            return {"response": "You cannot add yourself as a friend."}
        elif Friends.objects.filter(main_user=request_user.get('id'), friend_user=friend_user.get('id'),
                                    confirmed=True).exists():
            return {"response": "You are already friends with this user."}
        elif Friends.objects.filter(main_user=friend_user.get('id'), friend_user=request_user.get('id'),
                                    confirmed=True).exists():
            return {"response": "You are already friends with this user."}
        elif Friends.objects.filter(main_user=request_user.get('id'), friend_user=friend_user.get('id'),
                                    confirmed=False).exists():
            return {"response": "You have already sent a friend request to this user."}
        elif Friends.objects.filter(main_user=friend_user.get('id'), friend_user=request_user.get('id'),
                                    confirmed=False).exists():
            return {"response": "You have already have a pending friend request from this user."}
        else:
            return None


class FriendsAPI(generics.ListAPIView):
    """Returns a user's friend's User information if the user_id is specified, otherwise returns all friends"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def get(self, request, *args, **kwargs):
        # If the request specifies a user id, return that user
        if kwargs.get('user_id'):
            user = User.objects.filter(id=kwargs.get('user_id')).values().first()
            if user:
                return Response({"response": UserSerializer(user).data}, status=status.HTTP_200_OK)
            else:
                return Response({"response": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Return all user's friends
        else:
            query1 = Friends.objects.filter(main_user=self.request.user.id, confirmed=True)
            query2 = Friends.objects.filter(friend_user=self.request.user.id, confirmed=True)
            friends_list_users = []
            for friend in query1:
                friends_list_users.append(UserSerializer(User.objects.get(id=friend.friend_user.id)).data)
            for friend in query2:
                friends_list_users.append(UserSerializer(User.objects.get(id=friend.friend_user.id)).data)

            return Response({"response": friends_list_users}, status=status.HTTP_200_OK)


class RemoveFriendsAPI(generics.DestroyAPIView):
    """Removes a friend from the user's friend list"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def delete(self, request, *args, **kwargs):
        if kwargs.get('friend_id'):
            friend1 = Friends.objects.filter(main_user=request.user.id, friend_user=kwargs.get('friend_id'),
                                            confirmed=True)
            friend2 = Friends.objects.filter(friend_user=request.user.id, main_user=kwargs.get('friend_id'),
                                             confirmed=True)
            if friend1.exists():
                friend1.delete()
                return Response({"response": "Friend removed successfully"}, status=HTTP_200_OK)
            elif friend2.exists():
                friend2.delete()
                return Response({"response": "Friend removed successfully"}, status=HTTP_200_OK)
            else:
                return Response({"response": "Friend not found"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"response": "User ID not specified"}, status=HTTP_400_BAD_REQUEST)


class FriendRequestResponseAPI(generics.UpdateAPIView):
    """Accept or reject a friend request"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def put(self, request, *args, **kwargs):
        if kwargs.get('friend_id'):

            friend = Friends.objects.filter(friend_user=request.user.id, main_user=kwargs.get('friend_id'),
                                            confirmed=False)
            if friend.exists():
                # requestResponse of 0 = reject, 1 = accept
                if kwargs.get('requestResponse') == 1:
                    friend.update(confirmed=True)
                    return Response({"response": "Friend request accepted"}, status=HTTP_200_OK)
                elif kwargs.get('requestResponse') == 0:
                    friend.delete()
                    return Response({"response": "Friend request rejected"}, status=HTTP_200_OK)
                else:
                    return Response({"response": "Invalid response"}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({"response": "Friend request not found"}, status=HTTP_400_BAD_REQUEST)

        return Response({"response": "User ID or response not specified correctly"}, status=HTTP_400_BAD_REQUEST)


class InviteFriendsAPI(generics.GenericAPIView):
    """Sends an invite to join the app, and a pending friend request associated with the email invited"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def post(self, request, *args, **kwargs):

        try:
            validate_email(request.data.get('email'))
        except ValidationError:
            return Response({"response": "Invalid email address"}, status=HTTP_400_BAD_REQUEST)

        friend_user = User.objects.filter(email=request.data.get('email')).values().first()

        if friend_user:
            return Response('This email is already registered as a user', status=HTTP_400_BAD_REQUEST)

        friendInv = Friends.objects.filter(main_user=request.user.id, confirmed=False,
                                           temp_email=request.data.get('email'))

        if friendInv:
            return Response('U have already sent an invite to this email', status=HTTP_400_BAD_REQUEST)

        else:
            # Create entry in FRIENDS database for friend request using temp_email
            serializer = self.get_serializer(data={
                "main_user": request.user.id,
                "friend_user": None,
                "confirmed": False,
                "temp_email": request.data.get('email')
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            sendEmail(request.data.get('email'), 'BudgetLens Invitation',
                      request.user.first_name + ' ' + request.user.last_name + 'has invited you to download BudgetLens')

            return Response({"response": "An invitation has been sent to the following email"}, status=HTTP_200_OK)


class FriendRequestsSentAPI(generics.ListAPIView):
    """Returns a user's friend requests that he has sent"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def get(self, request, *args, **kwargs):
        friend_requests = Friends.objects.filter(main_user=request.user.id, confirmed=False, temp_email=None)
        friend_requests_list = []
        for friend_request in friend_requests:
            friend_requests_list.append(UserSerializer(User.objects.get(id=friend_request.friend_user.id)).data)

        return Response({"response": friend_requests_list}, status=HTTP_200_OK)


class FriendRequestsReceivedAPI(generics.ListAPIView):
    """Returns a user's friend requests that he has received"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def get(self, request, *args, **kwargs):
        friend_requests = Friends.objects.filter(friend_user=request.user.id, confirmed=False, temp_email=None)
        friend_requests_list = []
        for friend_request in friend_requests:
            friend_requests_list.append(UserSerializer(User.objects.get(id=friend_request.main_user.id)).data)

        return Response({"response": friend_requests_list}, status=HTTP_200_OK)
