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

    def test_invalid_user_login(self):
        """
        Test Case for user.LoginAPI when user enters wrong data
        """
        login_url = reverse('login_user')

        data = {
            'username': 'wrongusername@gmail.com',
            'password': 'westlingrules123'
        }

        response = self.client.post(
            login_url,
            data=data,
            format='json'
        )

        # Assert bad request
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert values in user database match to values from the response
        self.assertEqual(response.data['non_field_errors'], ['Incorrect Credentials'])

        # Assert that no tokens were generated
        self.assertEqual(Token.objects.count(), 0)

    def test_view_user_instance(self):
        """
        Test Case for users.views.UserAPI
        """
        user_data_url = reverse('user_data')

        # Create user instance for the test
        user = User.objects.create_user(
            username='johncena123@gmail.com',
            email='johncena123@gmail.com',
            first_name='John',
            last_name='Cena',
            password='westlingrules123'
        )

        # Create token for the test
        token = Token.objects.create(user_id=user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        response = self.client.get(
            user_data_url,
            format='json',
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Assert values in user database match to values from the response
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['first_name'], user.first_name)
        self.assertEqual(response.data['last_name'], user.last_name)

    def test_invalid_token(self):
        """
        Test Case for users.views.UserAPI when we pass an invalid token
        """
        user_data_url = reverse('user_data')

        # Create invalid token for the test that is not in the database
        token = '1234'

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(
            user_data_url,
            format='json',
        )

        # Assert an unathorized status message
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Assert values in user database match to values from the response
        self.assertEqual(response.data['detail'], 'Invalid token.')

    def test_logout(self):
        """
        Test Case for user.views.LogoutAPI
        """
        logout_url = reverse('logout_user')

        # Create user instance for the test
        user = User.objects.create_user(
            username='johncena123@gmail.com',
            email='johncena123@gmail.com',
            first_name='John',
            last_name='Cena',
            password='westlingrules123'
        )

        # Create token for the test
        token = Token.objects.create(user_id=user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        response = self.client.delete(
            logout_url,
            format='json',
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Assert that the data message is correct
        self.assertEqual(response.data['data'], 'Succesfully deleted')

        # Assert that there are no more tokens in the database
        self.assertEqual(Token.objects.count(), 0)
