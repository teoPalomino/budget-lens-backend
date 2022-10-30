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


# This function is used when I want to directly create/add a new scanned receipt in the database
def get_test_image_file():
    receipt_image_file = tempfile.NamedTemporaryFile(suffix='.png')
    return ImageFile(receipt_image_file, name=receipt_image_file.name)


# I use this function to create a test image with a given image file type/extension that is used when I try
# to send a post request to the API client in order to create/add a new scanned receipt in the database
def create_image(image_file_type):
    with tempfile.NamedTemporaryFile(suffix=image_file_type, delete=False) as f:
        image = Image.new('RGB', (200, 200), 'white')
        image.save(f, 'PNG')
    return open(f.name, mode='rb')


class AddReceiptsAPITest(APITransactionTestCase):
    # this makes sure that the database ids reset to 1 for every test (when dealing with fetching receipts
    # ids from the database) which is especially important for the tests:
    # test_add_receipt_images_using_post_request_from_Receipts_API_View
    # test_get_list_of_receipt_images_using_get_request_from_Receipts_API_View
    # test_get_specific_receipt_image_with_receipt_id_using_get_request_from_Detail_Receipts_API_View
    # test_update_specific_receipt_image_with_receipt_id_using_put_request_from_Detail_Receipts_API_View
    # test_update_specific_receipt_image_with_receipt_id_using_patch_request_from_Detail_Receipts_API_View
    # test_delete_specific_receipt_image_with_receipt_id_using_delete_request_from_Detail_Receipts_API_View
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

    # I have to use the "tearDown" method to make sure the added/created scanned
    # test receipts don't stay locally in the "receipt_images" folder
    def tearDown(self):
        shutil.rmtree(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}'), ignore_errors=True)
        shutil.rmtree(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.new_user.id}'), ignore_errors=True)
        super().tearDown()

    def test_create_user_id_sub_folder(self):
        # I should expect the "user_id" sub-folder to not exist in the "receipt_images" folder at first since
        # no receipt has been added/created yet
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # I then create a new receipt and add it to the database
        receipt = Receipts.objects.create(
            user=self.user, receipt_image=get_test_image_file(),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4
        )

        # Now, I should expect the "user_id" sub-folder to exist in the "receipt_images" folder since a receipt has been added/created
        self.assertTrue(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # I check that the user id of the created/added receipt in the database I just created is the same as the user id of the user who created/added it
        self.assertEqual(
            receipt.user_id,
            self.user.id
        )

        # I check the created/added receipt's datetime scan date in the database is the same as the Unix timestamp equivalent used to rename the receipt's image file
        self.assertEqual(
            receipt.scan_date.replace(microsecond=0),
            make_aware(datetime.datetime.fromtimestamp(time.mktime(receipt.scan_date.timetuple()))).replace(tzinfo=datetime.timezone.utc)
        )

        # I check to make sure the receipt's image URL directory/path saved in the database is the same as the one I expect it
        # to be,given the user id as its "user_id" sub-folder and the Unix timestamp equivalent used to rename the image file itself
        self.assertEqual(
            receipt.receipt_image,
            os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}', f'{trunc(time.mktime(receipt.scan_date.timetuple()))}.png').replace('\\', '/')
        )

    def test_user_id_sub_folder_exists(self):
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # Here, a similar thing happens compared to the previous test, except that I am now checking what happens
        # when a new receipt is added by the same user: I should expect the new receipt to be added to the same "user_id" sub-folder
        receipt1 = Receipts.objects.create(
            user=self.user,
            receipt_image=get_test_image_file(),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4
        )
        receipt2 = Receipts.objects.create(
            user=self.user,
            receipt_image=get_test_image_file(),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4
        )

        self.assertEqual(
            receipt1.user_id,
            receipt2.user.id
        )
        self.assertTrue(os.path.join(settings.RECEIPT_IMAGES_URL, f'{receipt1.user.id}'), os.path.join(settings.RECEIPT_IMAGES_URL, f'{receipt2.user.id}'))
        self.assertNotEqual(
            receipt1.receipt_image.name.split('/')[2],
            receipt2.receipt_image.name.split('/')[2]
        )

        # The following/rest of the code below in this test is used to check what happens if a new user tries to add a new receipt of their own:
        # I should expect the new receipt to be added to a new "user_id" sub-folder that corresponds to the new user's id, therefore the path/directory
        # of the new receipt's image URL saved in the database should be different from the one of the previous receipt's image URL saved in the database
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.new_user.id}')))

        receipt3 = Receipts.objects.create(
            user=self.new_user,
            receipt_image=get_test_image_file(),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4
        )

        self.assertTrue(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))
        self.assertEqual(
            receipt3.user_id,
            self.new_user.id
        )
        self.assertEqual(
            receipt3.receipt_image,
            os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.new_user.id}', f'{trunc(time.mktime(receipt3.scan_date.timetuple()))}.png').replace('\\', '/')
        )

    def test_add_null_receipt_images_using_post_request_from_Receipts_API_View(self):
        shutil.rmtree(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}'), ignore_errors=True)
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # Here, I am testing the API client for the case where a user tries to add a null receipt (or no receipt at all basically)
        # using a POST request. I am also making use of the "force_authenticate" method to authenticate the user
        # before making the POST request since I don't need to "properly" authenticate the user before doing so as this test
        # is not relevant to that behaviour/functionality
        self.client.force_authenticate(user=self.user)
        self.response = self.client.post(
            reverse('list_create_receipts'),
            format='multipart'
        )

        # Here, I should expect the "user_id" sub-folder to still not exist in the "receipt_images" folder since
        # no receipt has been passed to the API client using the POST request for it to add it/create it and save it
        # in the database under the "receipt_images" folder
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # A response error detail should be raised/returned to the user here since no receipt has been passed to the API client using the POST request
        self.assertEqual(self.response.data['receipt_image'][0], 'No file was submitted.')

        # Asserts a Client Error 4XX BAD REQUEST status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_add_receipt_images_using_post_request_from_Receipts_API_View(self):
        self.assertFalse(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))

        # Here, I am testing the API client for the case where a user tries to add a new receipt using a POST request
        # which is the normal way/behaviour in the future for a user to be able to add/create new receipts.
        # I am also making use of the "force_authenticate" method to authenticate the user before making the POST request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        # (See the "Given" part of the "Given, When, Then" test design pattern in each of the two acceptance criteria scenarios for this user story (BUD-4) on the Jira Board)
        self.client.force_authenticate(user=self.user)
        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )

        # Through the post request, I should expect the path/directory of the new added/created receipt to also be automatically saved in the database under the "receipt_images" folder
        self.assertTrue(os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}')))
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[4],
            str(self.user.id)
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[5].strip('.png'),
            Receipts.objects.get(user=self.user).receipt_image.name.split('/')[2].strip('.png')
        )
        self.assertEqual(
            Receipts.objects.get(user=self.user).receipt_image,
            os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}', f'{self.response.data["receipt_image"].split("/")[5]}').replace('\\', '/')
        )

        # Asserts a Successful 2XX CREATED status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_201_CREATED
        )

    def test_get_list_of_receipt_images_using_get_request_from_Receipts_API_View(self):
        # Here, I am testing the API client for the case where a user tries to get a list of all the receipts they have added/created using a GET request
        # which is the normal way/behaviour in the future for a user to be able to get a list of all the receipts they have added/created.
        # I am also making use of the "force_authenticate" method to authenticate the user before making the GET request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        # (See the "Given" part of the "Given, When, Then" test design pattern in each of the two acceptance criteria scenarios for this user story (BUD-4) on the Jira Board)
        self.client.force_authenticate(user=self.user)
        self.response = self.client.get(
            reverse('list_create_receipts')
        )

        # Since no receipts have been added/created by the user yet, I should expect the list of receipts to be empty
        self.assertEqual(self.receipts_from_responses, [])

        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        # I am creating a second image to add to the list of receipts
        self.image = create_image('.jpeg')
        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        # Now, after the user has added/created the new receipts, when I call the GET request, I should expect the list of receipts to contain the newly added receipts
        self.response = self.client.get(
            reverse('list_create_receipts')
        )
        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count()
        )
        self.assertEqual(
            self.response.data[0]['receipt_image'].split('/')[4],
            str(self.user.id)
        )
        self.assertEqual(
            self.response.data[0]['receipt_image'].split('/')[5].strip('.png'),
            Receipts.objects.get(id=1).receipt_image.name.split('/')[2].strip('.png')
        )
        self.assertEqual(
            Receipts.objects.get(id=1).receipt_image,
            os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}', f'{self.response.data[0]["receipt_image"].split("/")[5]}').replace('\\', '/')
        )

        # Asserts a Successful 2XX OK status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_200_OK
        )

    def test_get_specific_receipt_image_with_receipt_id_using_get_request_from_Detail_Receipts_API_View(self):
        # Here, I am testing the API client for the case where a user tries to get a specific receipt they have added/created using a GET request
        # which is the normal way/behaviour in the future for a user to be able to get a specific receipt they have added/created.
        # I am also making use of the "force_authenticate" method to authenticate the user before making the GET request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        self.client.force_authenticate(user=self.user)

        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.image = create_image('.jpeg')
        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count()
        )

        # Now, after the user has added/created the new receipts, when I call the GET request on a specific
        # receipt, I should expect only that newly added specific receipt to be returned
        self.response = self.client.get(
            reverse('detail_receipts', kwargs={'receipt_id': Receipts.objects.get(id=1).id})
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[4],
            str(self.user.id)
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[5].strip('.png'),
            Receipts.objects.get(id=1).receipt_image.name.split('/')[2].strip('.png')
        )
        self.assertEqual(
            Receipts.objects.get(id=1).receipt_image,
            os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}', f'{self.response.data["receipt_image"].split("/")[5]}').replace('\\', '/')
        )

        # Asserts a Successful 2XX OK status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_200_OK
        )

    def test_update_specific_receipt_image_with_receipt_id_using_put_request_from_Detail_Receipts_API_View(self):
        # Here, I am testing the API client for the case where a user tries to update a specific receipt they have already added/created using a PUT request
        # I am also making use of the "force_authenticate" method to authenticate the user before making the PUT request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        self.client.force_authenticate(user=self.user)

        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.image = create_image('.jpeg')
        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count()
        )

        # Here, I am creating a new image to update the receipt with
        self.image = create_image('.jpg')

        # Now, after the user has added/created the new receipts, when I call the PUT request on a specific
        # receipt, I should expect only that newly added specific receipt to be updated
        self.response = self.client.put(
            reverse('detail_receipts', kwargs={'receipt_id': Receipts.objects.get(id=1).id}),
            data={'receipt_image': self.image},
            format='multipart'
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[4],
            str(self.user.id)
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[5].strip('.png'),
            Receipts.objects.get(id=1).receipt_image.name.split('/')[2].strip('.png')
        )
        self.assertEqual(
            Receipts.objects.get(id=1).receipt_image,
            os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}', f'{self.response.data["receipt_image"].split("/")[5]}').replace('\\', '/')
        )

        # Asserts a Successful 2XX OK status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_200_OK
        )

        # Asserts that the old receipt image has indeed been removed from the file system
        # by making sure that the sub-folder that corresponds to the user's receipt images
        # is of the same size as before his/her receipt image was updated using the PUT request
        self.assertEqual(
            len(os.listdir(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}'))),
            Receipts.objects.all().count()
        )

        # Since the PUT request requires the user to send the entire data, I am testing the case where the user
        # does not send the entire data when they are, for example, only trying to update the scan date of an
        # already existing receipt image which should return a 400 Bad Request status message from the API client
        self.response = self.client.put(
            reverse('detail_receipts', kwargs={'receipt_id': Receipts.objects.get(id=1).id}),
            data={'scan_date': '2022-10-14 02:24:08.801455 +00:00'},
            format='multipart'
        )

        # Asserts a Client Error 4XX BAD REQUEST status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_update_specific_receipt_image_with_receipt_id_using_patch_request_from_Detail_Receipts_API_View(self):
        # Here, I am testing the API client for the case where a user tries to update a specific receipt they have already added/created using a PATCH request
        # I am also making use of the "force_authenticate" method to authenticate the user before making the PATCH request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        self.client.force_authenticate(user=self.user)

        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.image = create_image('.jpeg')
        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count()
        )

        # Here, since I am using the PATCH request, I am only sending the data that I want to update and
        # not the entire data which means I am allowed to update the scan date of the receipt image
        # independently without having to send the receipt image, unlike with the PUT request, therefore I
        # should expect a Successful 2XX OK status message from the API client later down below in the code
        self.response = self.client.patch(
            reverse('detail_receipts', kwargs={'receipt_id': Receipts.objects.get(id=1).id}),
            data={'scan_date': '2022-10-14 02:24:08.801455 +00:00'},
            format='multipart'
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[4],
            str(self.user.id)
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[5].strip('.png'),
            Receipts.objects.get(id=1).receipt_image.name.split('/')[2].strip('.png')
        )
        self.assertEqual(
            Receipts.objects.get(id=1).receipt_image,
            os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}', f'{self.response.data["receipt_image"].split("/")[5]}').replace('\\', '/')
        )

        # Asserts a Successful 2XX OK status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_200_OK
        )

        # Asserts that the old receipt image has indeed been removed from the file system
        # by making sure that the sub-folder that corresponds to the user's receipt images
        # is of the same size as before his/her receipt image was updated using the PATCH request
        self.assertEqual(
            len(os.listdir(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}'))),
            Receipts.objects.all().count()
        )

    def test_delete_specific_receipt_image_with_receipt_id_using_delete_request_from_Detail_Receipts_API_View(self):
        # Here, I am testing the API client for the case where a user tries to delete a specific receipt they have already added/created using a DELETE request
        # which is the normal way/behaviour in the future for a user to be able to delete a specific receipt they have added/created.
        # I am also making use of the "force_authenticate" method to authenticate the user before making the DELETE request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        self.client.force_authenticate(user=self.user)

        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.image = create_image('.jpeg')
        self.response = self.client.post(
            reverse('list_create_receipts'),
            data={
                'receipt_image': self.image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count()
        )

        # Now, after the user has added/created the new receipts, when I call the DELETE request on a specific
        # receipt, I should expect only that newly added specific receipt to be deleted and not the other receipts
        self.response = self.client.delete(
            reverse('detail_receipts', kwargs={'receipt_id': Receipts.objects.get(id=1).id}),
            format='multipart'
        )

        # Asserts a Successful 2XX NO CONTENT status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        # Asserts that the specific receipt image has indeed been deleted from the database
        self.assertEqual(
            Receipts.objects.all().count(),
            1
        )

        # Asserts that the specific receipt image has indeed been deleted from the file system
        # by making sure that the sub-folder that corresponds to the user's receipt images
        # is of the same size as before his/her receipt image was deleted using the DELETE request
        self.assertEqual(
            len(os.listdir(os.path.join(settings.RECEIPT_IMAGES_URL, f'{self.user.id}'))),
            Receipts.objects.all().count()
        )


class PaginationReceiptsAPITest(APITestCase):
    '''
    Test Cases for dividing the receipts of a user into pages
    '''

    def setUp(self):
        # Create a user to test with
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

        # Create login token
        self.token = BearerToken.objects.create(user=self.user)

        # Create random number of receipts from certain range for this user.
        for i in range(randint(0, 100)):
            Receipts.objects.create(
                user=self.user,
                receipt_image=get_test_image_file(),
                merchant=Merchant.objects.create(name='Random Merchant'),
                location='123 Testing Street T1E 5T5',
                total=1.1,
                tax=2.2,
                tip=3.3,
                coupon=4
            )

        # Get the size of the reciepts create for this user
        self.receipt_size = len(Receipts.objects.filter(user=self.user))

    def test_pagination_successful(self):
        for i in range(1, self.receipt_size//10 + 2):
            url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': i, 'pageSize': 10})

            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

            response = self.client.get(
                url_paged_receipts,
                format='json'
            )

            if i == self.receipt_size//10 + 1:
                self.assertEqual(len(response.data['page_list']), self.receipt_size % 10)
            else:
                self.assertEqual(len(response.data['page_list']), 10)

            self.assertEqual(response.data['description'], f'<Page {i} of {self.receipt_size//10 + 1}>')

    def test_pagination_page_zero_error(self):
        url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': 0, 'pageSize': 10})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_receipts,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) <= 10)
        if (self.receipt_size % 10 == 0):
            self.assertEqual(response.data['description'], f'<Page {1} of {self.receipt_size//10}>')
        else:
            self.assertEqual(response.data['description'], f'<Page {1} of {self.receipt_size//10 + 1}>')

    def test_pagination_over_page_size_error(self):
        url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': self.receipt_size//10 + 2, 'pageSize': 10})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_receipts,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) <= 10)
        if (self.receipt_size % 10 == 0):
            self.assertEqual(response.data['description'], f'<Page {self.receipt_size//10} of {self.receipt_size//10}>')
        else:
            self.assertEqual(response.data['description'], f'<Page {self.receipt_size//10 + 1} of {self.receipt_size//10 + 1}>')

    def test_pagination_zero_page_size_error(self):
        url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': 1, 'pageSize': 0})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_receipts,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) <= 10)
        if (self.receipt_size % 10 == 0):
            self.assertEqual(response.data['description'], f'<Page {1} of {self.receipt_size//10}>')
        else:
            self.assertEqual(response.data['description'], f'<Page {1} of {self.receipt_size//10 + 1}>')

    def test_pagination_invalid_type_string(self):
        url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': 'test', 'pageSize': 'test'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_receipts,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) <= 10)
        if (self.receipt_size % 10 == 0):
            self.assertEqual(response.data['description'], f'<Page {1} of {self.receipt_size//10}>')
        else:
            self.assertEqual(response.data['description'], f'<Page {1} of {self.receipt_size//10 + 1}>')
