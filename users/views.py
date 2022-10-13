from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import generics
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import password_validators_help_texts

from .models import UserProfile
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .authentication import BearerToken
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
