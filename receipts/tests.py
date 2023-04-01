import datetime
import os
from random import randint
import time

from django.contrib.auth.models import User
from users.authentication import BearerToken
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.test import APITransactionTestCase, APITestCase

from receipts.models import Receipts
from users.models import UserProfile
from merchant.models import Merchant


class AddReceiptsAPITest(APITransactionTestCase):
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
            telephone_number="+1-613-555-0187",
            forwardingEmail='momoamineahmadi@gmail.com'
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

        self.receipts_from_responses = []

    def test_create_user_id_sub_folder(self):
        # I create a new receipt and add it to the database
        receipt = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        # I check that the user id of the created/added receipt in the database I just created is the same as the user id of the user who created/added it
        self.assertEqual(
            receipt.user_id,
            self.user.id
        )

        # I check the created/added receipt's datetime scan date in the database is the same as the Unix timestamp equivalent used to rename the receipt's image file
        self.assertEqual(
            receipt.scan_date.replace(microsecond=0),
            make_aware(datetime.datetime.fromtimestamp(time.mktime(receipt.scan_date.timetuple()))).replace(
                tzinfo=datetime.timezone.utc)
        )

    def test_user_id_sub_folder_exists(self):
        # Here, a similar thing happens compared to the previous test, except that I am now checking what happens
        # when a new receipt is added by the same user: I should expect the new receipt to be added to the same "user_id" sub-folder
        receipt1 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )
        receipt2 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests2.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.assertEqual(
            receipt1.user_id,
            receipt2.user.id
        )

        self.assertNotEqual(
            receipt1.receipt_image.name,
            receipt2.receipt_image.name
        )

        # The following/rest of the code below in this test is used to check what happens if a new user tries to add a new receipt of their own:
        receipt3 = Receipts.objects.create(
            user=self.new_user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.assertEqual(
            receipt3.user_id,
            self.new_user.id
        )

    def test_add_null_receipt_images_using_post_request_from_Receipts_API_View(self):
        # Here, I am testing the API client for the case where a user tries to add a null receipt (or no receipt at all basically)
        # using a POST request. I am also making use of the "force_authenticate" method to authenticate the user
        # before making the POST request since I don't need to "properly" authenticate the user before doing so as this test
        # is not relevant to that behaviour/functionality
        self.client.force_authenticate(user=self.user)
        self.response = self.client.post(
            reverse('create_manual_receipts'),
            format='multipart'
        )

    def test_add_receipt_images_using_post_request_from_Receipts_API_View(self):
        # Here, I am testing the API client for the case where a user tries to add a new receipt using a POST request
        # which is the normal way/behaviour in the future for a user to be able to add/create new receipts.
        # I am also making use of the "force_authenticate" method to authenticate the user before making the POST request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        # (See the "Given" part of the "Given, When, Then" test design pattern in each of the two acceptance criteria scenarios for this user story (BUD-4) on the Jira Board)
        self.client.force_authenticate(user=self.user)

        receipt = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )

        # Through the post request, I should expect the path/directory of the new added/created receipt to also be automatically saved in the database under the "receipt_images" folder
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[5],
            str(self.user.id)
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
            reverse('list_paged_receipts', kwargs={'pageNumber': 1, 'pageSize': 10})
        )

        # Since no receipts have been added/created by the user yet, I should expect the list of receipts to be empty
        self.assertEqual(self.receipts_from_responses, [])

        receipt1 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt1.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        # I am creating a second image to add to the list of receipts
        receipt2 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests2.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt2.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        # Now, after the user has added/created the new receipts, when I call the GET request, I should expect the list of receipts to contain the newly added receipts
        self.response = self.client.get(
            reverse('list_paged_receipts', kwargs={'pageNumber': 1, 'pageSize': 10})
        )
        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count() - 2
        )
        self.assertEqual(
            str(self.response.data['page_list'][0]['id']),
            str(self.user.id)
        )
        self.assertEqual(
            self.response.data['page_list'][0]['receipt_image'].split('/')[4],
            Receipts.objects.get(id=1).receipt_image.name
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

        receipt1 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt1.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        receipt2 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt2.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count() - 2
        )

        # Now, after the user has added/created the new receipts, when I call the GET request on a specific
        # receipt, I should expect only that newly added specific receipt to be returned
        self.response = self.client.get(
            reverse('detail_receipts', kwargs={'receipt_id': Receipts.objects.get(id=1).id})
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[4],
            Receipts.objects.get(id=1).receipt_image.name
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

        receipt1 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt1.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        receipt2 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt2.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count() - 2
        )

        # Here, I am creating a new image to update the receipt with
        receipt3 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        # Now, after the user has added/created the new receipts, when I call the PUT request on a specific
        # receipt, I should expect only that newly added specific receipt to be updated
        self.response = self.client.put(
            reverse('detail_receipts', kwargs={'receipt_id': Receipts.objects.get(id=1).id}),
            data={'receipt_image': receipt3.receipt_image},
            format='multipart'
        )
        self.assertEqual(
            self.response.data['receipt_image'].split('/')[5],
            str(self.user.id)
        )

        # Asserts a Successful 2XX OK status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_200_OK
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

        receipt1 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt1.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        receipt2 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt2.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count() - 2
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
            Receipts.objects.get(id=1).receipt_image.name
        )

        # Asserts a Successful 2XX OK status message
        self.assertEquals(
            self.response.status_code,
            status.HTTP_200_OK
        )

    def test_delete_specific_receipt_image_with_receipt_id_using_delete_request_from_Detail_Receipts_API_View(self):
        # Here, I am testing the API client for the case where a user tries to delete a specific receipt they have already added/created using a DELETE request
        # which is the normal way/behaviour in the future for a user to be able to delete a specific receipt they have added/created.
        # I am also making use of the "force_authenticate" method to authenticate the user before making the DELETE request since
        # I don't need to "properly" authenticate the user before doing so as this test is not relevant to that behaviour/functionality
        self.client.force_authenticate(user=self.user)

        receipt1 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt1.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        receipt2 = Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="CAD"
        )

        self.response = self.client.post(
            reverse('create_manual_receipts'),
            data={
                'receipt_image': receipt2.receipt_image,
                'merchant': r'\{"name": Random Merchant\}',
                'location': '123 Testing Street T1E 5T5',
                'total': 1.1,
                'tax': 2.2,
                'tip': 3.3,
                'coupon': 4,
                'currency': "CAD"
            },
            format='multipart'
        )
        self.receipts_from_responses.append(self.response.data)

        self.assertEqual(
            len(self.receipts_from_responses),
            Receipts.objects.all().count() - 2
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
            3
        )

    def test_delete_receipt_from_another_user(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Insert a receipt for another user
        self.other_user_receipt = Receipts.objects.create(
            user=self.new_user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Fancy Merchant'),
            location='555 Concordia Street JD3 5T5',
            total=1.1,
            tax=2.2,
            tip=3.3,
            coupon=4,
            currency="USD"
        )

        # Try to send a delete request for a receipt that is not theirs
        self.delete_response = self.client.delete(
            reverse('detail_receipts', kwargs={'receipt_id': self.other_user_receipt.pk}))

        self.assertEquals(
            self.delete_response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEquals(
            self.delete_response.data['detail'],
            'Not found.'
        )


class PaginationReceiptsAPITest(APITestCase):
    """
    Test Cases for dividing the receipts of a user into pages
    """

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
                receipt_image=os.path.join('receipt_image_for_tests.png'),
                merchant=Merchant.objects.create(name='Random Merchant'),
                location='123 Testing Street T1E 5T5',
                total=1.1,
                tax=2.2,
                tip=3.3,
                coupon=4,
                currency="CAD"
            )

        # Get the size of the receipts create for this user
        self.receipt_size = len(Receipts.objects.filter(user=self.user))

    def test_pagination_successful(self):
        # Calculates the number of pages. The num of pages wii return different results if the
        # number of receipts is not perfectly divisible by the page size.
        if self.receipt_size % 10 == 0:
            num_of_pages = self.receipt_size // 10
        else:
            num_of_pages = self.receipt_size // 10 + 1

        for i in range(1, num_of_pages + 1):
            url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': i, 'pageSize': 10})

            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

            response = self.client.get(
                url_paged_receipts,
                format='json'
            )

            if i == num_of_pages:
                # The last page will require a different check, it can return from 1 to 10 receipts
                self.assertTrue(len(response.data['page_list']) <= 10)
            else:
                self.assertEqual(len(response.data['page_list']), 10)

            self.assertEqual(response.data['description'], f'<Page {i} of {num_of_pages}>')

    def test_pagination_page_zero_error(self):
        url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': 0, 'pageSize': 10})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_receipts,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) == 0)
        self.assertEqual(response.data['description'], 'Invalid Page Number')

    def test_pagination_over_page_size_error(self):
        url_paged_receipts = reverse('list_paged_receipts',
                                     kwargs={'pageNumber': self.receipt_size // 10 + 2, 'pageSize': 10})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_receipts,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) == 0)
        self.assertEqual(response.data['description'], 'Invalid Page Number')

    def test_pagination_zero_page_size_error(self):
        url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': 1, 'pageSize': 0})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_receipts,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) <= 10)
        if self.receipt_size % 10 == 0:
            self.assertEqual(response.data['description'], f'<Page {1} of {self.receipt_size // 10}>')
        else:
            self.assertEqual(response.data['description'], f'<Page {1} of {self.receipt_size // 10 + 1}>')

    def test_pagination_invalid_type_string(self):
        url_paged_receipts = reverse('list_paged_receipts', kwargs={'pageNumber': 'test', 'pageSize': 'test'})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            url_paged_receipts,
            format='json'
        )

        self.assertTrue(len(response.data['page_list']) == 0)
        self.assertEqual(response.data['description'], 'Invalid Page Number')


class TestReceiptsFilteringOrderingSearching(APITestCase):
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
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='starbucks'),
            location='123 Testing Street T1E 5T5',
            total=1,
            tax=1,
            tip=1,
            coupon=1,
            currency="CAD"
        )

        Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=2,
            tax=2,
            tip=2,
            coupon=2,
            currency="CAD"
        )

        Receipts.objects.create(
            user=self.user,
            receipt_image=os.path.join('receipt_image_for_tests.png'),
            merchant=Merchant.objects.create(name='Random Merchant'),
            location='123 Testing Street T1E 5T5',
            total=3,
            tax=3,
            tip=3,
            coupon=3,
            currency="USD"
        )

    def test_search(self):
        receipts_url = reverse('list_paged_receipts', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?search=CAD'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(receipts_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure only 2 receipts are returned
        self.assertEqual(len(response.data['page_list']), 2)

    def test_partial_keyword_search(self):
        receipts_url = reverse('list_paged_receipts', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?search=123'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(receipts_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # should return all 3 receipts because they all contain '123' in their location field
        self.assertEqual(len(response.data['page_list']), 3)

    def test_ordering(self):
        receipts_url = reverse('list_paged_receipts', kwargs={'pageNumber': 1, 'pageSize': 10}) + '?ordering=-total'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(receipts_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # the response return receipts in descending order of total, therefore the previous total field should be
        # greater than or equal to the current total field
        for i in range(len(response.data['page_list'])):
            if i > 0:
                previous_total = response.data['page_list'][i - 1]['total']
            else:
                previous_total = response.data['page_list'][i]['total']
            self.assertTrue(previous_total >= response.data['page_list'][i]['total'])

    def test_filtering(self):
        receipts_url = reverse('list_paged_receipts', kwargs={'pageNumber': 1, 'pageSize': 10}) + "?currency=USD"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(receipts_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only one receipt contained the currency USD
        self.assertEqual(len(response.data['page_list']), 1)
