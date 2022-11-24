from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.authentication import BearerToken

from users.models import UserProfile
from users.serializers import UserSerializer
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

        self.user3 = User.objects.create_user(
            username='johnnybravo@gmail.com',
            email='johnnybravo@gmail.com',
            first_name='johnny',
            last_name='bravo',
            password='johnnybravo123'
        )

        self.user_profile = UserProfile.objects.create(
            user=self.user,
            telephone_number="+1-613-555-0187"
        )

        self.user_profile2 = UserProfile.objects.create(
            user=self.user2,
            telephone_number="+1-438-979-4449"
        )

        self.user_profile3 = UserProfile.objects.create(
            user=self.user3,
            telephone_number="+1-323-555-1234",
        )

    def test_friend_requests_success(self):
        """
        Test Case for user.AddFriendsAPI
        """
        friend_requests_url = reverse('friend_requests')

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
            friend_requests_url,
            data=data,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend2 = Friends.objects.get(main_user=self.user.id, friend_user=self.user2.id, confirmed=False)

        # Showing the existence of the friend object (friend request)
        self.assertTrue(friend2)

    def test_friend_requests_adding_yourself(self):
        """
        Test Case for user.AddFriendsAPI
        """
        friend_requests_url = reverse('friend_requests')

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
            friend_requests_url,
            data=data,
            format='json'
        )

        # Assert a BAD REQUEST status message
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response was a failure
        self.assertEquals(response.content, b'{"response":"You cannot add yourself as a friend."}')

    def test_friend_requests_duplicate(self):
        """
        Test Case for user.AddFriendsAPI
        """
        friend_requests_url = reverse('friend_requests')

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
            friend_requests_url,
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
            friend_requests_url,
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

    def test_pending_friend_requests_sent_and_received(self):
        """
        Test Case for FriendRequestsAPI
        """
        friend_requests_url = reverse('friend_requests')

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

        data1 = {
            'email': 'bingbong@gmail.com'
        }

        data2 = {
            'email': 'johnnybravo@gmail.com'
        }

        # send a friend request
        response1 = self.client.post(
            friend_requests_url,
            data=data1,
            format='json'
        )

        response2 = self.client.post(
            friend_requests_url,
            data=data2,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        self.assertEquals(response2.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend_requests_sent = Friends.objects.filter(main_user=self.user.id, confirmed=False)
        friend_requests_received = Friends.objects.filter(friend_user=self.user.id, confirmed=False)
        self.assertTrue(friend_requests_sent)
        self.assertEquals(len(friend_requests_sent), 2)
        self.assertFalse(friend_requests_received)

        response3 = self.client.get(
            friend_requests_url,
            format='json'
        )

        self.assertEquals(response3.status_code, status.HTTP_200_OK)

        # Assert the response returns the same number of friend requests that are in the database
        self.assertEquals(len(response3.data['requests_sent']), len(friend_requests_sent))
        self.assertEquals(len(response3.data['requests_received']), len(friend_requests_received))

        token2 = BearerToken.objects.create(user_id=self.user2.pk)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token2.key)

        response4 = self.client.get(
            friend_requests_url,
            format='json'
        )
        self.assertEquals(response4.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend_requests_sent = Friends.objects.filter(main_user=self.user2.id, confirmed=False)
        friend_requests_received = Friends.objects.filter(friend_user=self.user2.id, confirmed=False)
        self.assertFalse(friend_requests_sent)
        self.assertEquals(len(friend_requests_received), 1)
        self.assertTrue(friend_requests_received)

        # Assert the response returns the same number of friend requests that are in the database
        self.assertEquals(len(response4.data['requests_sent']), len(friend_requests_sent))
        self.assertEquals(len(response4.data['requests_received']), len(friend_requests_received))

    def test_friend_request_response_accepted(self):
        """
        Test Case for FriendRequestAPI
        """
        friend_requests_url = reverse('friend_requests')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token1 = BearerToken.objects.create(user_id=self.user.pk)

        # accept friend request from user using response 1
        accept_friend_url = reverse('friend_requests', kwargs={'friend_id': self.user.id, 'answer': 1})

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1.key)

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data1 = {
            'email': 'bingbong@gmail.com'
        }

        data2 = {
            'email': 'johnnybravo@gmail.com'
        }

        # send a friend request
        response1 = self.client.post(
            friend_requests_url,
            data=data1,
            format='json'
        )

        response2 = self.client.post(
            friend_requests_url,
            data=data2,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        self.assertEquals(response2.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend_requests1 = Friends.objects.filter(main_user=self.user.id, confirmed=False)
        self.assertTrue(friend_requests1)
        self.assertEquals(len(friend_requests1), 2)

        token2 = BearerToken.objects.create(user_id=self.user2.pk)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token2.key)

        response3 = self.client.put(
            accept_friend_url,
            format='json'
        )
        self.assertEquals(response3.status_code, status.HTTP_200_OK)

        friend_requests2 = Friends.objects.filter(friend_user=self.user2.id, confirmed=True)
        self.assertEquals(len(friend_requests2), 1)
        self.assertTrue(friend_requests2)

        friend_requests3 = Friends.objects.filter(main_user=self.user.id, confirmed=True)
        self.assertEquals(len(friend_requests3), 1)
        self.assertTrue(friend_requests3)

    def test_friend_request_response_rejected(self):
        """
        Test Case for FriendRequestAPI
        """
        friend_requests_url = reverse('friend_requests')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token1 = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1.key)

        # reject friend request from user using answer: 0
        reject_friend_url = reverse('friend_requests', kwargs={'friend_id': self.user.id, 'answer': 0})

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data1 = {
            'email': 'bingbong@gmail.com'
        }

        data2 = {
            'email': 'johnnybravo@gmail.com'
        }

        # send a friend request
        response1 = self.client.post(
            friend_requests_url,
            data=data1,
            format='json'
        )

        response2 = self.client.post(
            friend_requests_url,
            data=data2,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        self.assertEquals(response2.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend_requests1 = Friends.objects.filter(main_user=self.user.id, confirmed=False)
        self.assertTrue(friend_requests1)
        self.assertEquals(len(friend_requests1), 2)

        token2 = BearerToken.objects.create(user_id=self.user2.pk)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token2.key)

        response3 = self.client.put(
            reject_friend_url,
            format='json'
        )
        self.assertEquals(response3.status_code, status.HTTP_200_OK)

        friend_requests2 = Friends.objects.filter(friend_user=self.user2.id, confirmed=True)
        self.assertEquals(len(friend_requests2), 0)
        self.assertFalse(friend_requests2)

        friend_requests3 = Friends.objects.filter(main_user=self.user.id, confirmed=True)
        self.assertEquals(len(friend_requests3), 0)
        self.assertFalse(friend_requests3)

    def test_friends(self):
        """
        Test Case for FriendAPI
        """
        friend_requests_url = reverse('friend_requests')
        friends_url = reverse('friends')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        # accept friend request from user using response 1
        accept_request_url = reverse('friend_requests', kwargs={'friend_id': self.user.id, 'answer': 1})
        get_friend_url = reverse('friends', kwargs={'friend_id': self.user.id})

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data1 = {
            'email': 'bingbong@gmail.com'
        }

        data2 = {
            'email': 'johnnybravo@gmail.com'
        }


        # send a friend request
        response1 = self.client.post(
            friend_requests_url,
            data=data1,
            format='json'
        )

        response2 = self.client.post(
            friend_requests_url,
            data=data2,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        self.assertEquals(response2.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend_requests1 = Friends.objects.filter(main_user=self.user.id, confirmed=False)
        self.assertTrue(friend_requests1)
        self.assertEquals(len(friend_requests1), 2)

        token2 = BearerToken.objects.create(user_id=self.user2.pk)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token2.key)

        # accept friend request
        response3 = self.client.put(
            accept_request_url,
            format='json'
        )
        self.assertEquals(response3.status_code, status.HTTP_200_OK)

        friend_requests2 = Friends.objects.filter(friend_user=self.user2.id, confirmed=True)
        self.assertEquals(len(friend_requests2), 1)
        self.assertTrue(friend_requests2)

        friend_requests3 = Friends.objects.filter(main_user=self.user.id, confirmed=True)
        self.assertEquals(len(friend_requests3), 1)
        self.assertTrue(friend_requests3)

        # get all friends
        response4 = self.client.get(
            friends_url,
            format='json'
        )
        self.assertEquals(response4.status_code, status.HTTP_200_OK)

        # get specific friend
        response5 = self.client.get(
            get_friend_url,
            format='json'
        )
        self.assertEquals(response5.status_code, status.HTTP_200_OK)

    def test_delete_friend(self):
        """
        Test Case for FriendAPI
        """
        friend_requests_url = reverse('friend_requests')

        # Create 2 users in the database for testing
        self.helper_create_user_instance()

        # Create token for the test
        token = BearerToken.objects.create(user_id=self.user.pk)

        # Enter credentials for authentication using the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        # accept friend request from user using response 1
        accept_request_url = reverse('friend_requests', kwargs={'friend_id': self.user.id, 'answer': 1})

        # delete friend url
        delete_friend_url = reverse('friends', kwargs={'friend_id': self.user.id})

        # Getting all friend objects from the db
        friend1 = Friends.objects.all()

        # Showing the absence of friend objects in the db
        self.assertFalse(friend1)

        data1 = {
            'email': 'bingbong@gmail.com'
        }

        data2 = {
            'email': 'johnnybravo@gmail.com'
        }


        # send a friend request
        response1 = self.client.post(
            friend_requests_url,
            data=data1,
            format='json'
        )

        response2 = self.client.post(
            friend_requests_url,
            data=data2,
            format='json'
        )

        # Assert a good status message
        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        self.assertEquals(response2.status_code, status.HTTP_200_OK)

        # Get friends table values from database
        friend_requests1 = Friends.objects.filter(main_user=self.user.id, confirmed=False)
        self.assertTrue(friend_requests1)
        self.assertEquals(len(friend_requests1), 2)

        token2 = BearerToken.objects.create(user_id=self.user2.pk)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token2.key)

        # accept friend request
        response3 = self.client.put(
            accept_request_url,
            format='json'
        )
        self.assertEquals(response3.status_code, status.HTTP_200_OK)

        # showing the new confirmed friend table with friend user user2
        friend_requests2 = Friends.objects.filter(friend_user=self.user2.id, confirmed=True)
        self.assertEquals(len(friend_requests2), 1)
        self.assertTrue(friend_requests2)

        # showing the new confirmed friend table with main user user
        friend_requests3 = Friends.objects.filter(main_user=self.user.id, confirmed=True)
        self.assertEquals(len(friend_requests3), 1)
        self.assertTrue(friend_requests3)

        # get all friends
        response4 = self.client.delete(
            delete_friend_url,
            format='json'
        )
        self.assertEquals(response4.status_code, status.HTTP_200_OK)

        # showing the friend table with friend user user2 is deleted
        friend_requests2 = Friends.objects.filter(friend_user=self.user2.id, confirmed=True)
        self.assertEquals(len(friend_requests2), 0)
        self.assertFalse(friend_requests2)

        # showing the friend table with main user user is deleted
        friend_requests3 = Friends.objects.filter(main_user=self.user.id, confirmed=True)
        self.assertEquals(len(friend_requests3), 0)
        self.assertFalse(friend_requests3)



