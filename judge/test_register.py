from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from judge.models import Language


class RegisterWithoutEmailTest(TestCase):
    fixtures = ['language_small.json']

    def test_email_is_optional(self):
        response = self.client.post(reverse('registration_register'), {
            'username': 'no_mail_student',
            'email': '',
            'password1': 'Sx7-unusual-pass',
            'password2': 'Sx7-unusual-pass',
            'timezone': 'Asia/Bishkek',
            'language': Language.objects.first().id,
        })
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None) and
                         response.context['form'].errors)
        user = User.objects.get(username='no_mail_student')
        self.assertEqual(user.email, '')
        self.assertTrue(user.is_active)
