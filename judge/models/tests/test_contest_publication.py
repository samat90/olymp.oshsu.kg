from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from judge.models import Contest, ContestProblem, Problem, ProblemGroup
from judge.utils.contest_publication import publish_finished_contest_problems


class ContestPublicationTests(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.group = ProblemGroup.objects.create(name='publication', full_name='Publication')
        self.contest = Contest.objects.create(key='publication', name='Publication', is_visible=True,
                                             start_time=self.now-timedelta(hours=3), end_time=self.now)

    def add_problem(self, code, contest=None, **fields):
        problem = Problem.objects.create(code=code, name=code, group=self.group, description='Statement',
                                         time_limit=1, memory_limit=65536, points=100,
                                         is_listed=False, **fields)
        ContestProblem.objects.create(contest=contest or self.contest, problem=problem, points=100, order=0)
        return problem

    def test_five_tasks_publish_at_end_and_are_available_to_everyone(self):
        problems = [self.add_problem('p%d' % i, is_organization_private=True) for i in range(5)]
        self.assertEqual(publish_finished_contest_problems(self.now-timedelta(seconds=1))['problems'], 0)
        result = publish_finished_contest_problems(self.now)
        self.assertEqual(result, {'contests':1, 'problems':5, 'waiting':0})
        for problem in problems:
            problem.refresh_from_db()
            self.assertTrue(problem.is_public)
            self.assertTrue(problem.is_listed)
            self.assertFalse(problem.is_organization_private)
            self.assertEqual(problem.date, self.contest.end_time)
            self.assertEqual(self.client.get('/problem/'+problem.code).status_code, 200)
        response = self.client.get('/problems/')
        self.assertEqual({p.pk for p in response.context['problems']}, {p.pk for p in problems})
        self.assertEqual(ContestProblem.objects.count(), 5)

    def test_hidden_contest_and_explicit_opt_out(self):
        problem = self.add_problem('private')
        self.contest.is_visible = False
        self.contest.save()
        self.assertEqual(publish_finished_contest_problems(self.now)['problems'], 0)
        self.contest.is_visible = True
        self.contest.publish_problems_after_end = False
        self.contest.save()
        self.assertEqual(publish_finished_contest_problems(self.now)['problems'], 0)
        problem.refresh_from_db()
        self.assertFalse(problem.is_public)

    def test_shared_task_waits_until_other_contest_ends(self):
        problem = self.add_problem('shared')
        later = Contest.objects.create(key='later', name='Later', is_visible=True,
                                       start_time=self.now, end_time=self.now+timedelta(days=1))
        ContestProblem.objects.create(contest=later, problem=problem, points=100, order=0)
        self.assertEqual(publish_finished_contest_problems(self.now)['waiting'], 1)
        self.contest.refresh_from_db()
        self.assertIsNone(self.contest.problems_published_at)
        problem.refresh_from_db()
        self.assertFalse(problem.is_public)
        self.assertEqual(publish_finished_contest_problems(later.end_time)['problems'], 1)
        problem.refresh_from_db()
        self.assertTrue(problem.is_public)

    def test_repeat_does_not_republish_manually_hidden_task(self):
        problem = self.add_problem('once')
        publish_finished_contest_problems(self.now)
        Problem.objects.filter(pk=problem.pk).update(is_listed=False)
        self.assertEqual(publish_finished_contest_problems(self.now+timedelta(minutes=1))['problems'], 0)
        problem.refresh_from_db()
        self.assertFalse(problem.is_listed)

    def test_task_added_after_finish_is_also_published(self):
        self.add_problem('first')
        publish_finished_contest_problems(self.now)
        extra = self.add_problem('extra')
        self.contest.refresh_from_db()
        self.assertIsNone(self.contest.problems_published_at)
        self.assertEqual(publish_finished_contest_problems(self.now+timedelta(minutes=1))['problems'], 1)
        extra.refresh_from_db()
        self.assertTrue(extra.is_public)

    def test_private_contest_publishes_tasks_after_finish(self):
        self.contest.is_private = True
        self.contest.save()
        problem = self.add_problem('closed-event')
        self.assertEqual(publish_finished_contest_problems(self.now)['problems'], 1)
        problem.refresh_from_db()
        self.assertEqual(self.client.get('/problem/'+problem.code).status_code, 200)
