import time

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from judge.models.tests.util import create_problem, create_user
from judge.utils import online


class FakePipeline:
    def __init__(self, client):
        self.client = client
        self.calls = []

    def hset(self, key, member, value):
        self.calls.append(('hset', key, member, value))

    def expire(self, key, seconds):
        self.calls.append(('expire', key, seconds))

    def execute(self):
        for name, *args in self.calls:
            getattr(self.client, name)(*args)


class FakeRedis:
    """Just enough of redis.Redis for RedisBackend; values come back as bytes like the real client."""

    def __init__(self):
        self.data = {}
        self.expires = {}
        self.round_trips = 0

    def pipeline(self, transaction=False):
        self.round_trips += 1
        return FakePipeline(self)

    def hset(self, key, member, value):
        self.data.setdefault(key, {})[member] = value

    def expire(self, key, seconds):
        self.expires[key] = seconds

    def hgetall(self, key):
        self.round_trips += 1
        return {k.encode(): v.encode() for k, v in self.data.get(key, {}).items()}

    def hdel(self, key, *members):
        for m in members:
            self.data.get(key, {}).pop(m, None)


class ClassifyTest(TestCase):
    def test_tools(self):
        self.assertEqual(online.classify('workspace', {}), ('compiler', ''))
        self.assertEqual(online.classify('workspace_api_save', {'file_id': 1}), ('compiler', ''))
        self.assertEqual(online.classify('typing', {}), ('trainer', ''))
        self.assertEqual(online.classify('typing_save', {}), ('trainer', ''))
        self.assertEqual(online.classify('typing_records', {}), ('browse', 'typing_records'))

    def test_quiz(self):
        self.assertEqual(online.classify('quiz_play', {'pin': '123456'}), ('quiz', 'p:123456'))
        self.assertEqual(online.classify('quiz_state', {'pin': '123456'}), ('quiz', 'p:123456'))
        self.assertEqual(online.classify('quiz_solo', {'key': 'abc'}), ('quiz', 'k:abc'))
        self.assertEqual(online.classify('quiz_catalog', {}), ('browse', 'quiz_catalog'))

    def test_problems_and_contests(self):
        self.assertEqual(online.classify('problem_detail', {'problem': 'aplusb'}), ('problem', 'aplusb'))
        self.assertEqual(online.classify('problem_submit', {'problem': 'aplusb'}), ('problem', 'aplusb'))
        self.assertEqual(online.classify('contest_view', {'contest': 'c1'}), ('contest', 'k:c1'))
        # A participant solving a problem is shown under the contest.
        self.assertEqual(online.classify('problem_detail', {'problem': 'a'}, True, 7), ('contest', 'i:7'))
        self.assertEqual(online.classify('home', {}), ('browse', 'home'))

    def test_widget_own_requests_are_ignored(self):
        self.assertIsNone(online.classify('online_now', {}))
        self.assertIsNone(online.classify(None, {}))


class OnlineRecordingTest(TestCase):
    def setUp(self):
        cache.clear()
        self.user = create_user(username='ivan')
        self.user.set_password('online-pass-1')
        self.user.save()
        self.admin = create_user(username='boss', is_superuser=True, is_staff=True)
        self.admin.set_password('online-pass-1')
        self.admin.save()
        self.problem = create_problem(code='aplusb', name='A plus B', is_public=True)

    def login(self, name):
        self.client.login(username=name, password='online-pass-1')

    def rows(self):
        return {member: (kind, ref) for member, kind, ref in online.snapshot()}

    def test_page_views_are_recorded_with_throttle(self):
        self.login('ivan')
        self.client.get(reverse('problem_detail', args=['aplusb']))
        uid = 'u%d' % self.user.pk
        self.assertEqual(self.rows()[uid], ('problem', 'aplusb'))
        # Same page again within the throttle: no second write.
        first = cache.get(online.HASH_KEY)[uid]
        time.sleep(1.1)
        self.client.get(reverse('problem_detail', args=['aplusb']))
        self.assertEqual(cache.get(online.HASH_KEY)[uid], first)
        # A different page is written at once.
        self.client.get(reverse('problem_list'))
        self.assertEqual(self.rows()[uid], ('browse', 'problem_list'))

    def test_ajax_static_and_bots_are_not_recorded(self):
        self.login('ivan')
        self.client.get(reverse('problem_list'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(self.rows(), {})
        self.client.logout()
        self.client.get(reverse('home'), HTTP_USER_AGENT='Googlebot/2.1')
        self.assertEqual(self.rows(), {})

    def test_guests_are_counted_without_names(self):
        self.client.get(reverse('home'), HTTP_USER_AGENT='Mozilla/5.0 test')
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertTrue(next(iter(rows)).startswith('g'))

    def test_old_records_expire(self):
        backend = online.get_backend()
        now = time.time()
        backend.touch('u1', '%d|compiler|' % (now - online.WINDOW - 5))
        backend.touch('u2', '%d|trainer|' % now)
        self.assertEqual([m for m, _, _ in online.snapshot()], ['u2'])
        self.assertNotIn('u1', backend.all())

    def test_payload_groups_names_and_links(self):
        backend = online.get_backend()
        now = int(time.time())
        backend.touch('u%d' % self.user.pk, '%d|problem|aplusb' % now)
        backend.touch('u%d' % self.admin.pk, '%d|problem|aplusb' % now)
        backend.touch('g1', '%d|problem|aplusb' % now)
        backend.touch('g2', '%d|compiler|' % now)
        data = online.build_payload()
        self.assertEqual((data['total'], data['users'], data['guests']), (4, 2, 2))
        problem, compiler = data['groups']
        self.assertEqual(problem['title'], 'Задача A plus B')
        self.assertEqual(problem['url'], reverse('problem_detail', args=['aplusb']))
        self.assertEqual(problem['users'], ['boss', 'ivan'])
        self.assertEqual((problem['guests'], problem['count']), (1, 3))
        self.assertEqual((compiler['kind'], compiler['count'], compiler['users']), ('compiler', 1, []))

    def test_long_name_lists_are_cut(self):
        backend = online.get_backend()
        now = int(time.time())
        for i in range(online.NAMES_PER_GROUP + 5):
            user = create_user(username='bulk%d' % i)
            backend.touch('u%d' % user.pk, '%d|trainer|' % now)
        group = online.build_payload()['groups'][0]
        self.assertEqual(group['count'], online.NAMES_PER_GROUP + 5)
        self.assertEqual(len(group['users']), online.NAMES_PER_GROUP)
        self.assertEqual(group['more'], 5)

    def test_redis_backend(self):
        fake = FakeRedis()
        backend = online.RedisBackend(fake)
        backend.touch('u5', '%d|trainer|' % time.time())
        self.assertEqual(fake.round_trips, 1)
        self.assertEqual(fake.expires[online.HASH_KEY], 3600)
        self.assertEqual(list(backend.all()), ['u5'])
        backend.drop(['u5'])
        self.assertEqual(backend.all(), {})


class OnlineAccessTest(TestCase):
    def setUp(self):
        cache.clear()
        for name, kwargs in (('plain', {}), ('staff', {'is_staff': True}), ('root', {'is_superuser': True})):
            user = create_user(username=name, **kwargs)
            user.set_password('online-pass-1')
            user.save()

    def test_endpoint_is_for_admins_only(self):
        url = reverse('online_now')
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.login(username='plain', password='online-pass-1')
        self.assertEqual(self.client.get(url).status_code, 404)
        for name in ('staff', 'root'):
            self.client.login(username=name, password='online-pass-1')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.json()), {'total', 'users', 'guests', 'groups'})

    def test_widget_is_rendered_for_admins_only(self):
        marker = b'id="online-live"'
        self.assertNotIn(marker, self.client.get(reverse('home')).content)
        self.client.login(username='plain', password='online-pass-1')
        self.assertNotIn(marker, self.client.get(reverse('home')).content)
        self.client.login(username='root', password='online-pass-1')
        self.assertIn(marker, self.client.get(reverse('home')).content)
        self.client.login(username='staff', password='online-pass-1')
        self.assertIn(marker, self.client.get(reverse('home')).content)

    def test_polling_does_not_count_as_activity(self):
        self.client.login(username='root', password='online-pass-1')
        self.client.get(reverse('online_now'))
        self.assertEqual(online.snapshot(), [])

    def test_site_survives_broken_storage(self):
        from unittest import mock
        with mock.patch.object(online, 'get_backend', side_effect=RuntimeError('redis is down')):
            self.assertEqual(self.client.get(reverse('home')).status_code, 200)
