import pdb
from django.contrib.auth.models import User
from rest_framework import status

from item.models import Item
from item.serializers import ItemSerializer
from merchant.models import Merchant
from receipts.models import Receipts
from receipts.tests import create_image, get_test_image_file
from users.authentication import BearerToken
from django.core.files.images import ImageFile
from django.urls import reverse
from rest_framework.test import APITransactionTestCase, APITestCase

from users.models import UserProfile
from rest_framework.renderers import JSONRenderer
from django.core import serializers


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

        self.receipt1 = Receipts.objects.create(
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
            name='coffee',
            price=10,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            receipt=Receipts.objects.get(user=self.user),
            name='poutine',
            price=59,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            receipt=Receipts.objects.get(user=self.user),
            name='mateo',
            price=121423432543241524130,
            important_dates="2022-10-09"
        )

    def test_add_new_item(self):  
    # This test checks if a new item is created and checks if the list of items is increased

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_item_count = Item.objects.count()

        response = self.client.post(
            reverse('add_item'),
            data={
                "receipt_id": self.receipt1.id,
                "name" : "potato",
                "price": 1.0,
                "important_dates": "1990-12-12",
            }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Item.objects.count(), original_item_count + 1)

    def test_item_details(self):
    # This test checks if the specific item is returned, it does this by checking if
    # receipt_id, price, name and important_dates match the database

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get(
            reverse('item_details',
            kwargs={'item_id': Item.objects.get(price=10).id}),
            format='multipart')
            
        item = Item.objects.get(price=10)
        self.assertEquals(response.data[0]['receipt_id'], item.receipt_id)
        self.assertEquals(response.data[0]['price'], item.price)
        self.assertEquals(response.data[0]['name'], item.name)
        self.assertEquals(response.data[0]['important_dates'], str(item.important_dates))


    def test_item_total(self):
    # This test checks if the response of total price and the list of each item
    # match with what is in our database. Same implementation as the api.

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        
        response = self.client.get(
            reverse('items'),
            format='multipart')

        items = Item.objects.all()
        item_costs_dict = {}
        item_total_cost = 0
        if items.exists():
            for item in items:
                item_costs_dict[item.id] = [item.receipt_id,
                                            item.name,
                                            item.price,
                                            item.important_dates,]
                item_total_cost += int(item.price)
        
        self.assertEquals(response.data['totalPrice'], item_total_cost)
        self.assertEquals(response.data['items'], item_costs_dict)

    def test_delete_item(self):
        delete_item_url = reverse('delete_item', kwargs={'item_id': 1})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_item_count = Item.objects.count()

        response = self.client.delete(delete_item_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Item.objects.count(), original_item_count - 1)
