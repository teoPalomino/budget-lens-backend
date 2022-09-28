from django.test import TestCase


# A Test example to see if the "python manage.py test" command works when ran in the GitHub actions workflow
class Test(TestCase):
    def test_example(self):
        self.assertEqual("test1", "test1")
