from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.authentication import BearerToken

from users.models import UserProfile
from .models import Friends


class FriendsAPITest(APITestCase):
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
            password='wrestlingrules123'
        )

        self.user2 = User.objects.create_user(
            username='bingbong@gmail.com',
            email='bingbong@gmail.com',
            first_name='bing',
            last_name='bong',
            password='bingbong123'
        )

        self.user_profile = UserProfile.objects.create(
            user=self.user,
            telephone_number="+1-613-555-0187"
        )

        self.user_profile2 = UserProfile.objects.create(
            user=self.user2,
            telephone_number="+1-438-979-4449"
        )

    def test_add_friend_success(self):
        """
        Test Case for user.AddFriendsAPI
        """
        addfriend_url = reverse('add_friends')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data = {
            'email': 'bingbong@gmail.com'
        }

        response = self.client.post(
            addfriend_url,
            data=data,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend2 = Friends.objects.get(main_user=self.user.id, friend_user=self.user2.id, confirmed=False)

        # Showing the existence of the friend object (friend request)
        self.assertTrue(friend2)

    def test_add_friend_adding_yourself(self):
        """
        Test Case for user.AddFriendsAPI
        """
        addfriend_url = reverse('add_friends')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data = {
            'email': 'johncena123@gmail.com'
        }

        response = self.client.post(
            addfriend_url,
            data=data,
            format='json'
        )

        # Assert a BAD REQUEST status message
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"response":"You cannot add yourself as a friend."}')

    def test_add_friend_duplicate(self):
        """
        Test Case for user.AddFriendsAPI
        """
        addfriend_url = reverse('add_friends')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data = {
            'email': 'bingbong@gmail.com'
        }

        response = self.client.post(
            addfriend_url,
            data=data,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend2 = Friends.objects.get(main_user=self.user.id, friend_user=self.user2.id, confirmed=False)

        # Showing the existence of the friend object (friend request)
        self.assertTrue(friend2)

        # resending the friend request
        response = self.client.post(
            addfriend_url,
            data=data,
            format='json'
        )

        # Assert a bad request status message
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"response":"You have already sent a friend request to this user."}')


    def test_invite_friend_success(self):
        """
        Test Case for user.InviteFriendsAPI
        """
        invitefriend_url = reverse('invite_friends')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data = {
            'email': 'nizareljurdi@gmail.com'
        }

        response = self.client.post(
            invitefriend_url,
            data=data,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend2 = Friends.objects.get(main_user=self.user.id, confirmed=False, temp_email=data['email'])

        # Showing the existence of the friend object (friend invite)
        self.assertTrue(friend2)

    def test_invite_friend_existing_user(self):
        """
        Test Case for user.InviteFriendsAPI
        """
        invitefriend_url = reverse('invite_friends')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data = {
            'email': 'bingbong@gmail.com'
        }

        response = self.client.post(
            invitefriend_url,
            data=data,
            format='json'
        )

        # Assert a bad request status message
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'"This email is already registered as a user"')

    def test_invite_friend_duplicate_invite(self):
        """
        Test Case for user.InviteFriendsAPI
        """
        invitefriend_url = reverse('invite_friends')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data = {
            'email': 'nizareljurdi@gmail.com'
        }

        response = self.client.post(
            invitefriend_url,
            data=data,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend2 = Friends.objects.get(main_user=self.user.id, confirmed=False, temp_email=data['email'])

        # Showing the existence of the friend object (friend invite)
        self.assertTrue(friend2)

        # Sending a duplicate request
        response = self.client.post(
            invitefriend_url,
            data=data,
            format='json'
        )

        # Assert a bad request status message
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'"U have already sent an invite to this email"')

