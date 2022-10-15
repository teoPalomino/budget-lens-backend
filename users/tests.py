from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.authentication import BearerToken
from unittest import mock

from users.models import UserProfile


class UserAPITest(APITestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def helper_create_user_instance(self):
        """
        Helper method for creating a new user in db
        """
        self.user = User.objects.create_user(
            username='johncena123@gmail.com',
            email='johncena123@gmail.com',
            first_name='John',
            last_name='Cena',
            password='westlingrules123'
        )

        self.user_profile = UserProfile.objects.create(
            user=self.user,
            telephone_number="+1-613-555-0187"
        )

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
            'telephone_number': "+1-613-555-0187"
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
        self.helper_create_user_instance()

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
        self.assertEqual(response.data['user']['username'], self.user_profile.user.username)
        self.assertEqual(response.data['user']['email'], self.user_profile.user.email)
        self.assertEqual(response.data['user']['first_name'], self.user_profile.user.first_name)
        self.assertEqual(response.data['user']['last_name'], self.user_profile.user.last_name)

        # Get token from database and assert with value from response
        token = BearerToken.objects.get(user_id=self.user.pk)
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
        self.assertEqual(BearerToken.objects.count(), 0)

    def test_view_user_instance(self):
        """
        Test Case for users.views.UserAPI
        """
        user_data_url = reverse('user_data')

        # Create user instance for the test
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        response = self.client.get(
            user_data_url,
            format='json',
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Assert values in user database match to values from the response
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)

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
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        response = self.client.delete(
            logout_url,
            format='json',
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Assert that the data message is correct
        self.assertEqual(response.data['data'], 'Successfully deleted')

        # Assert that there are no more tokens in the database
        self.assertEqual(BearerToken.objects.count(), 0)

    def test_edit_user_profile_success(self):
        profile_edit_url = reverse('user_profile')

        # Create user instance for the test
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        data = {
            'username': 'notjohncena@gmail.com',
            'first_name': 'Joey',
            'last_name': 'Senorita',
            'email': 'notjohncena@gmail.com',
            'telephone_number': "+1-613-555-0187"
        }

        response = self.client.put(
            profile_edit_url,
            data=data,
            format='multipart'
        )

        # Retrieve the UserProfile to check against
        user_profile = UserProfile.objects.get(user=self.user)

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Assert the response was a success
        self.assertEquals(response.content, b'{"response":"Success"}')

        # Assert values in database match the updated values
        self.assertEqual(data['username'], user_profile.user.username)
        self.assertEqual(data['email'], user_profile.user.email)
        self.assertEqual(data['first_name'], user_profile.user.first_name)
        self.assertEqual(data['last_name'], user_profile.user.last_name)
        self.assertEqual(data['telephone_number'], user_profile.telephone_number)

    def test_edit_user_profile_invalid_email(self):
        profile_edit_url = reverse('user_profile')

        # Create user instance for the test
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        data = {
            'username': 'notjohncena@gmail.com',
            'first_name': 'Joey',
            'last_name': 'Senorita',
            'email': 'notjohncena@gmail',
            'telephone_number': "+1-613-555-0187"
        }

        response = self.client.put(
            profile_edit_url,
            data=data,
            format='multipart'
        )

        # Assert a 400 status code
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response is an invalid email format
        self.assertEquals(response.content, b'{"response":"Invalid email format."}')

    def test_edit_user_profile_invalid_telephone_number(self):
        profile_edit_url = reverse('user_profile')

        # Create user instance for the test
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        data = {
            'username': 'notjohncena@gmail.com',
            'first_name': 'Joey',
            'last_name': 'Senorita',
            'email': 'notjohncena@gmail.com',
            'telephone_number': "+161355507"
        }

        response = self.client.put(
            profile_edit_url,
            data=data,
            format='multipart'
        )

        # Assert a 400 status code
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"response":"Invalid phone number."}')

    def test_edit_user_profile_missing_keys(self):
        profile_edit_url = reverse('user_profile')

        # Create user instance for the test
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        data = {
            'username': 'notjohncena@gmail.com',
            'first_name': 'Joey',
            'last_name': 'Senorita'
        }
        response = self.client.put(
            profile_edit_url,
            data=data,
            format='multipart'
        )

        # Assert a 400 status code
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"response":"Missing field or value for [\'Email\', \'Phone Number\']."}')

    def test_generateDigitCode_existedUser_succeed(self):
        """
        Test Case for user.views.GenerateDigitCodeView
        The 6 randomized digit code should be generated with the existed User
        """
        self.create_user()

        generate_digit_url = reverse('generate_digit_code')

        data = {
            'email': 'johncena123@gmail.com'
        }

        response = self.client.post(
            generate_digit_url,
            data=data,
            format='json'
        )

        # Assert a 200 status code
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"response":"Success"}')

        # Assert the 6 digits code has been saved
        user = User.objects.get(email='johncena123@gmail.com')
        userprofile = UserProfile.objects.get(user_id=user.id)
        self.assertIsNotNone(userprofile.one_time_code)

    def test_generateDigitCode_unExistedUser_failed(self):
        """
        Test Case for user.views.GenerateDigitCodeView
        The 6 randomized digit code should not be generated with the unExisted User
        """

        generate_digit_url = reverse('generate_digit_code')

        data = {
            'email': 'unexistedemail@gmail.com'
        }

        response = self.client.post(
            generate_digit_url,
            data=data,
            format='json'
        )

        # Assert a 400 status code
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"non_field_errors":["User doesn\'t exist"]}')

    def test_validateDigitCode_unExistedUser_failed(self):
        """
        Test Case for user.views.GenerateDigitCodeView
        The 6 randomized digit code should not be generated with the unExisted User
        """
        validate_digit_url = reverse('validate_digit_code')

        data = {
            'email': 'unexistedemail@gmail.com',
            'digit': 123456
        }

        response = self.client.post(
            validate_digit_url,
            data=data,
            format='json'
        )

        # Assert a 400 status code
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"non_field_errors":["User doesn\'t exist"]}')

    def test_validateDigitCode_uncorrectedCode_failed(self):
        """
        Test Case for user.views.GenerateDigitCodeView
        The 6 randomized digit code should not be generated with the unExisted User
        """
        self.generate_digit_code()

        validate_digit_url = reverse('validate_digit_code')

        data = {
            'email': 'johncena123@gmail.com',
            'digit': 000000
        }

        response = self.client.post(
            validate_digit_url,
            data=data,
            format='json'
        )

        # Assert a 400 status code
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"response":"failed, doesn\'t match"}')

    def test_validateDigitCode_correctedCode_succeed(self):
        """
        Test Case for user.views.GenerateDigitCodeView
        The 6 randomized digit code should not be generated with the unExisted User
        """
        self.generate_digit_code()

        validate_digit_url = reverse('validate_digit_code')
        user = User.objects.get(email='johncena123@gmail.com')
        userprofile = UserProfile.objects.get(user_id=user.id)
        data = {
            'email': 'johncena123@gmail.com',
            'digit': userprofile.one_time_code
        }

        response = self.client.post(
            validate_digit_url,
            data=data,
            format='json'
        )

        # Assert a 200 status code
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Assert the response was a success
        self.assertEquals(response.content, b'{"response":"succeed"}')

    def create_user(self):
        """
        A helper method to create user and avoid duplicated code
        """
        registration_url = reverse('register_user')
        data = {
            'user': {
                'username': 'johncena123@gmail.com',
                'email': 'johncena123@gmail.com',
                'first_name': 'John',
                'last_name': 'Cena',
                'password': 'westlingrules123',
            },
            'telephone_number': "+1-613-555-0187"
        }

        response = self.client.post(
            registration_url,
            data=data,
            format='json'
        )

    def generate_digit_code(self):
        """
        A helper method to create a user and generate a 6 digits code to him
        """

        self.create_user()

        generate_digit_url = reverse('generate_digit_code')

        data = {
            'email': 'johncena123@gmail.com'
        }

        self.client.post(
            generate_digit_url,
            data=data,
            format='json'
        )
