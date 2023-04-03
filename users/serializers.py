from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth import authenticate
from django.core import exceptions
import django.contrib.auth.password_validation as validators
from rest_framework.validators import UniqueValidator


class LoginSerializer(serializers.Serializer):
    """Login route using KNOX authentication"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class UserSerializer(serializers.ModelSerializer):
    """User values for gathering the values of a user in the Views Response"""

    # Make these field required (username and password are required by default)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """Overide the Vaidate method for validating the password"""
        user = User(**data)
        password = data.get('password')

        errors = dict()
        try:
            validators.validate_password(password=password, user=user)

        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        # Validate the password and then return the validation from the register serializer class
        return RegisterSerializer.validate(self, data)


class RegisterSerializer(serializers.ModelSerializer):
    """For registering a new user profile with user and telephone number"""
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ('user', 'telephone_number', 'forwarding_email')

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        # Create the new user with user_data before creating the user profile
        user = User.objects.create_user(
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password=user_data['password']
        )

        user_profile = UserProfile.objects.create(
            user=user,
            telephone_number=str(validated_data.pop('telephone_number')),
        )
        return user_profile


class EmailSerializer(serializers.Serializer):
    """For verify the user enters an email exists in the system"""
    email = serializers.EmailField()

    def validate(self, data):
        if User.objects.filter(email=data["email"]).exists():
            user = User.objects.get(email=data["email"])
            return user
        raise serializers.ValidationError("User doesn't exist")


class ValidateDigitSerializer(serializers.Serializer):
    """For verify the user enters the correct 6 digits code"""
    email = serializers.EmailField()
    digit = serializers.IntegerField()

    def validate(self, data):
        if User.objects.filter(email=data["email"]).exists():
            user = User.objects.get(email=data["email"])
            userprofile = UserProfile.objects.get(user_id=user.id)
            return userprofile
        raise serializers.ValidationError("User doesn't exist")


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    email = serializers.EmailField()
    new_password = serializers.CharField(required=True)
    re_password = serializers.CharField(required=True)

    def validate(self, data):
        if User.objects.filter(email=data["email"]).exists():
            user = User.objects.get(email=data["email"])
            return user
        raise serializers.ValidationError("User doesn't exist")
