from django.contrib.auth.models import User
from rest_framework import status

from category.models import Category
from rules.models import Rule
from users.authentication import BearerToken
from django.urls import reverse
from rest_framework.test import APITransactionTestCase

from users.models import UserProfile


class TestRules(APITransactionTestCase):
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

        self.token = BearerToken.objects.get(user=self.user)

        self.category1 = Category.objects.create(
            user=self.user,
            category_name="clothes",
            category_toggle_star=False,
            parent_category_id=None
        )

        self.category2 = Category.objects.create(
            user=self.user,
            category_name="not clothes",
            category_toggle_star=False,
            parent_category_id=None
        )

        self.rules1 = Rule.objects.create(
            user=self.user,
            regex="clothes",
            category=self.category1,
            created_at="2020-12-12"
        )

        self.rules2 = Rule.objects.create(
            user=self.user,
            regex="food",
            category=self.category1,
            created_at="2020-12-12"
        )

    def test_create_rule(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_rules_count = Rule.objects.count()

        response = self.client.post(
            reverse('add_rule'),
            data={
                "user": self.user.id,
                "regex": "regex",
                "category": self.category1.id,
                "created_at": "2022-12-12"},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Rule.objects.count(), original_rules_count + 1)

    def test_get_rules(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        response = self.client.get(
            reverse('get_rules')
        )

        rule = Rule.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['regex'], rule.regex)
        self.assertEqual(response.data[0]['category'], rule.category.id)

    def test_delete_rule(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        rule_id = 1
        original_rules_count = Rule.objects.count()

        response = self.client.delete(reverse('delete_rule', kwargs={'rule_id': rule_id}))

        rules = Rule.objects.all()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for rule in rules:
            self.assertNotEqual(rule.id, rule_id)

        self.assertEqual(Rule.objects.count(), original_rules_count - 1)

    def test_edit_rule(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        original_rule = Rule.objects.get(id=1)

        response = self.client.put(
            reverse('rule_details', kwargs={'rule_id': 1}),
            data={
                "regex": "not clothes",
                "category": self.category2.id
            },
            format='json'
        )

        edited_rule = Rule.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(original_rule.user, edited_rule.user)
        self.assertNotEqual(original_rule.regex, edited_rule.regex)
        self.assertNotEqual(original_rule.category, edited_rule.category)
