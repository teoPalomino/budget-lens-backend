import datetime
from random import randint
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.status import HTTP_200_OK

from item.models import Item

from merchant.models import Merchant
from receipts.models import Receipts
from category.models import Category
from receipts.tests import get_test_image_file
from users.authentication import BearerToken
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

        self.category1 = Category.objects.create(
            user=self.user,
            category_name="clothes",
            category_toggle_star=False,
            parent_category_id=None
        )

        Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='coffee',
            category_id=self.category1,
            price=10.15,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='poutine',
            category_id=self.category1,
            price=59.99,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='mateo',
            category_id=self.category1,
            price=12.99,
            important_dates="2022-10-09"
        )

    def test_add_new_item(self):
        # This test checks if a new item is created and checks if the list of items is increased

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_item_count = Item.objects.count()

        response = self.client.post(
            reverse('add_item'),
            data={
                "user": self.user.id,
                "receipt": self.receipt1.id,
                "category_id": self.category1.id,
                "name": "potato",
                "price": 1.0,
                "important_dates": "1990-12-12",
            }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(Item.objects.filter(name="potato").exists())

        self.assertEqual(Item.objects.count(), original_item_count + 1)

    def test_item_details(self):
        # This test checks if the specific item is returned, it does this by checking if
        # receipt_id, price, name and important_dates match the database

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get(reverse('item_details', kwargs={'item_id': Item.objects.get(id=1).id}),
                                   format='multipart')
        item = Item.objects.get(id=1)
        self.assertEquals(response.data[0]['receipt'], item.receipt.id)
        self.assertEquals(response.data[0]['price'], str(item.price))
        self.assertEquals(response.data[0]['name'], item.name)
        self.assertEquals(response.data[0]['important_dates'], str(item.important_dates))

    def test_delete_item(self):
        # This test checks if the item is deleted and if the list of items is decreased
        item_id = 1
        delete_item_url = reverse('delete_item', kwargs={'item_id': item_id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_item_count = Item.objects.count()

        response = self.client.delete(delete_item_url, format='json')

        items = Item.objects.all()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for item in items:
            self.assertNotEqual(item.id, item_id)

        self.assertEqual(Item.objects.count(), original_item_count - 1)


class PaginationReceiptsAPITest(APITestCase):
    '''Test Cases for dividing the receipts of a user into pages'''

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

        self.category1 = Category.objects.create(
            user=self.user,
            category_name="clothes",
            category_toggle_star=False,
            parent_category_id=None
        )

        # Create random number of receipts from certain range for this user.
        for i in range(randint(0, 100)):
            Item.objects.create(
                user=self.user,
                receipt=Receipts.objects.get(user=self.user),
                category_id=self.category1,
                name='poutine',
                price=59.99,
                important_dates="2022-10-09"
            )

        # Get the size of the reciepts create for this user
        self.item_size = len(Item.objects.filter(user=self.user))

    def test_pagination_successful(self):
        # Calculates the number of pages. The num of pages wii return different results if the
        # number of recipts is not perfectly divisible by the page size.
        if (self.item_size % 10 == 0):
            num_of_pages = self.item_size // 10
        else:
            num_of_pages = self.item_size // 10 + 1

        for i in range(1, num_of_pages + 1):
            url_paged_items = reverse('list_paged_items', kwargs={'pageNumber': i, 'pageSize': 10})

            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

            response = self.client.get(
                url_paged_items,
                format='json'
            )

            if i == num_of_pages:
                # The last page will require a different check, it can return from 1 to 10 receipts
                self.assertTrue(len(response.data['page_list']) <= 10)
            else:
                self.assertEqual(len(response.data['page_list']), 10)

            self.assertEqual(response.data['description'], f'<Page {i} of {num_of_pages}>')

    def test_pagination_page_zero_error(self):
        url_paged_items = reverse('list_paged_items', kwargs={'pageNumber': 0, 'pageSize': 10})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_items,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) == 0)
        self.assertEqual(response.data['description'], 'Invalid Page Number')

    def test_pagination_over_page_size_error(self):
        url_paged_items = reverse('list_paged_items', kwargs={'pageNumber': self.item_size // 10 + 2, 'pageSize': 10})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_items,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) == 0)
        self.assertEqual(response.data['description'], 'Invalid Page Number')

    def test_pagination_zero_page_size_error(self):
        url_paged_items = reverse('list_paged_items', kwargs={'pageNumber': 1, 'pageSize': 0})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_items,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) <= 10)
        if (self.item_size % 10 == 0):
            self.assertEqual(response.data['description'], f'<Page {1} of {self.item_size // 10}>')
        else:
            self.assertEqual(response.data['description'], f'<Page {1} of {self.item_size // 10 + 1}>')

    def test_pagination_invalid_type_string(self):
        url_paged_items = reverse('list_paged_items', kwargs={'pageNumber': 'test', 'pageSize': 'test'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_items,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) == 0)
        self.assertEqual(response.data['description'], 'Invalid Page Number')


class TestItemsFilteringOrderingSearching(APITestCase):
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

        self.receipt1 = Receipts.objects.create(
            user=self.user,
            receipt_image=get_test_image_file(),
            merchant=Merchant.objects.create(name='starbucks'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            scan_date=datetime.datetime.strptime("2022-10-30", "%Y-%m-%d").date(),
            coupon=1,
            currency="CAD"
        )

        self.receipt2 = Receipts.objects.create(
            user=self.user,
            receipt_image=get_test_image_file(),
            merchant=Merchant.objects.create(name='starbucks'),
            location='456 Testing Street T1E 5T5',
            total=10,
            tax=10,
            tip=10,
            scan_date=datetime.datetime.strptime("2022-10-20", "%Y-%m-%d").date(),
            coupon=1,
            currency="USD"
        )

        self.category1 = Category.objects.create(
            user=self.user,
            category_name="clothes",
            category_toggle_star=False,
            parent_category_id=None
        )

        Item.objects.create(
            user=self.user,
            receipt=self.receipt1,
            name='coffee',
            category_id=self.category1,
            price=10.15,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            user=self.user,
            receipt=self.receipt1,
            name='coffee',
            category_id=self.category1,
            price=10.15,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            user=self.user,
            receipt=self.receipt2,
            name='poutine',
            category_id=self.category1,
            price=59.99,
            important_dates="2022-10-09"
        )

        Item.objects.create(
            user=self.user,
            receipt=self.receipt2,
            name='mateo',
            category_id=self.category1,
            price=12.99,
            important_dates="2022-10-12"
        )

    '''
    TODO: un-pass when search is fixed'''

    def test_search(self):
        pass
        # items_url = reverse('list_paged_items', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?search=coffee'
        # self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        # response = self.client.get(items_url, format='json')
        #
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        #
        # # ensure only 2 items are returned
        # self.assertEqual(len(response.data['page_list']), 2)

    def test_ordering(self):
        items_url = reverse('list_paged_items', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?ordering=-price'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(items_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # the response return items in descending order of price, therefore the previous price field should be
        # greater than or equal to the current price field
        for i in range(len(response.data['page_list'])):
            if i > 0:
                previous_price = response.data['page_list'][i - 1]['price']
            else:
                previous_price = response.data['page_list'][i]['price']
            self.assertTrue(previous_price >= response.data['page_list'][i]['price'])

    def test_filtering(self):
        items_url = reverse('list_paged_items', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?name=poutine'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(items_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only one item contained the name poutine
        self.assertEqual(len(response.data['page_list']), 1)

    def test_start_date_filtering(self):
        items_url = reverse('list_paged_items', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?start_date=2022-10-30'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(items_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # two items were contained in a receipt with a scan_date on or after 2022-10-30
        self.assertEqual(len(response.data['page_list']), 2)

    def test_min_price_filtering(self):
        items_url = reverse('list_paged_items', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?min_price=12'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(items_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # two items contained prices >=12
        self.assertEqual(len(response.data['page_list']), 2)

class CategoryCostsAPITest(APITransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(
            username='therock123@gmail.com',
            email='therock123@gmail.com',
            first_name='The',
            last_name='Rock',
            password='wrestlingrules123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            telephone_number="+1-613-555-1234"
        )
        self.data = {
            'username': 'therock123@gmail.com',
            'password': 'wrestlingrules123'
        }

        self.token = BearerToken.objects.create(user=self.user)

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

        self.category1 = Category.objects.create(
            user=self.user,
            category_name="clothes",
            category_toggle_star=False,
            parent_category_id=None
        )

        self.shirt = Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='shirt',
            category_id=self.category1,
            price=10.15,
            important_dates="2022-10-09"
        )

        self.category2 = Category.objects.create(
            user=self.user,
            category_name="drinks",
            category_toggle_star=False,
            parent_category_id=None
        )

        self.coffee = Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='coffee',
            category_id=self.category2,
            price=10.15,
            important_dates="2022-10-09"
        )

        self.tea = Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='tea',
            category_id=self.category2,
            price=10.15,
            important_dates="2022-10-09"
        )

    def test_get_category_costs(self):


        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(reverse('get_category_costs'), format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

        # Assert the prices
        self.assertEqual(float(response.data['Costs'][0]['category_cost']), self.shirt.price)
        self.assertEqual(float(response.data['Costs'][1]['category_cost']),
                         self.coffee.price + self.tea.price)
