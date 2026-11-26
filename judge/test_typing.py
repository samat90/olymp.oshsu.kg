import json
import random

from django.contrib.admin.models import LogEntry
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from judge.models import TypingResult
from judge.models.tests.util import create_user
from judge.views.typing import keystroke_problem, level_info


def human_keys(chars, seconds):
    """Uneven gaps between key presses that add up to the time, like a person typing."""
    rnd = random.Random(chars)
    gaps = [rnd.uniform(0.5, 1.5) for _ in range(chars - 1)]
    scale = seconds * 1000 * 0.98 / sum(gaps)
    return [0] + [int(g * scale) for g in gaps]


class TypingTrainerTest(TestCase):
    def setUp(self):
        cache.clear()
        self.user = create_user(username='typist')
        self.user.set_password('typing-pass-1')
        self.user.save()

    def ticket(self):
        return self.client.post(reverse('typing_start')).json()['token']

    def save(self, keys=None, ticket=True, wait=None, **data):
        body = {'mode': 'test', 'layout': 'ru', 'seconds': 60, 'chars': 300, 'errors': 3}
        body.update(data)
        if ticket:
            body['token'] = self.ticket()
            # The ticket must be older than the exercise: pretend it was taken a minute ago.
            run = cache.get('typing-run:' + body['token'])
            run['time'] -= body['seconds'] if wait is None else wait
            cache.set('typing-run:' + body['token'], run, 3600)
        body['keys'] = human_keys(body['chars'], body['seconds']) if keys is None else keys
        cache.delete('typing-save:%d' % self.user.profile.id)  # one save every few seconds per user
        return self.client.post(reverse('typing_save'), json.dumps(body), content_type='application/json')

    def test_pages_open(self):
        self.assertEqual(self.client.get(reverse('typing')).status_code, 200)
        self.assertEqual(self.client.get(reverse('typing_records')).status_code, 200)
        self.client.login(username='typist', password='typing-pass-1')
        self.assertEqual(self.client.get(reverse('typing')).status_code, 200)

    def test_save_counts_speed_on_the_server(self):
        self.client.login(username='typist', password='typing-pass-1')
        response = self.save(cpm=99999)
        self.assertEqual(response.status_code, 200)
        result = TypingResult.objects.get()
        self.assertEqual(result.cpm, 300)
        self.assertEqual(result.accuracy, 99.0)
        self.assertTrue(result.checked)
        self.assertTrue(response.json()['record'])
        self.assertFalse(self.save(chars=200).json()['record'])

    def test_impossible_results_are_rejected(self):
        self.client.login(username='typist', password='typing-pass-1')
        self.assertEqual(self.save(chars=5000, seconds=60).status_code, 400)   # 5000 chars a minute
        self.assertEqual(self.save(seconds=1).status_code, 400)
        self.assertEqual(self.save(mode='hack').status_code, 400)
        self.assertFalse(TypingResult.objects.exists())

    def test_paste_and_scripts_are_rejected(self):
        self.client.login(username='typist', password='typing-pass-1')
        self.assertEqual(self.save(ticket=False).status_code, 400)               # no ticket
        self.assertEqual(self.save(wait=5).status_code, 400)                     # ticket younger than the run
        pasted = [0] * 300
        self.assertEqual(self.save(keys=pasted).json()['why'], 'burst')         # whole text at once
        self.assertEqual(self.save(keys=[0] + [200] * 299).json()['why'], 'even')  # a script with a fixed delay
        self.assertEqual(self.save(keys=[0] * 10).json()['why'], 'count')       # fewer key presses than chars
        self.assertFalse(TypingResult.objects.exists())

    def test_ticket_is_used_once(self):
        self.client.login(username='typist', password='typing-pass-1')
        token = self.ticket()
        run = cache.get('typing-run:' + token)
        run['time'] -= 60
        cache.set('typing-run:' + token, run, 3600)
        body = {'mode': 'test', 'layout': 'ru', 'seconds': 60, 'chars': 300, 'errors': 3, 'token': token,
                'keys': human_keys(300, 60)}
        self.assertEqual(self.client.post(reverse('typing_save'), json.dumps(body),
                                          content_type='application/json').status_code, 200)
        cache.delete('typing-save:%d' % self.user.profile.id)
        self.assertEqual(self.client.post(reverse('typing_save'), json.dumps(body),
                                          content_type='application/json').status_code, 400)

    def test_records_show_best_checked_result_per_user(self):
        self.client.login(username='typist', password='typing-pass-1')
        self.save(chars=250)
        self.save(chars=400)
        TypingResult.objects.create(user=self.user.profile, mode='test', layout='ru', seconds=60, chars=900,
                                    errors=0, cpm=900, accuracy=100)   # an unchecked result
        page = self.client.get(reverse('typing_records') + '?mode=test&layout=ru&period=all')
        self.assertContains(page, 'typist')
        self.assertContains(page, '<b>400</b>')
        self.assertNotContains(page, '<b>250</b>')
        self.assertNotContains(page, '<b>900</b>')

    def admin_action(self, action, *results):
        url = reverse('admin:judge_typingresult_changelist')
        return self.client.post(url, {'action': action, '_selected_action': [r.pk for r in results]})

    def test_admin_removes_a_result_from_records_without_deleting_it(self):
        self.client.login(username='typist', password='typing-pass-1')
        self.save(chars=250)
        self.save(chars=900)
        cheat = TypingResult.objects.get(cpm=900)
        records = reverse('typing_records') + '?mode=test&layout=ru&period=all'
        self.assertContains(self.client.get(records), '<b>900</b>')          # now in the cached table

        self.client.force_login(create_user(username='boss', is_staff=True, is_superuser=True))
        self.assertEqual(self.admin_action('exclude_from_records', cheat).status_code, 302)

        cheat.refresh_from_db()
        self.assertFalse(cheat.checked)
        self.assertEqual(TypingResult.objects.count(), 2)
        page = self.client.get(records)                                      # the cache was dropped
        self.assertContains(page, '<b>250</b>')
        self.assertNotContains(page, '<b>900</b>')
        entry = LogEntry.objects.get(object_id=str(cheat.pk))
        self.assertIn('900', entry.get_change_message())

        self.assertEqual(self.admin_action('return_to_records', cheat).status_code, 302)
        cheat.refresh_from_db()
        self.assertTrue(cheat.checked)
        self.assertContains(self.client.get(records), '<b>900</b>')

    def test_view_only_staff_cannot_change_records(self):
        result = TypingResult.objects.create(user=self.user.profile, mode='test', layout='ru', seconds=60,
                                             chars=300, errors=0, cpm=300, accuracy=100, checked=True)
        viewer = create_user(username='viewer', is_staff=True, user_permissions=('view_typingresult',))
        self.client.force_login(viewer)
        self.admin_action('exclude_from_records', result)
        result.refresh_from_db()
        self.assertTrue(result.checked)

    def test_levels(self):
        self.assertEqual(level_info(0)['level'], 1)
        self.assertEqual(level_info(999)['level'], 1)
        self.assertEqual(level_info(1000)['level'], 2)
        self.assertEqual(level_info(3000)['level'], 3)
        self.assertEqual(level_info(2000)['percent'], 50)
        self.client.login(username='typist', password='typing-pass-1')
        response = self.save(chars=600, seconds=120).json()
        self.assertEqual(response['level']['xp'], 600)
        self.assertFalse(response['level_up'])
        self.assertTrue(self.save(chars=500, seconds=100).json()['level_up'])

    def test_keystroke_checks(self):
        self.assertIsNone(keystroke_problem(human_keys(200, 40), 200, 40))
        self.assertEqual(keystroke_problem(human_keys(200, 40), 200, 10), 'time')

    def test_anonymous_cannot_save(self):
        self.assertEqual(self.save(ticket=False).status_code, 302)
        self.assertEqual(self.client.post(reverse('typing_start')).status_code, 302)
