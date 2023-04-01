import os

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from category.models import Category
from item.models import Item
from merchant.models import Merchant
from receipts.models import Receipts
from users.authentication import BearerToken
from users.models import UserProfile


class CategoryAPITestCase(APITestCase):
    def setUp(self):
        """
        Set up the values in database for testing Category API
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
            receipt_image=os.path.join('receipt_image_for_tests.png'),
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
            parent_category_id=Category.objects.get(category_name='Food').pk,
            icon=''
        )

        self.sub_category_uber = Category.objects.create(
            category_name='Uber',
            category_toggle_star=False,
            user=self.user,
            parent_category_id=Category.objects.get(category_name='Taxi').pk,
            icon=''
        )

        self.sub_category_meats = Category.objects.create(
            category_name='Meats',
            category_toggle_star=False,
            user=self.user,
            parent_category_id=Category.objects.get(category_name='Food').pk,
            icon=''
        )

        self.sub_category_list_food = [self.sub_category_fruit, self.sub_category_meats]
        self.sub_category_list_taxi = [self.sub_category_uber]
        self.sub_category_list = [self.sub_category_list_food, self.sub_category_list_taxi]

        # Create the Item for testing which is in a particular subcategory
        self.fruit_item = Item.objects.create(
            name='Fruit Item test',
            price=5.99,
            receipt_id=Receipts.objects.get(user=self.user).pk,
            category_id=Category.objects.get(category_name='Fruits'),
            user=self.user
        )

        self.taxi_item = Item.objects.create(
            name='Taxi Item test',
            price=10,
            receipt_id=Receipts.objects.get(user=self.user).pk,
            category_id=Category.objects.get(category_name='Taxi'),
            user=self.user
        )

        self.taxi_item2 = Item.objects.create(
            name='Taxi2 Item test',
            price=15,
            receipt_id=Receipts.objects.get(user=self.user).pk,
            category_id=Category.objects.get(category_name='Taxi'),
            user=self.user
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
                'parent_category_id': 16,
                'icon': ''
            },
            format='json'
        )

        # Get the value in the Category table
        new_sub_category = Category.objects.get(category_name='Veggies')

        # Assert the Response
        self.assertEqual(response.data['category_name'], new_sub_category.category_name)
        self.assertEqual(response.data['category_toggle_star'], new_sub_category.category_toggle_star)
        self.assertEqual(response.data['parent_category_id'], new_sub_category.parent_category_id)
        self.assertEqual(response.data['icon'], new_sub_category.icon)
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
        Test Case for deleting a sub category. The Fruits category should not exist anymore in the Category table.
        """
        # Delete the item for this test case so that there is no item stored under the Fruits subcategory
        Item.objects.get(name='Fruit Item test').delete()

        url_delete_sub_category = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Fruits'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.delete(
            url_delete_sub_category,
            format='json'
        )

        # Assert that the correct message is returned
        self.assertEqual(response.data['Description'], 'SubCategory successfully deleted')

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

        url_delete_sub_category = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Gibberish'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.delete(
            url_delete_sub_category,
            format='json'
        )

        self.assertEqual(response.data['Description'], 'This sub category does not exist')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

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
        self.assertEqual(response.data['Description'], 'Updated Successfully')

        # Assert the status code
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_toggle_category_star_invalid_category_name(self):
        """
        Test Case for toggling a category star when inputting and invalid category name
        """
        url_toggle_category_star = reverse('delete_and_toggle_category', kwargs={'categoryName': 'Gibberish'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.put(
            url_toggle_category_star,
            format='json'
        )

        # Assert that this category does not exist in Category model
        self.assertFalse(Category.objects.filter(category_name='Gibberish').exists())

        # Assert the message
        self.assertEqual(response.data['Description'], 'Category does not exist')

        # Assert the status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_category_costs(self):

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(reverse('get_category_costs'))

        self.assertEqual(response.status_code, HTTP_200_OK)

        # Assert the prices
        self.assertEqual(float(response.data['Costs'][0]['category_cost']), self.fruit_item.price)
        self.assertEqual(float(response.data['Costs'][1]['category_cost']),
                         self.taxi_item.price + self.taxi_item2.price)

    def test_edit_category(self):
        """
        Test Case for adding a new subcategory, adding a category is also possible but would be redundant to do in this test case
        """
        url_edit_category = reverse('edit_category', kwargs={'categoryName': 'food'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.put(
            url_edit_category,
            data={
                'category_name': 'edited food'
            },
            format='json'
        )

        # Assert the status code
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Get the value of category using the new name in the Category table
        edited_category = Category.objects.filter(category_name='edited food')

        # Assert there is only 1 category with the new edited name
        self.assertEquals(len(edited_category), 1)
        self.assertTrue(edited_category)

        # Get the value of category using the old name in the Category table
        old_category = Category.objects.filter(category_name='food')

        # Assert there is no category with the old name
        self.assertEquals(len(old_category), 0)
        self.assertFalse(old_category)
