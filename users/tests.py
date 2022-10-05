from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users.models import UserProfile


class UserAPITest(APITestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_user_registration(self):
        """
        Test Case for user.RegistrationAPI
        """
        registation_url = reverse('register_user')
        data = {
            'user': {
                'username': 'johncena123@gmail.com',
                'email': 'johncena123@gmail.com',
                'first_name': 'John',
                'last_name': 'Cena',
                'password': 'westlingrules123',
            },
            'telephone_number': 5141111111
        }

        response = self.client.post(
            registation_url,
            data=data,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get UserProfile value from database
        user_profile = UserProfile.objects.get(
            user=User.objects.get(
                username='johncena123@gmail.com'
            )
        )

        # Assert values in database match to values passed in to register
        self.assertEqual(data['user']['username'], user_profile.user.username)
        self.assertEqual(data['user']['email'], user_profile.user.email)
        self.assertEqual(data['user']['first_name'], user_profile.user.first_name)
        self.assertEqual(data['user']['last_name'], user_profile.user.last_name)
        self.assertEqual(data['telephone_number'], user_profile.telephone_number)

        # For the password, only make sure it's hashed using sha256 when stored in the database
        self.assertTrue('sha256' in user_profile.user.password)

    def test_user_login(self):
        """
        Test Case for user.LoginAPI
        """
        login_url = reverse('login_user')

        # Create a user in the database for testing
        user = User.objects.create_user(
            username='johncena123@gmail.com',
            email='johncena123@gmail.com',
            first_name='John',
            last_name='Cena',
            password='westlingrules123'
        )
        user_profile = UserProfile.objects.create(
            user=user,
            telephone_number=5141111111
        )

        data = {
            'username': 'johncena123@gmail.com',
            'password': 'westlingrules123'
        }

        response = self.client.post(
            login_url,
            data=data,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Assert values in user database match to values from the response
        self.assertEqual(response.data['user']['username'], user_profile.user.username)
        self.assertEqual(response.data['user']['email'], user_profile.user.email)
        self.assertEqual(response.data['user']['first_name'], user_profile.user.first_name)
        self.assertEqual(response.data['user']['last_name'], user_profile.user.last_name)

        # Get token from database and assert with value from response
        token = Token.objects.get(user_id=user.pk)
        self.assertEqual(response.data['token'], token.key)
