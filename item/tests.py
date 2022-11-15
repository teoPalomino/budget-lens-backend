from django.contrib.auth.models import User
from rest_framework import status

from item.models import Item
from merchant.models import Merchant
from receipts.models import Receipts
from receipts.tests import create_image, get_test_image_file
from users.authentication import BearerToken
from django.core.files.images import ImageFile
from django.urls import reverse
from rest_framework.test import APITransactionTestCase, APITestCase

from users.models import UserProfile


# Create your tests here.
class ItemsAPITest(APITransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(
            username='johncena123@gmail.com',
            email='momoamineahmadi@gmail.com',
            first_name='John',
            last_name='Cena',
            password='wrestlingrules123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            telephone_number="+1-613-555-0187"
        )
        self.data = {
            'username': 'johncena123@gmail.com',
            'password': 'wrestlingrules123'
        }

        self.token = BearerToken.objects.create(user=self.user)

        self.client.post(
            reverse('login_user'),
            data=self.data,
            format='json'
        )

        Receipts.objects.create(
            user=self.user,
            receipt_image=get_test_image_file(),
            merchant=Merchant.objects.create(name='starbucks'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            coupon=1,
            currency="CAD"
        )

        Item.objects.create(
            receipt=Receipts.objects.get(user=self.user),
            tax=1,
            name='coffee',
            price=10,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            receipt=Receipts.objects.get(user=self.user),
            tax=15,
            name='poutine',
            price=59,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            receipt=Receipts.objects.get(user=self.user),
            tax=200,
            name='mateo',
            price=121423432543241524130,
            important_dates="2022-10-09"
        )

    def test_add_new_item(self):
        pass

    def test_get_items(self):
        pass

    def test_get_items(self):
        pass

    def test_delete_item(self):
        delete_item_url = reverse('delete_item', kwargs={'item_id': 1})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_item_count = Item.objects.count()

        response = self.client.delete(delete_item_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Item.objects.count(), original_item_count - 1)
