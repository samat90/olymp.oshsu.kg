from importlib import import_module

from django.test import TestCase
from django.utils import timezone

from judge.models import ContestParticipation, ContestSubmission, Language, Problem, Submission
from judge.models.tests.util import create_contest, create_contest_problem, create_problem, create_user

to_100 = import_module('judge.migrations.0169_all_problems_100_points').to_100


class AllProblems100PointsTest(TestCase):
    fixtures = ['language_small.json']

    def submit(self, user, problem, result, case_points, case_total, points):
        return Submission.objects.create(user=user.profile, problem=problem, language=Language.objects.first(),
                                         status='D', result=result, case_points=case_points,
                                         case_total=case_total, points=points)

    def test_old_solutions_get_100(self):
        student = create_user(username='p100_student')
        full = create_problem(code='p100a', points=1, partial=False, is_public=True)
        part = create_problem(code='p100b', points=10, partial=True, is_public=True)
        self.submit(student, full, 'AC', 5, 5, 1)
        self.submit(student, full, 'WA', 3, 5, 0)
        self.submit(student, part, 'WA', 2, 4, 5)
        student.profile.calculate_points()

        to_100(None, None)

        self.assertEqual(set(Problem.objects.values_list('points', flat=True)), {100})
        self.assertEqual(sorted(Submission.objects.values_list('points', flat=True)), [0, 50, 100])
        student.profile.refresh_from_db()
        self.assertEqual(student.profile.points, 150)
        self.assertEqual(student.profile.problem_count, 1)

    def test_contest_results_recomputed(self):
        student = create_user(username='p100_contestant')
        now = timezone.now()
        contest = create_contest(key='p100c', start_time=now - timezone.timedelta(hours=2),
                                 end_time=now - timezone.timedelta(hours=1), format_name='ioi')
        problem = create_problem(code='p100c', points=1, partial=True)
        cp = create_contest_problem(contest=contest, problem=problem, points=10, partial=True)
        participation = ContestParticipation.objects.create(contest=contest, user=student.profile)
        sub = self.submit(student, problem, 'WA', 1, 2, 0.5)
        Submission.objects.filter(id=sub.id).update(date=now - timezone.timedelta(minutes=90))
        ContestSubmission.objects.create(submission=sub, problem=cp, participation=participation, points=5)
        participation.recompute_results()

        to_100(None, None)

        cp.refresh_from_db()
        participation.refresh_from_db()
        self.assertEqual(cp.points, 100)
        self.assertEqual(ContestSubmission.objects.get().points, 50)
        self.assertEqual(participation.score, 50)
        self.assertEqual(Submission.objects.get().points, 50)
