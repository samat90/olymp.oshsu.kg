from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from judge.models import Problem, ProblemGroup, ProblemType


class ProblemArchiveTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = ProblemGroup.objects.create(name='archive-tests', full_name='Archive')
        for code, difficulty, listed in [('easy', 1, True), ('hard', 100, True),
                                         ('unknown', None, True), ('duplicate', 2, False)]:
            Problem.objects.create(code=code, name=code, group=group, difficulty=difficulty,
                                   is_listed=listed, is_public=True, time_limit=1,
                                   memory_limit=65536, points=100, description='Statement')
        Problem.objects.get(code='easy').types.add(ProblemType.objects.create(name='z-topic',full_name=''))
        Problem.objects.get(code='hard').types.add(ProblemType.objects.create(name='a-topic',full_name=''))

    def test_percent_bounds(self):
        problem = Problem.objects.get(code='easy')
        field = Problem._meta.get_field('difficulty')
        for value in (0, 101):
            with self.assertRaises(ValidationError):
                field.clean(value, problem)
            with self.assertRaises(IntegrityError), transaction.atomic():
                Problem.objects.filter(pk=problem.pk).update(difficulty=value)

    def test_sorting_and_filtering(self):
        for order, expected in [('difficulty', ['easy', 'hard', 'unknown']),
                                ('-difficulty', ['hard', 'easy', 'unknown'])]:
            response = self.client.get('/problems/', {'order':order})
            self.assertEqual(response.status_code, 200)
            self.assertEqual([p.code for p in response.context['problems']], expected)
        response = self.client.get('/problems/', {'difficulty_start':90, 'difficulty_end':100})
        self.assertEqual([p.code for p in response.context['problems']], ['hard'])
        self.assertContains(response, '100%')
        self.assertContains(response, 'order=-difficulty')

    def test_old_problem_still_accessible(self):
        response = self.client.get('/problem/duplicate')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'available-judges')
        self.assertTrue(Problem.objects.get(code='duplicate').is_public)

    def test_topics_sort_without_extra_filter(self):
        response = self.client.get('/problems/', {'order':'type'})
        self.assertEqual([p.code for p in response.context['problems']], ['unknown','hard','easy'])
        self.assertContains(response,'a-topic')
        self.assertContains(response,'z-topic')
