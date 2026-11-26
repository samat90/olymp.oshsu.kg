from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone, translation

from judge.models import Language, Submission, TypingResult
from judge.models.tests.util import create_problem, create_user
from judge.utils import attendance, visit_stats

CHROME = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
          'Chrome/126.0 Safari/537.36')
IPHONE = ('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
          'Version/17.0 Mobile/15E148 Safari/604.1')


def local(year, month, day, hour=12, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=ZoneInfo(settings.DEFAULT_USER_TIME_ZONE)).timestamp()


class UserAgentTest(TestCase):
    def test_devices(self):
        self.assertEqual(visit_stats.device_of(CHROME), 'desktop')
        self.assertEqual(visit_stats.device_of(IPHONE), 'mobile')
        self.assertEqual(visit_stats.device_of('Mozilla/5.0 (Linux; Android 14; SM-A52) Mobile Safari'), 'mobile')
        self.assertEqual(visit_stats.device_of('Mozilla/5.0 (Linux; Android 14; SM-X700) Safari'), 'tablet')
        self.assertEqual(visit_stats.device_of('Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) Mobile/15E148'),
                         'tablet')

    def test_browsers(self):
        self.assertEqual(visit_stats.browser_of(CHROME), 'Chrome')
        self.assertEqual(visit_stats.browser_of(IPHONE), 'Safari')
        self.assertEqual(visit_stats.browser_of(CHROME + ' Edg/126.0'), 'Edge')
        self.assertEqual(visit_stats.browser_of(CHROME + ' OPR/100.0'), 'Opera')
        self.assertEqual(visit_stats.browser_of(CHROME + ' YaBrowser/24.1'), 'Yandex')
        self.assertEqual(visit_stats.browser_of('Mozilla/5.0 (X11; rv:127.0) Gecko/20100101 Firefox/127.0'),
                         'Firefox')
        self.assertEqual(visit_stats.browser_of('SomethingElse/1.0'), 'other')

    def test_only_external_referrers_count(self):
        factory = RequestFactory()

        def host(referer):
            return visit_stats.referrer_host(factory.get('/', HTTP_REFERER=referer, HTTP_HOST='testserver'))

        self.assertEqual(host('https://www.google.com/search?q=secret'), 'google.com')
        self.assertEqual(host('https://t.me/'), 't.me')
        self.assertIsNone(host('http://testserver/problems/'))
        self.assertIsNone(host('http://127.0.0.1:8000/'))
        self.assertIsNone(host('http://10.10.8.178/'))
        self.assertIsNone(host('not a url'))
        self.assertIsNone(host('http://[broken'))
        self.assertIsNone(host('https://%s.com/' % ('a' * 200)))


class CountersTest(TestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def track(self, member, when, kind=('browse', 'home'), page=True, ua=CHROME, **extra):
        request = self.factory.get('/', HTTP_USER_AGENT=ua, **extra)
        visit_stats.track(request, member, kind[0], kind[1], page, now=when)

    def test_unique_visitors_views_and_periods(self):
        now = local(2026, 11, 26, 15, 30)
        self.track('u1', now)
        self.track('u1', now, ('problem', 'aplusb'))
        self.track('gaaaa', now)
        self.track('u2', now - 86400)               # yesterday
        self.track('u3', now - 10 * 86400)          # within the month only
        self.track('u1', now - 86400)               # the same person again: not a new one in the week
        data = visit_stats.read(now=now)
        self.assertEqual(data['today'], {'users': 1, 'guests': 1, 'visitors': 2, 'views': 3,
                                         'peak': 2, 'peak_time': '15:30'})
        self.assertEqual(data['yesterday'], {'users': 2, 'guests': 0, 'visitors': 2, 'views': 2})
        self.assertEqual(data['week'], {'users': 2, 'guests': 1, 'visitors': 3})
        self.assertEqual(data['month'], {'users': 3, 'guests': 1, 'visitors': 4})
        self.assertEqual(len(data['days']), 30)
        self.assertEqual(data['days'][-1], {'date': '2026-11-26', 'users': 1, 'guests': 1, 'views': 3})
        self.assertEqual(data['days'][-2]['users'], 2)
        self.assertEqual(data['since'], '2026-11-26')  # the day the counters were first written

    def test_since_is_the_first_recorded_day(self):
        self.assertIsNone(visit_stats.read(now=local(2026, 11, 26))['since'])
        self.track('u1', local(2026, 11, 20))
        self.track('u1', local(2026, 11, 26))
        self.assertEqual(visit_stats.read(now=local(2026, 11, 26))['since'], '2026-11-20')

    def test_activity_without_page_view_counts_the_visitor_only(self):
        now = local(2026, 11, 26)
        self.track('gq', now, ('quiz', 'p:1'), page=False)
        data = visit_stats.read(now=now)
        self.assertEqual((data['today']['guests'], data['today']['views']), (1, 0))
        self.assertEqual(data['pages']['today'], [])

    def test_hours_peak_and_heatmap(self):
        now = local(2026, 11, 26, 23, 0)           # a Thursday
        for member in ('u1', 'u2', 'u3'):
            self.track(member, local(2026, 11, 26, 9, 2))
        self.track('u1', local(2026, 11, 26, 18, 0))
        self.track('u1', local(2026, 11, 19, 9, 0))  # the Thursday before
        data = visit_stats.read(now=now)
        self.assertEqual(data['hours']['today'][9], {'visitors': 3, 'views': 3})
        self.assertEqual(data['hours']['today'][10], {'visitors': 0, 'views': 0})
        self.assertEqual((data['today']['peak'], data['today']['peak_time']), (3, '09:00'))
        self.assertEqual(len(data['heat']), 7)
        self.assertEqual(data['heat'][3][9], 2.0)   # average of two Thursdays: (3 + 1) / 2
        self.assertEqual(data['heat'][3][18], 0.5)
        self.assertEqual(data['heat'][0], [0] * 24)

    def test_hours_still_ahead_today_do_not_lower_the_average(self):
        self.track('u1', local(2026, 11, 19, 18, 0))  # last Thursday evening
        self.track('u1', local(2026, 11, 26, 9, 0))
        data = visit_stats.read(now=local(2026, 11, 26, 10, 0))
        self.assertEqual(data['heat'][3][18], 1.0)    # today's 18:00 has not come yet
        self.assertEqual(data['heat'][3][9], 0.5)     # today's 09:00 has

    def test_pages_sources_devices(self):
        now = local(2026, 11, 26)
        self.track('u1', now, ('problem', 'aplusb'), HTTP_REFERER='https://google.com/')
        self.track('u2', now, ('problem', 'aplusb'), ua=IPHONE)
        self.track('u2', now, ('quiz', 'p:123'))
        self.track('u2', now - 86400, ('quiz', 'k:zz'))
        data = visit_stats.read(now=now)
        self.assertEqual(data['pages']['today'], [('problem|aplusb', 2), ('quiz|', 1)])
        self.assertEqual(sorted(data['pages']['week']), [('problem|aplusb', 2), ('quiz|', 2)])
        self.assertEqual(data['sources']['today'], [('google.com', 1)])
        self.assertEqual(data['devices'], {'desktop': 2, 'mobile': 1, 'tablet': 0})
        self.assertEqual(data['browsers'], [('Chrome', 2), ('Safari', 1)])

    def test_referrer_flood_is_bounded(self):
        now = local(2026, 11, 26)
        for i in range(visit_stats.MAX_TRACKED + 40):
            self.track('u1', now, HTTP_REFERER='https://site%d.example/' % i)
        client = visit_stats.get_client()
        self.assertEqual(len(client.zrevrange('olst:ref:20261126', 0, -1)), visit_stats.MAX_TRACKED)


class MiddlewareCountingTest(TestCase):
    def setUp(self):
        cache.clear()
        user = create_user(username='ivan')
        user.set_password('stat-pass-1')
        user.save()
        create_problem(code='aplusb', name='A plus B', is_public=True)

    def today(self):
        return visit_stats.read()['today']

    def test_page_views_of_users_and_guests(self):
        self.client.get(reverse('home'), HTTP_USER_AGENT=CHROME)
        self.client.login(username='ivan', password='stat-pass-1')
        self.client.get(reverse('problem_detail', args=['aplusb']), HTTP_USER_AGENT=CHROME)
        self.client.get(reverse('problem_detail', args=['aplusb']), HTTP_USER_AGENT=CHROME)  # reload: throttled
        today = self.today()
        self.assertEqual((today['users'], today['guests'], today['views']), (1, 1, 2))

    def test_guests_without_user_agent_and_bots_are_ignored(self):
        self.client.get(reverse('home'))
        self.client.get(reverse('home'), HTTP_USER_AGENT='Googlebot/2.1')
        self.client.get(reverse('home'), HTTP_USER_AGENT='curl/8.0')
        self.assertEqual(self.today()['visitors'], 0)

    def test_guests_behind_the_university_proxy_are_told_apart(self):
        for ip in ('203.0.113.1', '203.0.113.2'):
            self.client.get(reverse('home'), HTTP_USER_AGENT=CHROME, HTTP_X_FORWARDED_FOR=ip + ', 10.10.8.178')
        self.assertEqual(self.today()['guests'], 2)

    def test_broken_counters_do_not_break_pages(self):
        with mock.patch.object(visit_stats, 'get_client', side_effect=RuntimeError('redis is down')):
            self.assertEqual(self.client.get(reverse('home'), HTTP_USER_AGENT=CHROME).status_code, 200)


class ActivityTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_database_activity_per_day(self):
        user = create_user(username='ann')
        old = create_user(username='old')
        User.objects.filter(pk=old.pk).update(date_joined=timezone.now() - timedelta(days=200))
        problem = create_problem(code='sum', name='Sum', is_public=True)
        language = Language.get_default_language()
        for _ in range(3):
            Submission.objects.create(user=user.profile, problem=problem, language=language)
        TypingResult.objects.create(user=user.profile, mode='test', layout='ru', seconds=60, chars=200, errors=1,
                                    cpm=200, accuracy=99)
        days = attendance.activity()
        self.assertEqual(len(days), 30)
        self.assertEqual(days[-1]['registrations'], 1)
        self.assertEqual((days[-1]['submissions'], days[-1]['authors']), (3, 1))
        self.assertEqual((days[-1]['typing'], days[-1]['quiz_games']), (1, 0))
        self.assertEqual(days[0]['registrations'], 0)

    def test_activity_is_cheap_and_cached(self):
        with self.assertNumQueries(4):
            attendance.get_activity()
        with self.assertNumQueries(0):
            attendance.get_activity()


class ReportTest(TestCase):
    def setUp(self):
        cache.clear()
        create_problem(code='aplusb', name='A plus B', is_public=True)

    def test_page_labels_are_resolved_and_merged(self):
        rows = [('problem|aplusb', 5), ('browse|home', 3), ('browse|judge_x_changelist', 2),
                ('browse|something', 1), ('quiz|', 4), ('compiler|', 1), ('contest|k:gone', 1)]
        with translation.override('en'):
            out = attendance.label_pages(rows)
        self.assertEqual([(p['title'], p['views']) for p in out], [
            ('Problem A plus B', 5), ('Quiz', 4), ('Home', 3), ('Other pages', 3), ('Compiler', 1), ('Contest', 1)])
        self.assertEqual(out[0]['url'], reverse('problem_detail', args=['aplusb']))
        self.assertIsNone(out[3]['url'])


class DashboardAccessTest(TestCase):
    def setUp(self):
        cache.clear()
        for name, kwargs in (('plain', {}), ('staff', {'is_staff': True}), ('root', {'is_superuser': True})):
            user = create_user(username=name, **kwargs)
            user.set_password('stat-pass-1')
            user.save()

    def test_admins_only(self):
        for url in (reverse('online_dashboard'), reverse('online_dashboard_data')):
            self.client.logout()
            self.assertEqual(self.client.get(url).status_code, 404)
            self.client.login(username='plain', password='stat-pass-1')
            self.assertEqual(self.client.get(url).status_code, 404)
            for name in ('staff', 'root'):
                self.client.login(username=name, password='stat-pass-1')
                self.assertEqual(self.client.get(url).status_code, 200, (name, url))

    def test_page_and_data(self):
        self.assertIn(settings.ADMIN_URL_PREFIX, reverse('online_dashboard'))
        self.client.login(username='root', password='stat-pass-1')
        page = self.client.get(reverse('online_dashboard'))
        self.assertContains(page, 'id="attendance"')
        self.assertContains(page, reverse('online_dashboard_data'))
        data = self.client.get(reverse('online_dashboard_data')).json()
        self.assertEqual(set(data), {'generated', 'since', 'today', 'yesterday', 'week', 'month', 'days', 'hours',
                                     'heat', 'pages', 'sources', 'devices', 'browsers', 'activity'})
        self.assertEqual(len(data['activity']), 30)

    def test_looking_at_the_dashboard_is_not_counted(self):
        self.client.login(username='root', password='stat-pass-1')
        self.client.get(reverse('online_dashboard'), HTTP_USER_AGENT=CHROME)
        self.assertEqual(visit_stats.read()['today']['visitors'], 0)

    def test_links_to_the_dashboard(self):
        self.client.login(username='root', password='stat-pass-1')
        url = reverse('online_dashboard')
        self.assertContains(self.client.get(reverse('home')), url)
        self.client.login(username='staff', password='stat-pass-1')
        self.assertContains(self.client.get(reverse('admin:index')), url)

    def test_dashboard_survives_broken_counters(self):
        self.client.login(username='root', password='stat-pass-1')
        with mock.patch.object(visit_stats, 'get_client', side_effect=RuntimeError('redis is down')):
            response = self.client.get(reverse('online_dashboard_data'))
        self.assertEqual(response.status_code, 503)
