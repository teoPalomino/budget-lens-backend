from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from category.models import Category, SubCategory
from item.models import Item
from merchant.models import Merchant
from receipts.models import Receipts
from receipts.tests import get_test_image_file
from users.authentication import BearerToken
from users.models import UserProfile


class CategoriesAPITESTS(APITestCase):
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


"""        
TODO: fix the test cases when final Category, SubCategory models are created
        and when Items model is added
        Category.objects.create(
            user=self.user,
            category_name='food',
            category_toggle_star=True
        )

        Category.objects.create(
            user=self.user,
            category_name='car',
            category_toggle_star=True
        )

        SubCategory.objects.create(
            sub_category_name='food',
            user=self.user,
            parent_category_id=Category.objects.get(category_name='food')
        )

        SubCategory.objects.create(
            sub_category_name='car',
            user=self.user,
            parent_category_id=Category.objects.get(category_name='car')
        )

        Item.objects.create(
            receipt_id=Receipts.objects.get(user=self.user),
            # tax=15,
            name='poutine',
            price=30,
            sub_category_id=1
            # important_dates="2022-10-09"
        )

        Item.objects.create(
            receipt_id=Receipts.objects.get(user=self.user),
            # tax=5,
            name='shawarma',
            price=25,
            sub_category_id=1
            # important_dates="2022-10-09"
        )

        Item.objects.create(
            receipt_id=Receipts.objects.get(user=self.user),
            # tax=200,
            name='car',
            price=20000,
            category_id=Category.objects.get(category_name='car'),
            sub_category_id=2
            # important_dates="2022-10-09"
        )

    def test_get_category_costs(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(reverse('get_category_costs'))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, {'food': 55, 'car': 20200})"""
