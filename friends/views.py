from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Friends
from .serializers import FriendSerializer
from users.serializers import UserSerializer
from django.contrib.auth.models import User
from utility.sendEmail import sendEmail


class FriendsAPI(generics.GenericAPIView):
    """Returns a user's friend's User information if the friend_id is specified, otherwise returns all friends"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def get(self, request, *args, **kwargs):
        # If the request specifies a user id, return that user
        if kwargs.get('friend_id'):
            user = User.objects.filter(id=kwargs.get('friend_id')).values().first()
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
                friends_list_users.append(UserSerializer(User.objects.get(id=friend.main_user.id)).data)

            return Response({"response": friends_list_users}, status=status.HTTP_200_OK)

    # used to remove/delete a friend, friend_id needs to be specified in the url
    def delete(self, request, *args, **kwargs):
        if kwargs.get('friend_id'):
            friend1 = Friends.objects.filter(main_user=request.user.id, friend_user=kwargs.get('friend_id'),
                                             confirmed=True)
            friend2 = Friends.objects.filter(friend_user=request.user.id, main_user=kwargs.get('friend_id'),
                                             confirmed=True)
            if friend1.exists():
                friend1.delete()
                return Response({"response": "Friend removed successfully"}, status=status.HTTP_200_OK)
            elif friend2.exists():
                friend2.delete()
                return Response({"response": "Friend removed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"response": "Friend not found"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"response": "User ID not specified"}, status=status.HTTP_400_BAD_REQUEST)


class InviteFriendsAPI(generics.GenericAPIView):
    """Sends an invite to join the app, and a pending friend request associated with the email invited"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    # send an email invitation to non existing user with email passed as data
    def post(self, request, *args, **kwargs):

        try:
            validate_email(request.data.get('email'))
        except ValidationError:
            return Response({"response": "Invalid email address"}, status=status.HTTP_400_BAD_REQUEST)

        friend_user = User.objects.filter(email=request.data.get('email')).values().first()

        if friend_user:
            return Response('This email is already registered as a user', status=status.HTTP_400_BAD_REQUEST)

        friendInv = Friends.objects.filter(main_user=request.user.id, confirmed=False,
                                           temp_email=request.data.get('email'))

        if friendInv:
            return Response('U have already sent an invite to this email', status=status.HTTP_400_BAD_REQUEST)

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

            return Response({"response": "An invitation has been sent to the following email"}, status=status.HTTP_200_OK)


class FriendRequestAPI(generics.GenericAPIView):
    """Accept or reject a friend request"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    # sends a friend request to user with email sent as data
    def post(self, request, *args, **kwargs):

        friend_user = User.objects.filter(email=request.data.get('email')).values().first()

        if friend_user:
            response = self.validateFriendRequest(UserSerializer(request.user).data, friend_user)
            if response:
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

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

                return Response({"response": "Friend request sent successfully"}, status=status.HTTP_200_OK)

        return Response({"response": "The user does not exist"}, status=status.HTTP_400_BAD_REQUEST)

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

    # friend request response, depending on answer = 0(reject) or 1(accept) sent as data
    def put(self, request, *args, **kwargs):
        if kwargs.get('friend_id'):

            friend = Friends.objects.filter(friend_user=request.user.id, main_user=kwargs.get('friend_id'),
                                            confirmed=False)
            if friend.exists():
                # answer of 0 = reject, 1 = accept
                if request.data.get('answer') == 1:
                    friend.update(confirmed=True)
                    return Response({"response": "Friend request accepted"}, status=status.HTTP_200_OK)
                elif request.data.get('answer') == 0:
                    friend.delete()
                    return Response({"response": "Friend request rejected"}, status=status.HTTP_200_OK)
                else:
                    return Response({"response": "Invalid answer"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"response": "Friend request not found"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"response": "User ID or answer not specified correctly"}, status=status.HTTP_400_BAD_REQUEST)

    # friends page with requests sent and received
    def get(self, request, *args, **kwargs):

        friend_requests_sent = Friends.objects.filter(main_user=request.user.id, confirmed=False, temp_email=None)
        friend_requests_received = Friends.objects.filter(friend_user=request.user.id, confirmed=False, temp_email=None)
        friends1 = Friends.objects.filter(main_user=request.user.id, confirmed=True, temp_email=None)
        friends2 = Friends.objects.filter(friend_user=request.user.id, confirmed=True, temp_email=None)

        friend_requests_sent_list = []
        friend_requests_received_list = []
        friend_list = []

        for friend_request in friend_requests_sent:
            friend_requests_sent_list.append(UserSerializer(User.objects.get(id=friend_request.friend_user.id)).data)

        for friend_request in friend_requests_received:
            friend_requests_received_list.append(UserSerializer(User.objects.get(id=friend_request.main_user.id)).data)

        for friend in friends1:
            friend_list.append(UserSerializer(User.objects.get(id=friend.friend_user.id)).data)

        for friend in friends2:
            friend_list.append(UserSerializer(User.objects.get(id=friend.main_user.id)).data)

        return Response({"requests_sent": friend_requests_sent_list,
                         "requests_received": friend_requests_received_list,
                         "friends": friend_list}, status=status.HTTP_200_OK)
