from importlib import import_module

from django.test import TestCase
from django.utils import timezone

from judge.models import ContestParticipation, ContestSubmission, Language, Problem, Submission
from judge.models.tests.util import create_contest, create_contest_problem, create_problem, create_user

to_partial = import_module('judge.migrations.0176_partial_points_everywhere').to_partial


class PartialPointsEverywhereTest(TestCase):
    fixtures = ['language_small.json']

    def submit(self, user, problem, result, case_points, case_total, points):
        return Submission.objects.create(user=user.profile, problem=problem, language=Language.objects.first(),
                                         status='D', result=result, case_points=case_points,
                                         case_total=case_total, points=points)

    def test_old_submissions_get_partial_points(self):
        student = create_user(username='pp_student')
        full = create_problem(code='ppa', points=100, partial=False, is_public=True)
        half = create_problem(code='ppb', points=100, partial=False, is_public=True)
        part = create_problem(code='ppc', points=100, partial=True, is_public=True)
        self.submit(student, full, 'AC', 10, 10, 100)
        self.submit(student, half, 'WA', 5, 10, 0)
        self.submit(student, half, 'CE', 0, 0, 0)
        self.submit(student, part, 'WA', 1, 4, 25)

        to_partial(None, None)

        self.assertEqual(set(Problem.objects.values_list('partial', flat=True)), {True})
        self.assertEqual(sorted(Submission.objects.values_list('points', flat=True)), [0, 25, 50, 100])
        student.profile.refresh_from_db()
        self.assertEqual(student.profile.points, 175)
        self.assertEqual(student.profile.performance_points, 175)
        self.assertEqual(student.profile.problem_count, 1)

    def test_contest_results_untouched(self):
        student = create_user(username='pp_contestant')
        now = timezone.now()
        contest = create_contest(key='ppcontest', start_time=now - timezone.timedelta(hours=2),
                                 end_time=now - timezone.timedelta(hours=1))
        problem = create_problem(code='ppd', points=100, partial=False)
        cp = create_contest_problem(contest=contest, problem=problem, points=100, partial=False)
        participation = ContestParticipation.objects.create(contest=contest, user=student.profile)
        sub = self.submit(student, problem, 'WA', 1, 2, 0)
        ContestSubmission.objects.create(submission=sub, problem=cp, participation=participation, points=0)

        to_partial(None, None)

        cp.refresh_from_db()
        self.assertFalse(cp.partial)
        self.assertEqual(ContestSubmission.objects.get().points, 0)
        self.assertEqual(Submission.objects.get().points, 50)

    def test_rating_is_plain_sum(self):
        student = create_user(username='pp_sum')
        for i in range(30):
            problem = create_problem(code='pps%d' % i, points=100, is_public=True)
            self.submit(student, problem, 'AC', 1, 1, 100)

        student.profile.calculate_points()

        self.assertEqual(student.profile.points, 3000)
        self.assertEqual(student.profile.performance_points, 3000)
        self.assertEqual(student.profile.problem_count, 30)
