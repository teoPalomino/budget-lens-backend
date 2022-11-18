from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from category.models import Category
from item.models import Item
from merchant.models import Merchant
from receipts.models import Receipts
from receipts.tests import get_test_image_file
from users.authentication import BearerToken
from users.models import UserProfile


class CategoryAPITestCase(APITestCase):
    def setUp(self):
        """
        SetUp the values in database for testing Category API
        """
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

        # Create the Category and Subcategory for testing
        # Create Categories
        self.category_food = Category.objects.create(
            category_name='Food',
            category_toggle_star=False,
            user=self.user
        )

        self.category_taxi = Category.objects.create(
            category_name='Taxi',
            category_toggle_star=False,
            user=self.user,
        )

        self.category_list = [self.category_food, self.category_taxi]

        # Create SubCategories
        self.sub_category_fruit = Category.objects.create(
            category_name='Fruits',
            category_toggle_star=False,
            user=self.user,
            parent_category_id=Category.objects.get(category_name='Food').pk
        )

        self.sub_category_uber = Category.objects.create(
            category_name='Uber',
            category_toggle_star=False,
            user=self.user,
            parent_category_id=Category.objects.get(category_name='Taxi').pk
        )

        self.sub_category_meats = Category.objects.create(
            category_name='Meats',
            category_toggle_star=False,
            user=self.user,
            parent_category_id=Category.objects.get(category_name='Food').pk
        )

        self.sub_category_list_food = [self.sub_category_fruit, self.sub_category_meats]
        self.sub_category_list_taxi = [self.sub_category_uber]
        self.sub_category_list = [self.sub_category_list_food, self.sub_category_list_taxi]

        # Create the Item for testing which is in a particular subcategory
        Item.objects.create(
            name='Item test',
            price=5.99,
            receipt_id=Receipts.objects.get(user=self.user),
            category_id=Category.objects.get(category_name='Fruits')
        )

    def test_add_category(self):
        """
        Test Case for adding a new subcategory, adding a category is also possible but would be redundant to do in this test case
        """
        url_add_category = reverse('add_and_list_category')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.post(
            url_add_category,
            data={
                'category_name': 'Veggies',
                'category_toggle_star': False,
                'parent_category_id': 1
            },
            format='json'
        )

        # Get the value in the Category table
        new_sub_category = Category.objects.get(category_name='Veggies')

        # Assert the Response
        self.assertEqual(response.data['category_name'], new_sub_category.category_name)
        self.assertEqual(response.data['category_toggle_star'], new_sub_category.category_toggle_star)
        self.assertEqual(response.data['parent_category_id'], new_sub_category.parent_category_id)
        # Make sure that the parent_category_id is of reference to the actual parent_category (Food is this test case)
        self.assertEqual(response.data['parent_category_id'], self.category_food.pk)

        # Assert the status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_sub_category_when_item_is_in_sub_category(self):
        """
        Test Case for deleting a sub category when an item is already stored using that subcategory. The sub category should not be deleted.
        """
        url_delete_sub_category = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Fruits'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.delete(
            url_delete_sub_category,
            format='json'
        )

        self.assertEqual(response.data['Description'], 'Cannot delete SubCategory, items exists in this subcategory')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_sub_category_successful(self):
        """
        Test Case for deleting a sub category. The Fruits category should not exists anymore in the Category table"
        """
        # Delete the item for this test case so that there is no item stored under the Fruits subcategory
        Item.objects.get(name='Item test').delete()

        url_delete_sub_category = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Fruits'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.delete(
            url_delete_sub_category,
            format='json'
        )

        # Assert that the correct message is returned
        self.assertEqual(response.data['Description'], 'SubCategory succesfully deleted')

        # Assert that the Fruits subcategory does not exist
        self.assertFalse(Category.objects.filter(category_name='Fruits').exists())

        # Assert the status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_parent_category(self):
        """
        Test Case for deleting a parent category. the Food category should not be deleted since it is a parent category
        """

        url_delete_sub_category = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Food'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.delete(
            url_delete_sub_category,
            format='json'
        )

        self.assertEqual(response.data['Description'], 'This is a parent Category, it cannot be deleted')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_non_existing_category(self):
        """
        Test Case for deleting a category that doesn't exist.
        """

        url_delete_sub_category = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Giberish'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.delete(
            url_delete_sub_category,
            format='json'
        )

        self.assertEqual(response.data['Description'], 'This sub category does not exist')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_category_list(self):
        """
        Test Case for getting a list of categories
        """
        url_list_category = reverse('add_and_list_category')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_list_category,
            format='json'
        )

        # Go through every category and sub category nested in each category and assert each of the fields
        for count1, category in enumerate(response.data):
            self.assertEqual(category['category_name'], self.category_list[count1].category_name)
            self.assertEqual(category['category_toggle_star'], self.category_list[count1].category_toggle_star)
            self.assertEqual(category['parent_category_id'], self.category_list[count1].parent_category_id)

            for count2, sub_category in enumerate(category['sub_category_list']):
                self.assertEqual(sub_category['category_name'], self.sub_category_list[count1][count2].category_name)
                self.assertEqual(sub_category['category_toggle_star'], self.sub_category_list[count1][count2].category_toggle_star)

        # Assert the status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_toggle_category_star(self):
        """
        Test Case for toggling a category star
        """
        url_toggle_category_star = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Food'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.put(
            url_toggle_category_star,
            format='json'
        )

        # Assert that the star was changed to true (initially false)
        self.assertTrue(Category.objects.get(category_name='Food').category_toggle_star)

        # Assert the message
        self.assertEqual(response.data['Description'], 'Updated Succesfully')

        # Assert the status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_toggle_category_star_invalid_category_name(self):
        """
        Test Case for toggling a category star when inputing and invalid category name
        """
        url_toggle_category_star = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Giborish'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.put(
            url_toggle_category_star,
            format='json'
        )

        # Assert that this category does not exist in Category model
        self.assertFalse(Category.objects.filter(category_name='Giborish').exists())

        # Assert the message
        self.assertEqual(response.data['Description'], 'Category does not exist')

        # Assert the status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)



"""
    def test_get_category_costs(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(reverse('get_category_costs'))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, {'food': 55, 'car': 20200})"""
