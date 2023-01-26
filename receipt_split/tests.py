from django.contrib.auth.models import User
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from users.models import UserProfile
from .models import ReceiptSplit

from merchant.models import Merchant
from receipts.models import Receipts
from receipts.tests import get_test_image_file
from users.authentication import BearerToken
from django.urls import reverse
from rest_framework.test import APITestCase


class ReceiptSplitAPITestCase(APITestCase):
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

        # the urls
        self.url_add_receipt_split = reverse('add_receipt_split')

        # Authenticate user before each test
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

    def test_add_receipt_split_invalid_users(self):
        response = self.client.post(
            self.url_add_receipt_split,
            data={
                'receipt': self.receipt.pk,
                'shared_user_ids': '100, 3',
                'is_shared_with_receipt_owner': False
            },
            format='json'
        )

        # Assert that the receipt split object was created successfully
        self.assertEqual(response.data['message'], "List of users do not exist.")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_add_receipt_split_invalid_string(self):
        response = self.client.post(
            self.url_add_receipt_split,
            data={
                'receipt': self.receipt.pk,
                'shared_user_ids': 'test, 3',
                'is_shared_with_receipt_owner': False
            },
            format='json'
        )

        # Assert that the receipt split object was created successfully
        self.assertEqual(response.data['message'], "Invalid list of user IDs. Please enter numbers separated by commas.")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_add_receipt_split_pass(self):
        response = self.client.post(
            self.url_add_receipt_split,
            data={
                'receipt': self.receipt.pk,
                'shared_user_ids': f'{self.user2.pk}, {self.user3.pk}',
                'shared_amount': 10,
                'is_shared_with_receipt_owner': False
            },
            format='json'
        )

        # Assert that the receipt split object was created successfully
        self.assertEqual(response.data['receipt'], self.receipt.pk)
        self.assertEqual(response.data['shared_user_ids'], f'{self.user2.pk}, {self.user3.pk}')

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_get_shared_user_list_pass(self):
        # Create a new ReceiptSplit object
        receiptsplit = ReceiptSplit.objects.create(
            receipt=self.receipt,
            shared_user_ids=f'{self.user2.pk}, {self.user3.pk}',
            is_shared_with_receipt_owner=False
        )

        # The url using kwargs receipt_id
        self.url_shared_users_list = reverse('get_user_list', kwargs={'receipt_id': self.receipt.pk})

        response = self.client.get(
            self.url_shared_users_list,
            format='json'
        )

        self.assertEqual(response.data['original_user'], self.receipt.user.first_name)

        # Loop and assert that all the shared users are correct
        user_id_list = list(map(int, receiptsplit.shared_user_ids.split(',')))
        for count, user_id in enumerate(user_id_list):
            user = User.objects.get(id=user_id)
            self.assertEqual(response.data['shared_users'][count], user.first_name)

        # Assert status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_shared_user_list_invalid_id(self):
        # Create a new ReceiptSplit object
        ReceiptSplit.objects.create(
            receipt=self.receipt,
            shared_user_ids=f'{self.user2.pk}, {self.user3.pk}',
            is_shared_with_receipt_owner=False
        )

        # The url using kwargs receipt_id with invalid id number e.g. 100
        self.url_shared_users_list = reverse('get_user_list', kwargs={'receipt_id': 100})

        response = self.client.get(
            self.url_shared_users_list,
            format='json'
        )

        self.assertEqual(response.data['message'], f"ReceiptSplit object with a receipt id of '{100}' does not exist")

        # Assert status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Do the same request but with invalid parameters
        # The url using kwargs receipt_id with invalid id number e.g. a
        self.url_shared_users_list = reverse('get_user_list', kwargs={'receipt_id': 'a'})

        response = self.client.get(
            self.url_shared_users_list,
            format='json'
        )

        self.assertEqual(response.data['message'], f"ReceiptSplit object with a receipt id of '{'a'}' does not exist")

        # Assert status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_shared_amount_pass(self):
        # Create a new ReceiptSplit object using the post request
        receiptsplit_data_id = self.client.post(
            self.url_add_receipt_split,
            data={
                'receipt': self.receipt.pk,
                'shared_amount': 10,
                'shared_user_ids': f'{self.user2.pk}, {self.user3.pk}',
            },
            format='json'
        ).data['id']
        receiptsplit = ReceiptSplit.objects.get(id=receiptsplit_data_id)

        # The url using kwargs receipt_id
        self.url_shared_amount = reverse('get_shared_amount', kwargs={'receipt_id': self.receipt.pk})

        response = self.client.get(
            self.url_shared_amount,
            format='json'
        )

        self.assertEqual(response.data['shared_amount'], receiptsplit.shared_amount)
        self.assertEqual(response.data['is_shared_with_receipt_owner'], receiptsplit.is_shared_with_receipt_owner)

        # Assert status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_shared_amount_invalid_id(self):
        # Create a new ReceiptSplit object using the post request
        self.client.post(
            self.url_add_receipt_split,
            data={
                'receipt': self.receipt.pk,
                'shared_user_ids': f'{self.user2.pk}, {self.user3.pk}',
                'shared_amount': 10.00,
                'is_shared_with_receipt_owner': False
            },
            format='json'
        )

        # The url using kwargs receipt_id with invalid id number e.g. 100
        self.url_shared_amount = reverse('get_shared_amount', kwargs={'receipt_id': 100})

        response = self.client.get(
            self.url_shared_amount,
            format='json'
        )

        self.assertEqual(response.data['message'], f"ReceiptSplit object with a receipt id of '{100}' does not exist")

        # Assert status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Do the same request but with invalid parameters
        # The url using kwargs receipt_id with invalid id number e.g. a
        self.url_shared_amount = reverse('get_shared_amount', kwargs={'receipt_id': 'a'})

        response = self.client.get(
            self.url_shared_amount,
            format='json'
        )

        self.assertEqual(response.data['message'], f"ReceiptSplit object with a receipt id of '{'a'}' does not exist")

        # Assert status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
