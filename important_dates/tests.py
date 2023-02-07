from django.contrib.auth.models import User
from rest_framework.status import HTTP_200_OK

from django.urls import reverse
from rest_framework.test import APITransactionTestCase

from category.models import Category
from merchant.models import Merchant
from receipts.models import Receipts
from receipts.tests import get_test_image_file
from users.authentication import BearerToken

from item.models import Item
from important_dates.models import ImportantDates
from users.models import UserProfile


class ImportantDatesTests(APITransactionTestCase):
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

        self.item1 = Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='coffee',
            category_id=self.category1,
            price=10.15
        )

        self.item2 = Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='poutine',
            category_id=self.category1,
            price=59.99
        )

        self.item3 = Item.objects.create(
            user=self.user,
            receipt=Receipts.objects.get(user=self.user),
            name='mateo',
            category_id=self.category1,
            price=12.99
        )

        self.date1 = ImportantDates.objects.create(
            user=self.user,
            item=self.item1,
            date="2020-12-12",
            description="first"
        )

        self.date2 = ImportantDates.objects.create(
            user=self.user,
            item=self.item2,
            date="2023-01-01",
            description="second"
        )

    def test_add_new_important_dates(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_count = ImportantDates.objects.count()

        response = self.client.post(
            reverse('important_dates'),
            data={
                "user": self.user.id,
                "item": self.item1.id,
                "date": "2020-12-12",
                "description": "Christmas"
            }, format='multipart')

        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertTrue(ImportantDates.objects.filter(description="Christmas").exists())

        self.assertEqual(ImportantDates.objects.count(), original_count + 1)

    def test_delete_important_dates(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_count = ImportantDates.objects.count()

        date_id = self.date1.id

        response = self.client.delete(
            reverse('delete_important_dates',
                    kwargs={'important_date_id': date_id}),
            format='multipart')

        self.assertEqual(response.status_code, HTTP_200_OK)

        for date in ImportantDates.objects.all():
            self.assertNotEqual(date.id, date_id)

        self.assertFalse(ImportantDates.objects.filter(description="first").exists())

        self.assertEqual(ImportantDates.objects.count(), original_count - 1)

    def test_get_important_dates(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        count = ImportantDates.objects.count()

        response = self.client.get(
            reverse('important_dates'),
            format='multipart')

        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertEqual(len(response.data), count)

    def test_get_important_dates_by_item(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        count = ImportantDates.objects.filter(item=self.item1).count()

        response = self.client.get(
            reverse('get_important_dates',
                    kwargs={'item_id': self.item1.id}),
            format='multipart')

        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertEqual(len(response.data), count)

        self.assertEqual(response.data[0]['description'], "first")
        self.assertEqual(response.data[0]['item'], self.item1.id)
        self.assertEqual(response.data[0]['date'], "2020-12-12")
