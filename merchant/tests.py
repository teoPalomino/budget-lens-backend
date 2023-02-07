from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from merchant.models import Merchant
from users.authentication import BearerToken
from users.models import UserProfile


class MerchantTestCase(APITestCase):
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

        self.token = BearerToken.objects.create(user=self.user)

        self.merchant = Merchant.objects.create(
            name='Walmart'
        )

    def test_get_merchant(self):
        """
        Test to get a merchant
        """
        url_get_merchant = reverse('add_and_list_merchant')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_get_merchant,
            format='json'
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['merchants'][0]['name'], 'Walmart')

    def test_add_merchant(self):
        """
        Test to add a merchant
        """
        url_add_merchant = reverse('add_and_list_merchant')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post(
            url_add_merchant,
            data={
                'name': 'Dollarama'
            },
            format='json'
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Dollarama')
        self.assertTrue(Merchant.objects.filter(name='Dollarama').exists())
