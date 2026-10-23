import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from judge.models import ContestCheatEvent, ContestParticipation
from judge.models.tests.util import create_contest, create_contest_participation, create_contest_problem, \
    create_problem, create_user


class AnticheatTest(TestCase):
    fixtures = ['language_small.json']

    def setUp(self):
        now = timezone.now()
        self.contest = create_contest(key='acx', start_time=now - timezone.timedelta(hours=1),
                                      end_time=now + timezone.timedelta(hours=1), is_visible=True,
                                      anticheat_max_warnings=3)
        create_contest_problem(contest=self.contest, problem=create_problem(code='acp'))
        self.user = create_user(username='ac_user')
        self.user.set_password('ac-pass-123')
        self.user.save()
        self.participation = create_contest_participation(contest=self.contest, user=self.user.profile)
        profile = self.user.profile
        profile.current_contest = self.participation
        profile.save()
        self.client.login(username='ac_user', password='ac-pass-123')

    def report(self, kind='hidden'):
        return self.client.post(reverse('contest_anticheat_report', args=('acx',)), json.dumps({'kind': kind}),
                                content_type='application/json').json()

    def age_events(self):
        # Make the previous events old so the next one is not merged with them.
        ContestCheatEvent.objects.update(time=timezone.now() - timezone.timedelta(minutes=1))

    def test_three_warnings_then_disqualified(self):
        for i in range(1, 4):
            data = self.report()
            self.assertTrue(data['counted'])
            self.assertEqual(data['warnings'], i)
            self.assertFalse(data['disqualified'])
            self.age_events()
        data = self.report()
        self.assertTrue(data['disqualified'])
        self.participation.refresh_from_db()
        self.assertTrue(self.participation.is_disqualified)

    def test_quick_events_are_merged(self):
        self.assertTrue(self.report('blur')['counted'])
        self.assertFalse(self.report('hidden')['counted'])
        self.assertEqual(self.participation.cheat_events.filter(counted=True).count(), 1)
        self.assertEqual(self.participation.cheat_events.count(), 2)

    def test_paste_is_never_merged(self):
        self.report('blur')
        self.assertTrue(self.report('paste')['counted'])

    def test_disabled_contest_does_not_track(self):
        self.contest.anticheat_enabled = False
        self.contest.save()
        self.assertFalse(self.report()['tracking'])
        self.assertFalse(ContestCheatEvent.objects.exists())

    def test_not_tracked_after_end(self):
        self.contest.end_time = timezone.now() - timezone.timedelta(minutes=1)
        self.contest.save()
        self.assertFalse(self.report()['tracking'])

    def test_script_on_contest_pages_only_for_participant(self):
        page = self.client.get(reverse('contest_view', args=('acx',)))
        self.assertContains(page, 'OLYMP_ANTICHEAT')
        self.client.logout()
        page = self.client.get(reverse('problem_list'))
        self.assertNotContains(page, 'OLYMP_ANTICHEAT')

    def test_lifting_disqualification_forgives_warnings(self):
        for _ in range(4):
            self.report()
            self.age_events()
        admin = create_user(username='ac_admin', is_superuser=True, is_staff=True)
        admin.set_password('ac-pass-123')
        admin.save()
        self.client.login(username='ac_admin', password='ac-pass-123')
        self.client.post(reverse('contest_participation_disqualify', args=('acx',)),
                         {'participation': self.participation.id, 'next': 'violations'})
        self.participation.refresh_from_db()
        self.assertFalse(self.participation.is_disqualified)
        self.assertEqual(self.participation.cheat_events.filter(counted=True).count(), 0)
        page = self.client.get(reverse('contest_violations', args=('acx',)))
        self.assertContains(page, 'ac_user')


class PublicResultsTest(TestCase):
    fixtures = ['language_small.json']

    def setUp(self):
        now = timezone.now()
        self.contest = create_contest(key='pubres', start_time=now - timezone.timedelta(hours=3),
                                      end_time=now - timezone.timedelta(hours=1), is_visible=True)
        self.student = create_user(username='pr_student')
        self.contest.is_private = True
        self.contest.save()
        self.contest.private_contestants.add(self.student.profile)
        ContestParticipation.objects.create(contest=self.contest, user=self.student.profile, score=50)

    def test_private_contest_ranking_open_after_end(self):
        response = self.client.get(reverse('contest_ranking', args=('pubres',)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pr_student')

    def test_closed_when_option_off(self):
        self.contest.results_public_after_end = False
        self.contest.save()
        response = self.client.get(reverse('contest_ranking', args=('pubres',)))
        self.assertNotContains(response, 'pr_student', status_code=response.status_code)

    def test_closed_before_end(self):
        self.contest.end_time = timezone.now() + timezone.timedelta(hours=1)
        self.contest.save()
        response = self.client.get(reverse('contest_ranking', args=('pubres',)))
        self.assertNotContains(response, 'pr_student', status_code=response.status_code)
