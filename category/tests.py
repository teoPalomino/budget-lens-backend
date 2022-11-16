# from django.test import TestCase
# from users.models import User, UserProfile
# from users.authentication import BearerToken

# from item.models import Item

# from receipts.models import Receipts
# from receipts.tests import get_test_image_file

# from merchant.models import Merchant

# class CategoryAndSubCategoryTestCase(TestCase):
#     def setUp(self) -> None:
#         """
#         Create a user, user profile, some Items, and some Categories and SubCategories
#         """

#         # Create a user to test with
#         self.user = User.objects.create_user(
#             username='johncena123@gmail.com',
#             email='johncena123@gmail.com',
#             first_name='John',
#             last_name='Cena',
#             password='wrestlingrules123'
#         )
#         self.user_profile = UserProfile.objects.create(
#             user=self.user,
#             telephone_number="+1-613-555-0187"
#         )

#         # Create login token
#         self.token = BearerToken.objects.create(user=self.user)

#         # Create 1 receipt from certain range for this 
#         self.receipt = Receipts.objects.create(
#             user=self.user,
#             receipt_image=get_test_image_file(),
#             merchant=Merchant.objects.create(name='Random Merchant'),
#             location='123 Testing Street T1E 5T5',
#             total=1.1,
#             tax=2.2,
#             tip=3.3,
#             coupon=4,
#             currency="CAD",
#             important_dates="2022-10-09"
#         )

#         # Create an items from certain range for this user.
#         self.item = Item.objects.create(
#             name='TestSandwitch',
#             price=5.99,
#             receipt_id=self.receipt.pk,
#             category_id=,
#             sub_category_id=
#         )


