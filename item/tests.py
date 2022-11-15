import datetime
import os
from random import randint
import shutil
import tempfile
import time
from math import trunc

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from users.authentication import BearerToken
from django.core.files.images import ImageFile
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.test import APITransactionTestCase, APITestCase

from receipts.models import Receipts
from users.models import UserProfile
from merchant.models import Merchant

# Create your tests here.
class AddItemssAPITest(APITransactionTestCase):
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
        self.client.post(
            reverse('login_user'),
            data=self.data,
            format='json'
        )
        self.new_user = User.objects.create_user(
            username='johndoe123@gmail.com',
            email='momoamineahmadi@gmail.com',
            first_name='John',
            last_name='Doe',
            password='trollingrules123'
        )
        self.new_user_profile = UserProfile.objects.create(
            user=self.new_user,
            telephone_number="+1-613-420-4200"
        )
        self.new_data = {
            'username': 'johndoe123@gmail.com',
            'password': 'trollingrules123'
        }
        self.client.post(
            reverse('login_user'),
            data=self.new_data,
            format='json'
        )
        self.image = create_image('.png')
        self.receipts_from_responses = []

        def test_add_new_item():
            pass

        def test_get_items():
            pass

        def test_get_items():
            pass