from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from moderation.fields import SerializedObjectField
from tests.models import UserProfile

__author__ = 'sam'


class FieldsTestCase(TestCase):
    fixtures = ['test_users.json', ]

    def test_serialize(self):
        serialized_field = SerializedObjectField()

        profile = UserProfile(description='Profile for new user',
                              url='http://www.yahoo.com',
                              user=User.objects.get(username='user1'))

        profile.save()

        serialized_profile = serialized_field._serialize(profile)

        self.assertIn('"model": "tests.userprofile"', serialized_profile)
        self.assertIn('"fields": {', serialized_profile)
        self.assertIn('"url": "http://www.yahoo.com"', serialized_profile)
        self.assertIn('"user": 2', serialized_profile)
        self.assertIn('"description": "Profile for new user"',
                      serialized_profile)
        self.assertIn('"pk": 1', serialized_profile)

    def test_deserialize(self):
        serialized_profile = '[{"model": "tests.userprofile", "fields": {' \
                             '"url": "http://www.yahoo.com", "user": 2, ' \
                             '"description": "Profile for new user"}, "pk":' \
                             ' 1}]'

        serialized_field = SerializedObjectField()

        profile = serialized_field._deserialize(serialized_profile)

        self.assertIsNotNone(profile)
        self.assertEqual('http://www.yahoo.com', profile.url)
        self.assertEqual(2, profile.user.pk)
        self.assertEqual('Profile for new user', profile.description)
        self.assertEqual(1, profile.pk)

    def test_deserialize_missing_field(self):
        """
            This test is to simulate an old serialization that has been stored
            but the model has been updated since it was created
        """
        # Serialized profile doesn't have a description
        serialized_profile = '[{"model": "tests.userprofile", "fields": {' \
                             '"url": "http://www.yahoo.com", "user": 2 ' \
                             '}, "pk": 1}]'

        serialized_field = SerializedObjectField()

        profile = serialized_field._deserialize(serialized_profile)
        self.assertIsNotNone(profile)
        self.assertEqual('http://www.yahoo.com', profile.url)
        self.assertEqual('', profile.description)
        self.assertEqual(2, profile.user.pk)
        self.assertEqual(1, profile.pk)
