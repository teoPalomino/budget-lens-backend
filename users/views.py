from django.core.validators import validate_email
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import password_validators_help_texts

from .models import UserProfile, Friends
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, AddFriendsSerializer
from .authentication import BearerToken
from django.contrib.auth.models import User
from utility.sendEmail import SendEmail


class RegisterAPI(generics.GenericAPIView):
    """API for registering a new user"""
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_profile = serializer.save()

        token = BearerToken.objects.create(user=user_profile.user)

        return Response({
            # saves user and its data
            "user": UserSerializer(user_profile.user, context=self.get_serializer_context()).data,
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
        })


class AddFriendsAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = AddFriendsSerializer

    def post(self, request, *args, **kwargs):
        friend_user = User.objects.filter(email=request.data.get('email')).values().first()

        if friend_user:
            response = self.validateFriendRequest(UserSerializer(request.user).data, friend_user)

            if response:
                return Response(response)

            # Friend user email exists in database
            else:
                # TODO: Send friend request email (what will be in the email ?)

                # Create entry in FRIENDS database for friend request
                serializer = self.get_serializer(data={
                    "friend_user": friend_user.get('id'),
                    "main_user": request.user.id,
                    "confirmed": False
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({"response": "Friend request sent successfully"})

        # Email does not exist in database
        else:
            response = self.validateFriendInvite(UserSerializer(request.user).data, friend_user)

            if response:
                return Response(response)
            # Email is a valid email
            else:
                # Create entry in FRIENDS database for friend request using temp_email
                serializer = self.get_serializer(data={
                    "main_user": request.user.id,
                    "confirmed": False,
                    "temp_email": request.data.get('email')
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()
                # sendEmail(request.data.get('email'), request.user.first_name + ' ' + request.user.last_name + 'has invited you to download BudgetLens')

            return Response({"response": "An invitation has been sent to the following email"})

    @staticmethod
    def validateFriendRequest(request_user, friend_user):
        """Validate that we can send a friend request to the user"""
        try:
            validate_email(friend_user.get('email'))
        except ValidationError:
            return {"response": "Invalid email address"}

        if request_user.get('id') == friend_user.get('id'):
            return {"response": "You can't add yourself as a friend."}
        elif Friends.objects.filter(main_user=request_user.get('id'), friend_user=friend_user.get('id'), confirmed=True).exists():
            return {"response": "You are already friends with this user."}
        elif Friends.objects.filter(main_user=friend_user.get('id'), friend_user=request_user.get('id'), confirmed=True).exists():
            return {"response": "You are already friends with this user."}
        elif Friends.objects.filter(main_user=request_user.get('id'), friend_user=friend_user.get('id'), confirmed=False).exists():
            return {"response": "You have already sent a friend request to this user."}
        elif Friends.objects.filter(main_user=friend_user.get('id'), friend_user=request_user.get('id'), confirmed=False).exists():
            return {"response": "You have already have a pending friend request from this user."}
        else:
            return None

    @staticmethod
    def validateFriendInvite(request_user, friend_user):
        """Validate the email to send link to download the app"""
        try:
            validate_email(friend_user.get('email'))
        except ValidationError:
            return {"response": "Invalid email address"}

        return None
