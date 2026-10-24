import json

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from judge.models import TypingResult
from judge.models.tests.util import create_user


class TypingTrainerTest(TestCase):
    def setUp(self):
        cache.clear()
        self.user = create_user(username='typist')
        self.user.set_password('typing-pass-1')
        self.user.save()

    def save(self, **data):
        body = {'mode': 'test', 'layout': 'ru', 'seconds': 60, 'chars': 300, 'errors': 3}
        body.update(data)
        cache.clear()  # one save every few seconds per user
        return self.client.post(reverse('typing_save'), json.dumps(body), content_type='application/json')

    def test_pages_open(self):
        self.assertEqual(self.client.get(reverse('typing')).status_code, 200)
        self.assertEqual(self.client.get(reverse('typing_records')).status_code, 200)

    def test_save_counts_speed_on_the_server(self):
        self.client.login(username='typist', password='typing-pass-1')
        response = self.save(cpm=99999)
        self.assertEqual(response.status_code, 200)
        result = TypingResult.objects.get()
        self.assertEqual(result.cpm, 300)
        self.assertEqual(result.accuracy, 99.0)
        self.assertTrue(response.json()['record'])
        self.assertFalse(self.save(chars=200).json()['record'])

    def test_impossible_results_are_rejected(self):
        self.client.login(username='typist', password='typing-pass-1')
        self.assertEqual(self.save(chars=5000, seconds=60).status_code, 400)   # 5000 chars a minute
        self.assertEqual(self.save(seconds=1).status_code, 400)
        self.assertEqual(self.save(mode='hack').status_code, 400)
        self.assertFalse(TypingResult.objects.exists())

    def test_records_show_best_result_per_user(self):
        self.client.login(username='typist', password='typing-pass-1')
        self.save(chars=250)
        self.save(chars=400)
        page = self.client.get(reverse('typing_records') + '?mode=test&layout=ru&period=all')
        self.assertContains(page, 'typist')
        self.assertContains(page, '<b>400</b>')
        self.assertNotContains(page, '<b>250</b>')

    def test_anonymous_cannot_save(self):
        self.assertEqual(self.save().status_code, 302)
