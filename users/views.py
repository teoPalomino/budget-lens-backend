from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import password_validators_help_texts

from .models import UserProfile
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterAPI(generics.GenericAPIView):
    """API for registering a new user"""
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_profile = serializer.save()

        token = Token.objects.create(user=user_profile.user)

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

        token = Token.objects.create(user=user)
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
        request.user.auth_token.delete()
        return Response({
            "data": "Succesfully deleted"
        })
