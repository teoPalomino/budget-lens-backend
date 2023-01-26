from django.contrib.auth.models import User
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from item.models import Item
from users.models import UserProfile
from .models import ItemSplit

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
            price=10.15
        )

        # the urls
        self.url_add_item_split = reverse('add_item_split')

        # Authenticate user before each test
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

    def test_add_item_split_invalid_users(self):
        response = self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': '100, 3',
                'is_shared_with_item_user': False
            },
            format='json'
        )

        # Assert that the item split object was created successfully
        self.assertEqual(response.data['message'], "List of users do not exist.")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_add_item_split_invalid_string(self):
        # Case1:  Where shared_user_ids string has letters
        response = self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': 'test, 3',
                'is_shared_with_item_user': False
            },
            format='json'
        )

        # Assert that the item split object was created successfully
        self.assertEqual(response.data['message'], "Invalid list of user IDs. Please enter numbers separated by commas.")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Case2:  Where shared_user_ids string has duplicate numbers
        response = self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': '3, 3',
                'is_shared_with_item_user': False
            },
            format='json'
        )

        # Assert that the item split object was created successfully
        self.assertEqual(response.data['message'], "List of user IDs contains duplicates.")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_add_item_split_pass(self):
        response = self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': f'{self.user2.pk}, {self.user3.pk}',
                'is_shared_with_item_user': False
            },
            format='json'
        )

        # Assert that the item split object was created successfully
        self.assertEqual(response.data['item']['item_id'], self.item.pk)
        self.assertEqual(response.data['item']['item_name'], self.item.name)
        self.assertEqual(float(response.data['item']['item_price']), float(self.item.price))
        self.assertEqual(response.data['shared_user_ids'], f'{self.user2.pk}, {self.user3.pk}')

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_get_shared_user_list_pass(self):
        # Create a new ItemSplit object
        itemsplit = ItemSplit.objects.create(
            item=self.item,
            shared_user_ids=f'{self.user2.pk}, {self.user3.pk}',
            is_shared_with_item_user=False
        )

        # The url using kwargs item_id
        self.url_shared_users_list = reverse('get_user_list', kwargs={'item_id': self.item.pk})

        response = self.client.get(
            self.url_shared_users_list,
            format='json'
        )

        self.assertEqual(response.data['original_user'], self.item.user.first_name)

        # Loop and assert that all of the shared users are correct
        user_id_list = list(map(int, itemsplit.shared_user_ids.split(',')))
        for count, user_id in enumerate(user_id_list):
            user = User.objects.get(id=user_id)
            self.assertEqual(response.data['shared_users'][count], user.first_name)

        # Assert status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_shared_user_list_invalid_id(self):
        # Create a new ItemSplit object
        ItemSplit.objects.create(
            item=self.item,
            shared_user_ids=f'{self.user2.pk}, {self.user3.pk}',
            is_shared_with_item_user=False
        )

        # The url using kwargs item_id with invalid id number eg. 100
        self.url_shared_users_list = reverse('get_user_list', kwargs={'item_id': 100})

        response = self.client.get(
            self.url_shared_users_list,
            format='json'
        )

        self.assertEqual(response.data['message'], f"ItemSplit object with item id of '{100}' does not exist")

        # Assert status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Do the same request but with invalid parameters
        # The url using kwargs item_id with invalid id number eg. a
        self.url_shared_users_list = reverse('get_user_list', kwargs={'item_id': 'a'})

        response = self.client.get(
            self.url_shared_users_list,
            format='json'
        )

        self.assertEqual(response.data['message'], f"ItemSplit object with item id of '{'a'}' does not exist")

        # Assert status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_shared_amount_pass(self):
        # Create a new ItemSplit object using the post request
        itemsplit_data_id = self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': f'{self.user2.pk}, {self.user3.pk}',
            },
            format='json'
        ).data['id']
        itemsplit = ItemSplit.objects.get(id=itemsplit_data_id)

        # The url using kwargs item_id
        self.url_shared_amount = reverse('get_shared_amount', kwargs={'item_id': self.item.pk})

        response = self.client.get(
            self.url_shared_amount,
            format='json'
        )

        self.assertEqual(response.data['shared_amount'], itemsplit.shared_amount)
        self.assertEqual(response.data['is_shared_with_item_user'], itemsplit.is_shared_with_item_user)

        # Assert status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_shared_amount_invalid_id(self):
        # Create a new ItemSplit object using the post request
        self.client.post(
            self.url_add_item_split,
            data={
                'item': self.item.pk,
                'shared_user_ids': f'{self.user2.pk}, {self.user3.pk}',
                'is_shared_with_item_user': False
            },
            format='json'
        )

        # The url using kwargs item_id with invalid id number eg. 100
        self.url_shared_amount = reverse('get_shared_amount', kwargs={'item_id': 100})

        response = self.client.get(
            self.url_shared_amount,
            format='json'
        )

        self.assertEqual(response.data['message'], f"ItemSplit object with item id of '{100}' does not exist")

        # Assert status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Do the same request but with invalid parameters
        # The url using kwargs item_id with invalid id number eg. a
        self.url_shared_amount = reverse('get_shared_amount', kwargs={'item_id': 'a'})

        response = self.client.get(
            self.url_shared_amount,
            format='json'
        )

        self.assertEqual(response.data['message'], f"ItemSplit object with item id of '{'a'}' does not exist")

        # Assert status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
