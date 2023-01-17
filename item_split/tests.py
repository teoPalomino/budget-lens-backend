from django.contrib.auth.models import User
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from item.models import Item
from users.models import UserProfile

from merchant.models import Merchant
from receipts.models import Receipts
from receipts.tests import get_test_image_file
from users.authentication import BearerToken
from django.urls import reverse
from rest_framework.test import APITestCase


class ItemSplitAPITestCase(APITestCase):
    def setUp(self):
        # Create the user
        self.user1 = User.objects.create_user(
            username='johncena123@gmail.com',
            email='johncena123@gmail.com',
            first_name='John',
            last_name='Cena',
            password='wrestlingrules123'
        )
        self.user_profile1 = UserProfile.objects.create(
            user=self.user1,
            telephone_number="+1-613-555-0187"
        )

        self.user2 = User.objects.create_user(
            username='billybatson@gmail.com',
            email='billybatson@gmail.com',
            first_name='Billy',
            last_name='Baston',
            password='#Shazam123'
        )
        self.user_profile2 = UserProfile.objects.create(
            user=self.user2,
            telephone_number="+1-613-293-4960"
        )

        self.user3 = User.objects.create_user(
            username='batcave@gmail.com',
            email='batcave@gmail.com',
            first_name='Bat',
            last_name='Man',
            password='robin1234'
        )
        self.user_profile3 = UserProfile.objects.create(
            user=self.user3,
            telephone_number="+1-514-555-0187"
        )

        # Generate the users token
        self.token = BearerToken.objects.create(user=self.user1)

        # Create the receipt
        self.receipt = Receipts.objects.create(
            user=self.user1,
            receipt_image=get_test_image_file(),
            merchant=Merchant.objects.create(name='starbucks'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            coupon=1,
            currency="CAD"
        )

        self.item = Item.objects.create(
            user=self.user1,
            receipt=Receipts.objects.get(user=self.user1),
            name='coffee',
            price=10.15,
            important_dates="2022-10-09"
        )

        # the urls
        self.url_add_item_split = reverse('add_item_split')

        # Authenticate user before each test
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

    def test_add_item_split_invalid_users(self):
        respose = self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': '100, 3',
            },
            format='json'
        )

        # Assert that the item split object was created successfully
        self.assertEqual(respose.data['message'], "List of users do not exist.")

        self.assertEqual(respose.status_code, HTTP_400_BAD_REQUEST)

    def test_add_item_split_invalid_string(self):
        respose = self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': 'test, 3',
            },
            format='json'
        )

        # Assert that the item split object was created successfully
        self.assertEqual(respose.data['message'], "Invalid list of user IDs. Please enter numbers separated by commas.")

        self.assertEqual(respose.status_code, HTTP_400_BAD_REQUEST)

    def test_add_item_split_pass(self):
        respose = self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': f'{self.user2.pk}, {self.user3.pk}',
            },
            format='json'
        )

        print(respose.data)
        # Assert that the item split object was created successfully
        self.assertEqual(respose.data['item'], self.item.pk)
        self.assertEqual(respose.data['shared_user_ids'], f'{self.user2.pk}, {self.user3.pk}')

        self.assertEqual(respose.status_code, HTTP_201_CREATED)
