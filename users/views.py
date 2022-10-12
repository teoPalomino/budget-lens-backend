from django.core.validators import validate_email
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import password_validators_help_texts
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from .models import UserProfile, Friends
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, FriendSerializer
from .authentication import BearerToken
from django.contrib.auth.models import User
from utility.sendEmail import sendEmail


class RegisterAPI(generics.GenericAPIView):
    """API for registering a new user"""
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_profile = serializer.save()

        token = BearerToken.objects.create(user=user_profile.user)
        user = UserSerializer(user_profile.user, context=self.get_serializer_context())

        # TODO: a proper registration email need to be developed, right now, the function is proven to work

        # To use sendEmail function, you have to import it from the utility folder, for refrence, look at the imports at the top
        sendEmail(user.data['email'], 'User Successfully registered', 'User Successfully registered')
        # converting all email invites to friend requests upon registration
        friends = Friends.objects.get(temp_email=user.data['email'])
        for friend in friends:
            friend.friend_user = user.data['id']
            friend.temp_email = None
            friend.save()
        return Response({
            # saves user and its data
            "user": user.data,
            "telephone number": user_profile.telephone_number,
            # creates token for that particular user
            # "token": AuthToken.objects.create(user_profile.user)[1],
            "token": token.key,
            "passwordValidators": password_validators_help_texts(password_validators=None)
        })


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        try:
            token = BearerToken.objects.create(user=user)
        except Exception:
            return Response({
                "details": "Token already exists (User is already logged in)",
                "token": BearerToken.objects.get(user=user).key
            })

        return Response({
            # saves user and its data
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            # creates token for that particular user
            "token": token.key
        })


class UserAPI(generics.RetrieveAPIView):
    """User API use for returning user data from a Bearer Authentication"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def delete(self, request, *args, **kwargs):
        request.user.auth_bearertoken.delete()
        return Response({
            "data": "Succesfully deleted"
        }, status=HTTP_200_OK)


class AddFriendsAPI(generics.GenericAPIView):
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
                    "confirmed": False
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({"response": "Friend request sent successfully"}, status=HTTP_200_OK)

    @staticmethod
    def validateFriendRequest(request_user, friend_user):
        """Validate that we can send a friend request to the user"""
        try:
            validate_email(friend_user.get('email'))
        except ValidationError:
            return {"response": "Invalid email address"}

        if request_user.get('id') == friend_user.get('id'):
            return {"response": "You can't add yourself as a friend."}
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


class GetFriendsAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        # If the request specifies a user id, return that user
        if request.data.get('user_id'):
            user = UserSerializer(User.objects.get(id=request.data.get('user_id'))).data

            if user:
                return Response({"response": user}, status=HTTP_200_OK)
            else:
                return Response({"response": "User not found"}, status=HTTP_400_BAD_REQUEST)

        # Return all user's friends
        else:
            friends = Friends.objects.filter(main_user=self.request.user.id, confirmed=True)
            friends_list_users = []
            for friend in friends:
                friends_list_users.append(UserSerializer(User.objects.get(id=friend.friend_user.id)).data)

            return Response({"response": friends_list_users}, status=HTTP_200_OK)


class RemoveFriendsAPI(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, ]

    def delete(self, request, *args, **kwargs):
        try:
            # Delete entry in FRIENDS database for friend request
            Friends.objects.filter(main_user=request.user.id, friend_user=request.data.get('user_id'),
                                   confirmed=True).delete()
            return Response({"response": "Friend removed successfully"}, status=HTTP_200_OK)
        except Exception:
            return Response({"response": "Friend not found"}, status=HTTP_400_BAD_REQUEST)


class InviteFriendsAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendSerializer

    def post(self, request, *args, **kwargs):
        try:
            validate_email(request.data.get('email'))
        except ValidationError:
            return Response({"response": "Invalid email address"})

        # Create entry in FRIENDS database for friend request using temp_email
        serializer = self.get_serializer(data={
            "main_user": request.user.id,
            "confirmed": False,
            "temp_email": request.data.get('email')
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sendEmail(request.data.get('email'), 'BudgetLens Invitation',
                  request.user.first_name + ' ' + request.user.last_name + 'has invited you to download BudgetLens')

        return Response({"response": "An invitation has been sent to the following email"})
