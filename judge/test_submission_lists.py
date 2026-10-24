from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from judge.models import Language, Submission
from judge.models.tests.util import create_contest, create_contest_participation, create_contest_problem, \
    create_problem, create_user


class CommonListHidesRunningContestsTest(TestCase):
    fixtures = ['language_small.json']

    def setUp(self):
        now = timezone.now()
        self.viewer = create_user(username='list_viewer')
        self.viewer.set_password('viewer-pass-1')
        self.viewer.save()
        author = create_user(username='list_author').profile
        problem = create_problem(code='listprob', is_public=True)
        language = Language.objects.get(key='PY3')
        self.running = create_contest(key='running', start_time=now - timezone.timedelta(hours=1),
                                      end_time=now + timezone.timedelta(hours=1), is_visible=True,
                                      scoreboard_visibility='V')
        self.finished = create_contest(key='finished', start_time=now - timezone.timedelta(days=2),
                                       end_time=now - timezone.timedelta(days=1), is_visible=True,
                                       scoreboard_visibility='V')
        for contest in (self.running, self.finished):
            create_contest_problem(contest=contest, problem=problem)
            create_contest_participation(contest=contest, user=author)
        self.practice = Submission.objects.create(user=author, problem=problem, language=language, status='D',
                                                  result='AC')
        self.in_running = Submission.objects.create(user=author, problem=problem, language=language, status='D',
                                                    result='AC', contest_object=self.running)
        self.in_finished = Submission.objects.create(user=author, problem=problem, language=language, status='D',
                                                     result='AC', contest_object=self.finished)

    def ids(self):
        self.client.login(username='list_viewer', password='viewer-pass-1')
        page = self.client.get(reverse('all_submissions'))
        self.assertEqual(page.status_code, 200)
        return {s.id for s in page.context['submissions']}

    def test_running_contest_is_hidden_finished_is_shown(self):
        ids = self.ids()
        self.assertIn(self.practice.id, ids)
        self.assertNotIn(self.in_running.id, ids)
        self.assertIn(self.in_finished.id, ids)
