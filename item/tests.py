import datetime
import os
from random import randint
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from item.models import Item

from merchant.models import Merchant
from receipts.models import Receipts
from category.models import Category
from rules.models import Rule
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
            receipt_image=os.path.join('receipt_image_for_tests.png'),
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

        self.category2 = Category.objects.create(
            user=self.user,
            category_name="fun",
            category_toggle_star=False,
            parent_category_id=None
        )

        Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='coffee',
            category_id=self.category1,
            price=10.15
        )

        Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='poutine',
            category_id=self.category1,
            price=59.99
        )

        Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='mateo',
            category_id=self.category1,
            price=12.99
        )

        self.rules1 = Rule.objects.create(
            user=self.user,
            regex="fun",
            category=self.category1,
            created_at="2020-12-12"
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
                "price": 1.0
            }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(Item.objects.filter(name="potato").exists())

        self.assertEqual(Item.objects.count(), original_item_count + 1)

    def test_item_details(self):
        # This test checks if the specific item is returned, it does this by checking if
        # receipt_id, price, and name match the database

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get(reverse('item_details', kwargs={'item_id': Item.objects.get(id=1).id}),
                                   format='multipart')
        item = Item.objects.get(id=1)
        self.assertEquals(response.data[0]['id'], item.id)
        self.assertEquals(response.data[0]['user'], User.objects.get(id=item.user.id).first_name)
        self.assertEquals(response.data[0]['name'], item.name)
        self.assertEquals(response.data[0]['price'], item.price)
        self.assertEquals(response.data[0]['receipt'], item.receipt.id)
        self.assertEquals(response.data[0]['merchant_name'], item.receipt.merchant.name)
        self.assertEquals(response.data[0]['scan_date'], item.receipt.scan_date)
        self.assertEquals(response.data[0]['category_id'], item.category_id.id)
        self.assertEquals(response.data[0]['category_name'], item.category_id.category_name)
        self.assertEquals(response.data[0]['parent_category_id'], item.category_id.parent_category_id)

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

    def test_add_item_with_rules(self):
        # This test checks if a new item and it's name matches the regex of a rule, if it does
        # then the item's category is changed to the rule's category

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_item_count = Item.objects.count()

        response = self.client.post(
            reverse('add_item'),
            data={
                "user": self.user.id,
                "receipt": self.receipt1.id,
                "category_id": self.category1.id,
                "name": "fun",
                "price": 1.0
            }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(Item.objects.filter(name="fun").exists())

        self.assertEqual(Item.objects.count(), original_item_count + 1)

        # note that the item was added its names rules regex category, whereas it was specified to be added to category1
        # which was clothes
        self.assertEqual(Item.objects.get(name="fun").category_id.id, Rule.objects.get(regex="fun").category.id)


class PaginationReceiptsAPITest(APITestCase):
    """Test Cases for dividing the receipts of a user into pages"""

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
            receipt_image=os.path.join('receipt_image_for_tests.png'),
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
                price=59.99
            )

        # Get the size of the receipts create for this user
        self.item_size = len(Item.objects.filter(user=self.user))

    def test_pagination_successful(self):
        # Calculates the number of pages. The num of pages wii return different results if the
        # number of receipts is not perfectly divisible by the page size.
        if self.item_size % 10 == 0:
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
        url_paged_items = reverse('list_paged_items',
                                  kwargs={'pageNumber': self.item_size // 10 + 2, 'pageSize': 10})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_items,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) == 0)
        self.assertEqual(response.data['description'], 'Invalid Page Number')

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
            receipt_image=os.path.join('receipt_image_for_tests.png'),
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
            receipt_image=os.path.join('receipt_image_for_tests.png'),
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
            price=10.15
        )

        Item.objects.create(
            user=self.user,
            receipt=self.receipt1,
            name='coffee',
            category_id=self.category1,
            price=10.15
        )

        Item.objects.create(
            user=self.user,
            receipt=self.receipt2,
            name='poutine',
            category_id=self.category1,
            price=59.99
        )

        Item.objects.create(
            user=self.user,
            receipt=self.receipt2,
            name='mateo',
            category_id=self.category1,
            price=12.99
        )

    '''
    TODO: un-pass when search is fixed'''

    def test_search(self):
        items_url = reverse('list_paged_items', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?search=coffee'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get(items_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure only 2 items are returned
        self.assertEqual(len(response.data['page_list']), 2)

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
            receipt_image=os.path.join('receipt_image_for_tests.png'),
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
            price=10.15
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
            price=10.15
        )

        self.tea = Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='tea',
            category_id=self.category2,
            price=10.15
        )

    def test_get_category_costs(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(reverse('get_category_costs'), format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

        # Assert the prices
        self.assertEqual(float(response.data['Costs'][0]['category_cost']), self.shirt.price)
        self.assertEqual(float(response.data['Costs'][1]['category_cost']),
                         self.coffee.price + self.tea.price)


class ItemFrequencyAPITest(APITransactionTestCase):
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

        self.receipt_starbucks = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='starbucks'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            coupon=1,
            currency="CAD"
        )

        # Update the date to be an old receipt
        if (datetime.date.today().month == 3 and datetime.date.today().day == 29)\
                or (datetime.date.today().month == 3 and datetime.date.today().day == 30)\
                or (datetime.date.today().month == 3 and datetime.date.today().day == 31):
            self.receipt_starbucks.scan_date = self.receipt_starbucks.scan_date.replace(month=2, day=28)
        else:
            self.receipt_starbucks.scan_date = self.receipt_starbucks.scan_date.replace(month=datetime.date.today().month - 1)

        self.receipt_starbucks_newest = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.get(name='starbucks'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            coupon=1,
            currency="CAD"
        )

        self.receipt_walmart = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Walmart'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            coupon=1,
            currency="CAD"
        )
        self.shirt1 = Item.objects.create(
            user=self.user,
            receipt=self.receipt_walmart,
            name='shirt',
            price=10.15
        )

        self.coffee1 = Item.objects.create(
            user=self.user,
            receipt=self.receipt_starbucks,
            name='coffee',
            price=10.15
        )

    def test_get_item_frequency(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(reverse('get_item_frequency_month', kwargs={'item_id': self.shirt1.id}), format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

        # First, assert the case where the frequency of purchase of an item is just 1
        self.assertEqual(response.data[self.shirt1.name]['item_frequency'], 1)

        # Let's assume there were two items with this name under the same receipt, then we expect the frequency of
        # purchase to be incremented by 1 since there are two instances of this item that were bought
        self.shirt2 = Item.objects.create(
            user=self.user,
            receipt=self.receipt_walmart,
            name='shirt',
            price=10.15
        )

        response = self.client.get(reverse('get_item_frequency_month', kwargs={'item_id': self.shirt1.id}), format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data[self.shirt1.name]['item_frequency'], 2)

        # Now, let's assume the case where an item was bought more than once from different receipts: the frequency of
        # purchase should still reflect the number of times that item was bought previously, regardless of the receipt
        self.coffee2 = Item.objects.create(
            user=self.user,
            receipt=self.receipt_starbucks_newest,
            name='coffee',
            price=10.15
        )

        response = self.client.get(reverse('get_item_frequency_month', kwargs={'item_id': self.coffee1.id}), format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertEqual(response.data[self.coffee1.name]['item_frequency'], 2)

        # Now, let's assume the case where an item was bought more than a month ago: the response of the request should
        # return a message saying that the item was not bought in the last month
        self.receipt_starbucks.scan_date = self.receipt_starbucks.scan_date.replace(month=datetime.date.today().month - 2)
        self.receipt_starbucks.save()
        self.receipt_starbucks_newest.scan_date = self.receipt_starbucks_newest.scan_date.replace(month=datetime.date.today().month - 2)
        self.receipt_starbucks_newest.save()

        response = self.client.get(reverse('get_item_frequency_month', kwargs={'item_id': self.coffee1.id}), format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertEqual(list(response.data)[0], "This item was not bought in the last month")

        # Now, let's assume the case where the id of an item does not exist: the response of the request should return an
        # error message saying that the item with that specific id does not exist
        response = self.client.get(reverse('get_item_frequency_month', kwargs={'item_id': 100}), format='json')

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data['Error'], "Item with this id does not exist")


class CategoryCostsFrequencyAPITest(APITransactionTestCase):
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

        self.receipt_starbucks = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='starbucks'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            coupon=1,
            currency="CAD"
        )
        # Update the date to be an old receipt
        self.receipt_starbucks.scan_date = self.receipt_starbucks.scan_date - datetime.timedelta(days=2)

        self.receipt_starbucks_newest = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.get(name='starbucks'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            coupon=1,
            currency="CAD"
        )

        self.receipt_walmart = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Walmart'),
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
            receipt=self.receipt_walmart,
            name='shirt',
            category_id=self.category1,
            price=10.15
        )

        self.category2 = Category.objects.create(
            user=self.user,
            category_name="drinks",
            category_toggle_star=True,
            parent_category_id=None
        )

        self.coffee = Item.objects.create(
            user=self.user,
            receipt=self.receipt_starbucks_newest,
            name='coffee',
            category_id=self.category2,
            price=10.15
        )

        self.tea = Item.objects.create(
            user=self.user,
            receipt=self.receipt_starbucks,
            name='tea',
            category_id=self.category2,
            price=10.15
        )

    def test_get_category_costs_frequency(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(reverse('get_category_costs_frequency_date', kwargs={'days': 1}), format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

        # Assert the drinks prices and frequency of purchasing drinks
        self.assertEqual(float(response.data['drinks']['price']), self.coffee.price + self.tea.price)
        self.assertEqual(response.data['drinks']['category_frequency'], 2)

        # since drinks is a starred category, we should only have the drinks price and frequency
        #  and not the clothes price and frequency. So we assert that the clothes category in None in the response data
        self.assertIsNone(response.data.get('clothes'))
