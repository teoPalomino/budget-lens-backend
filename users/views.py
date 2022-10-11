import random
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import password_validators_help_texts

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, EmailSerializer, \
    ValidateDigitSerializer, ChangePasswordSerializer
from .models import UserProfile, Friends
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, AddFriendsSerializer
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

        # To use sendEmail function, you have to import it from the utility folder,
        # for reference, look at the imports at the top
        sendEmail(user.data['email'], 'User Successfully registered', 'User Successfully registered')
        return Response({
            # saves user and its data
            "user": user.data,
            "telephone_number": str(user_profile.telephone_number),
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
        }, HTTP_200_OK)


class UserProfileAPI(generics.UpdateAPIView):
    """Handles updating user profile information through a PUT request """
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        username = request.data.get('username', "NONE")
        first_name = request.data.get('first_name', "NONE")
        last_name = request.data.get('last_name', "NONE")
        email = request.data.get('email', "NONE")
        telephone_number = request.data.get('telephone_number', "NONE")

        # Makes sure all request input is valid
        result, status_code = self.is_valid_request(username, first_name, last_name, email, telephone_number)

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
    def is_valid_request(username, first_name, last_name, email, telephone_number):
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

        # Validate the email is a correct format
        try:
            validate_email(email)
        except ValidationError:
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

            else:


            # TODO: generate link to download app (???)

            # TODO: Send email to user to register, create record marked as temporary in database

            # TODO: when user registers, send/show them friend request

            return Response({"response": "Could not find this email in our database"})

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
