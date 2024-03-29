import random
import secrets
from django.core.validators import validate_email
from django.db import IntegrityError
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import password_validators_help_texts
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from friends.models import Friends
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, EmailSerializer, \
    ValidateDigitSerializer, ChangePasswordSerializer
from .models import UserProfile
from django.contrib.auth.models import User
from .authentication import BearerToken
from utility.sendEmail import sendEmail


class RegisterAPI(generics.GenericAPIView):
    """API for registering a new user"""
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user_profile = serializer.save()
        token = BearerToken.objects.create(user=user_profile.user)
        user = UserSerializer(user_profile.user, context=self.get_serializer_context())

        # creating the forwarding_email of a user

        email = user.data['email']
        splitEmail = email.split('@')[0]
        randomInt = secrets.randbelow(9000) + 1000
        user_profile.forwarding_email = str(splitEmail + str(randomInt) + "@budgetlens.tech")
        user_profile.save()

        # TODO: a proper registration email need to be developed, right now, the function is proven to work
        # To use sendEmail function, you have to import it from the utility folder, for refrence, look at the imports at the top
        sendEmail(user.data['email'], 'User Successfully registered', 'User Successfully registered')
        # converting all email invites to friend requests upon registration
        friends = Friends.objects.filter(temp_email=user.data['email'])
        for friend in friends:
            friend.friend_user = user_profile.user
            friend.temp_email = None
            friend.save()
        return Response({
            # saves user and its data
            "user": user.data,
            "telephone_number": str(user_profile.telephone_number),
            "forwarding_email": str(user_profile.forwarding_email),
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
        except IntegrityError:
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
    """User API uses for returning user data from a Bearer Authentication"""
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def delete(self, request, *args, **kwargs):
        request.user.auth_bearertoken.delete()
        return Response({
            "data": "Successfully deleted"
        }, status=HTTP_200_OK)


class UserProfileAPI(generics.UpdateAPIView):
    """Handles updating user profile information through a PUT request """
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            data = {
                "username": user_profile.user.username,
                "first_name": user_profile.user.first_name,
                "last_name": user_profile.user.last_name,
                "email": user_profile.user.email,
                "telephone_number": str(user_profile.telephone_number),
                "forwarding_email": user_profile.forwarding_email
            }
            return Response(data, status=HTTP_200_OK)
        except Exception as e:
            return Response({"response": "There has been an error retrieving the user profile." + str(e)},
                            status=404)

    def update(self, request, *args, **kwargs):
        username = request.data.get('username', "NONE")
        first_name = request.data.get('first_name', "NONE")
        last_name = request.data.get('last_name', "NONE")
        email = request.data.get('email', "NONE")
        telephone_number = request.data.get('telephone_number', "NONE")

        # Makes sure all request input is valid
        result, status_code = self.is_valid_request(username, first_name, last_name, email, telephone_number, request.user)

        if result is None:  # no error, update can happen
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.user.username = username
            user_profile.user.first_name = first_name
            user_profile.user.last_name = last_name
            user_profile.user.email = email
            user_profile.user.save()

            user_profile.telephone_number = telephone_number
            user_profile.save()

            result, status_code = {"response": "Success"}, HTTP_200_OK
        return Response(result, status=status_code)

    @staticmethod
    def is_valid_request(username, first_name, last_name, email, telephone_number, user_instance):
        """Checks if the request is valid by looking at the form data key/values and email format"""

        # Ensure no missing key or values for the form data
        expected_input = {'Username': username, 'First Name': first_name, 'Last Name': last_name, 'Email': email,
                          'Phone Number': telephone_number}
        missing_inputs = []
        for key, value in expected_input.items():
            if value == "NONE" or value == "":
                missing_inputs.append(key)

        if missing_inputs:
            return {"response": "Missing field or value for " + str(missing_inputs) + "."}, HTTP_400_BAD_REQUEST

        # Validate phone number
        valid_telephone_number = PhoneNumber.from_string(telephone_number)
        if not valid_telephone_number.is_valid():
            return {"response": "Invalid phone number."}, HTTP_400_BAD_REQUEST

        user_queryset = User.objects.filter().exclude(id=user_instance.id)
        if user_queryset.filter(username=username).exists() or user_queryset.filter(email=email).exists():
            return {"response": "Username and email already exist"}, HTTP_400_BAD_REQUEST

        # Validate the email is a correct format
        try:
            validate_email(email)
        # For some reason ValidationError is not caught here, causing the tests to fail. Exception is caught instead
        except Exception:
            return {"response": "Invalid email format."}, HTTP_400_BAD_REQUEST
        else:
            return None, HTTP_200_OK


class GenerateDigitCodeView(generics.GenericAPIView):
    """
    An endpoint for verify if the email exists in the account
    """
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        # those two lines is for using the validated_data method
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get the user profile data
        user = serializer.validated_data
        userprofile = UserProfile.objects.get(user_id=user.id)

        # generate a random 6 digits number
        code = random.randint(100000, 999999)
        sendEmail(request.data["email"], 'Your reset password 6 digit code is here', str(code))

        # Update user profile 6 digits number
        userprofile.one_time_code = code
        userprofile.save()
        return Response({"response": "Success"}, HTTP_200_OK)


class ValidateDigitCodeView(generics.GenericAPIView):
    """
    An endpoint for verifying 6 digits code matches.
    """
    serializer_class = ValidateDigitSerializer

    def post(self, request, *args, **kwargs):
        # those two lines is for using the validated_data method
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get the user profile data
        userprofile = serializer.validated_data

        # check if the input match the user digit code
        match = True if userprofile.one_time_code == int(request.data["digit"]) else False
        if match:
            return Response({"response": "succeed"}, HTTP_200_OK)
        return Response({"response": "failed, doesn't match"}, HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.GenericAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        # those two lines is for using the validated_data method
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get the user
        user = serializer.validated_data

        # verify the two field password match
        if request.data.get("new_password") == request.data.get("re_password"):
            # Update password
            user.set_password(request.data.get("new_password"))
            user.save()

            return Response({
                "Message:": "The password has been changed"
            }, HTTP_200_OK)
        return Response({"response": "The password doesn't match"}, HTTP_400_BAD_REQUEST)
