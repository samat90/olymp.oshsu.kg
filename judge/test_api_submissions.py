from django.test import TestCase

from judge.models import Language, Submission
from judge.models.tests.util import create_problem, create_user


class APISubmissionListTest(TestCase):
    fixtures = ['language_small.json']

    def test_list_shows_only_visible_problems(self):
        student = create_user(username='api_student')
        public = create_problem(code='apipub', is_public=True)
        hidden = create_problem(code='apihid', is_public=False)
        for problem in (public, hidden):
            Submission.objects.create(user=student.profile, problem=problem, language=Language.objects.first(),
                                      status='D', result='AC', case_points=1, case_total=1, points=100)

        for url in ('/api/v2/submissions', '/api/v2/submissions?user=api_student'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                problems = [sub['problem'] for sub in response.json()['data']['objects']]
                self.assertEqual(problems, ['apipub'])
