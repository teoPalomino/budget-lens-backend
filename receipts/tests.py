import datetime
import os
import shutil
import tempfile
import time
from math import trunc

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.test import APITestCase

from receipts.models import Receipts
from users.models import UserProfile


# This function is used when I want to directly create/add a new scanned receipt in the database
def get_test_image_file():
    receipt_image_file = tempfile.NamedTemporaryFile(suffix='.png')
    return ImageFile(receipt_image_file, name=receipt_image_file.name)


# I use this function to create a test image that is used when I try
# to send a post request to the API client in order to create/add a new scanned receipt in the database
def create_image():
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        image = Image.new('RGB', (200, 200), 'white')
        image.save(f, 'PNG')
    return open(f.name, mode='rb')


# Here, I am setting the settings.RECEIPT_IMAGES_ROOT, which is the one leading to the "receipt_images" folder,
# to a temporary directory in memory used for the tests below
RECEIPT_IMAGES_ROOT = tempfile.mkdtemp()
settings.RECEIPT_IMAGES_ROOT = RECEIPT_IMAGES_ROOT


class AddReceiptsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johncena123@gmail.com',
            email='johncena123@gmail.com',
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
            email='johndoe123@gmail.com',
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
        self.image = create_image()

    # I have to use the "tearDown" method to delete the temporary directory in memory and make sure the
    # added/created scanned test receipts don't stay locally in the "receipt_images" folder
    def tearDown(self):
        shutil.rmtree(RECEIPT_IMAGES_ROOT, ignore_errors=True)
        shutil.rmtree(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}'), ignore_errors=True)
        shutil.rmtree(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.new_user.id}'), ignore_errors=True)
        super().tearDown()

    def test_create_user_id_sub_folder(self):
        # I should expect the "user_id" sub-folder to not exist in the "receipt_images" folder at first since
        # no receipt has been added/created yet
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # I then create a new receipt and add it to the database
        receipt = Receipts.objects.create(user=self.user, receipt_image=get_test_image_file())

        # Now, I should expect the "user_id" sub-folder to exist in the "receipt_images" folder since a receipt has been added/created
        self.assertTrue(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # I check that the user id of the created/added receipt in the database I just created is the same as the user id of the user who created/added it
        self.assertEqual(receipt.user_id, self.user.id)

        # I check the created/added receipt's datetime scan date in the database is the same as the Unix timestamp equivalent used to rename the receipt's image file
        self.assertEqual(receipt.scan_date.replace(microsecond=0), make_aware(datetime.datetime.fromtimestamp(time.mktime(receipt.scan_date.timetuple()))).replace(tzinfo=datetime.timezone.utc))

        # I check to make sure the receipt's image URL directory/path saved in the database is the same as the one I expect it to be, given the user id as its "user_id" sub-folder and the Unix timestamp equivalent used to rename the image file itself
        self.assertEqual(receipt.receipt_image, os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}', f'{trunc(time.mktime(receipt.scan_date.timetuple()))}.png'))

    def test_user_id_sub_folder_exists(self):
        shutil.rmtree(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}'), ignore_errors=True)
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # Here, a similar thing happens compared to the previous test, except that I am now checking what happens
        # when a new receipt is added by the same user: I should expect the new receipt to be added to the same "user_id" sub-folder
        receipt1 = Receipts.objects.create(user=self.user, receipt_image=get_test_image_file())
        receipt2 = Receipts.objects.create(user=self.user, receipt_image=get_test_image_file())

        self.assertEqual(receipt1.user_id, receipt2.user.id)
        self.assertTrue(os.path.join(settings.RECEIPT_IMAGES_URL, f'{receipt1.user.id}'), os.path.join(settings.RECEIPT_IMAGES_URL, f'{receipt2.user.id}'))
        self.assertNotEqual(receipt1.receipt_image.name.split('/')[2], receipt2.receipt_image.name.split('/')[2])

        # The following/rest of the code below in this test is used to check what happens if a new user tries to add a new receipt of their own:
        # I should expect the new receipt to be added to a new "user_id" sub-folder that corresponds to the new user's id, therefore the path/directory
        # of the new receipt's image URL saved in the database should be different from the one of the previous receipt's image URL saved in the database
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.new_user.id}')))

        receipt3 = Receipts.objects.create(user=self.new_user, receipt_image=get_test_image_file())

        self.assertTrue(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))
        self.assertEqual(receipt3.user_id, self.new_user.id)
        self.assertEqual(receipt3.receipt_image, os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.new_user.id}', f'{trunc(time.mktime(receipt3.scan_date.timetuple()))}.png'))

    def test_add_receipt_images_using_post_request(self):
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # Here, I am testing the API client for the case where a user tries to add a new receipt using a POST request
        # which is the normal way/behaviour in the future for a user to be able to add/create new receipts.
        # I am also making of the "force_authenticate" method to authenticate the user before making the POST request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        # (See the "Given" part of the "Given, When, Then" test design pattern in each of the two acceptance criteria scenarios for this user story (BUD-4) on the Jira Board)
        self.client.force_authenticate(user=self.user)
        self.response = self.client.post(
            reverse('add_receipts'),
            data={'receipt_image': self.image},
            format='multipart'
        )

        # Through the post request, I should expect the path/directory of the new added/created receipt to also be automatically saved in the database under the "receipt_images" folder
        self.assertTrue(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))
        self.assertEqual(self.response.data['receipt image URL links'][0]['receipt_image'].split('/')[2], str(self.user.id))
        self.assertEqual(self.response.data['receipt image URL links'][0]['receipt_image'].split('/')[3].strip('.png'), Receipts.objects.get(user=self.user).receipt_image.name.split('/')[2].strip('.png'))
        self.assertEqual(self.response.data['receipt image URL links'][0]['receipt_image'].strip('/'), os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}', f'{self.response.data["receipt image URL links"][0]["receipt_image"].split("/")[3]}'))

        # Asserts a good/successful status message
        self.assertEqual(self.response.data['status'], 'success')
        self.assertEquals(self.response.status_code, status.HTTP_200_OK)
