from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.contrib.auth.models import User
from django.db import close_old_connections
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from judge.models import Language, Profile
from judge.views.register import CustomRegistrationForm


@override_settings(SECURE_SSL_REDIRECT=False, REGISTRATION_OPEN=True,
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class RegistrationTests(TestCase):
    def setUp(self):
        self.language = Language.get_default_language()
        self.data = {
            'username': 'registration_test_user', 'email': 'registration@example.org',
            'password1': 'Strong-registration-482!', 'password2': 'Strong-registration-482!',
            'timezone': settings.DEFAULT_USER_TIME_ZONE, 'language': self.language.pk,
        }

    def test_login_offers_registration_only_when_open(self):
        response = self.client.get(reverse('auth_login'))
        self.assertContains(response, 'class="button" href="%s"' % reverse('registration_register'))
        with override_settings(REGISTRATION_OPEN=False):
            self.assertNotContains(self.client.get(reverse('auth_login')), 'class="sign-up-link"')
            self.assertRedirects(self.client.get(reverse('registration_register')),
                                 reverse('registration_disallowed'))

    def test_registration_activates_without_sending_mail(self):
        with patch('registration.models.RegistrationProfile.send_activation_email',
                   side_effect=AssertionError('Registration must not send activation email')):
            response = self.client.post(reverse('registration_register'), self.data)
        self.assertRedirects(response, reverse('auth_login'))
        user = User.objects.get(username=self.data['username'])
        self.assertTrue(user.is_active)
        self.assertEqual(user.profile.language, self.language)
        self.assertTrue(self.client.login(username=user.username, password=self.data['password1']))

    def test_email_uniqueness_ignores_case(self):
        User.objects.create_user('existing_user', email='Registration@Example.org')
        form = CustomRegistrationForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_profile_failure_rolls_back_account(self):
        with patch.object(Profile, 'save', side_effect=RuntimeError('Profile save failed')):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse('registration_register'), self.data)
        self.assertFalse(User.objects.filter(username=self.data['username']).exists())

    def test_invalid_preferences_are_visible(self):
        self.data.update(timezone='invalid-zone', language='-1')
        response = self.client.post(reverse('registration_register'), self.data)
        self.assertContains(response, 'invalid-zone')
        self.assertContains(response, 'class="form-field-error"', count=2)

    @override_settings(DEFAULT_USER_LANGUAGE='ABSENT')
    def test_missing_default_language_does_not_break_registration(self):
        self.assertEqual(self.client.get(reverse('registration_register')).status_code, 200)


@override_settings(SECURE_SSL_REDIRECT=False, REGISTRATION_OPEN=True,
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class RegistrationBurstTests(TransactionTestCase):
    def test_parallel_users_can_register_and_login_with_csrf(self):
        language = Language.get_default_language()
        password = 'Strong-registration-482!'

        def register(index):
            close_old_connections()
            try:
                client = Client(enforce_csrf_checks=True)
                response = client.get(reverse('registration_register'))
                if response.status_code != 200:
                    return response.status_code, False
                username = 'burst_test_%02d' % index
                data = {'username': username, 'email': 'burst%02d@example.org' % index,
                        'password1': password, 'password2': password,
                        'timezone': settings.DEFAULT_USER_TIME_ZONE, 'language': language.pk,
                        'csrfmiddlewaretoken': client.cookies['csrftoken'].value}
                response = client.post(reverse('registration_register'), data)
                return response.status_code, client.login(username=username, password=password)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=8) as pool:
            result = list(pool.map(register, range(40)))
        self.assertEqual(result, [(302, True)] * 40)
        self.assertEqual(User.objects.filter(username__startswith='burst_test_').count(), 40)
        self.assertEqual(Profile.objects.filter(user__username__startswith='burst_test_').count(), 40)
