from django.test import TestCase
from django.utils import timezone

from judge.models import ContestSubmission, Language, Submission, SubmissionTestCase
from judge.models.tests.util import create_contest, create_contest_participation, create_contest_problem, \
    create_problem, create_user


class ContestFormatScoringTest(TestCase):
    """Every contest format must score submissions on the database we run in production (PostgreSQL)."""

    fixtures = ['language_small.json']

    def setUp(self):
        self.language = Language.objects.first()
        self.user = create_user(username='scoring_user')
        self.problem_a = create_problem(code='fmta', points=100, partial=True)
        self.problem_b = create_problem(code='fmtb', points=100, partial=True)

    def make_contest(self, key, format_name):
        contest = create_contest(key=key, format_name=format_name)
        cp_a = create_contest_problem(contest=contest, problem=self.problem_a, points=100, partial=True, order=1)
        cp_b = create_contest_problem(contest=contest, problem=self.problem_b, points=100, partial=True, order=2)
        participation = create_contest_participation(contest=contest, user=self.user.profile)
        return contest, participation, cp_a, cp_b

    def submit(self, participation, contest_problem, cases, minutes):
        """cases: list of (batch, points, total)."""
        sub = Submission.objects.create(user=self.user.profile, problem=contest_problem.problem,
                                        language=self.language, status='D', result='AC')
        Submission.objects.filter(id=sub.id).update(date=participation.start + timezone.timedelta(minutes=minutes))
        got = 0
        total = 0
        for i, (batch, points, case_total) in enumerate(cases, 1):
            SubmissionTestCase.objects.create(submission=sub, case=i, status='AC' if points else 'WA',
                                              points=points, total=case_total, batch=batch)
            got += points
            total += case_total
        sub.case_points = got
        sub.case_total = total
        sub.points = contest_problem.points * got / total
        sub.save()
        ContestSubmission.objects.create(submission=sub, problem=contest_problem, participation=participation,
                                         points=sub.points)
        return sub

    def test_ioi16_takes_best_batch_from_different_submissions(self):
        contest, participation, cp_a, cp_b = self.make_contest('fmt_ioi16', 'ioi16')
        # First try solves batch 1 only, second try solves batch 2 only: IOI 2016+ adds the best of each.
        self.submit(participation, cp_a, [(1, 50, 50), (2, 0, 50)], 10)
        self.submit(participation, cp_a, [(1, 0, 50), (2, 50, 50)], 20)
        self.submit(participation, cp_b, [(None, 30, 100)], 5)
        participation.recompute_results()
        participation.refresh_from_db()
        self.assertEqual(participation.score, 130)
        self.assertEqual(participation.format_data[str(cp_a.id)]['points'], 100)

    def test_legacy_ioi(self):
        contest, participation, cp_a, cp_b = self.make_contest('fmt_ioi', 'ioi')
        self.submit(participation, cp_a, [(None, 40, 100)], 10)
        self.submit(participation, cp_a, [(None, 70, 100)], 20)
        participation.recompute_results()
        participation.refresh_from_db()
        self.assertEqual(participation.score, 70)

    def test_icpc(self):
        contest, participation, cp_a, cp_b = self.make_contest('fmt_icpc', 'icpc')
        self.submit(participation, cp_a, [(None, 0, 100)], 10)
        self.submit(participation, cp_a, [(None, 100, 100)], 20)
        participation.recompute_results()
        participation.refresh_from_db()
        self.assertEqual(participation.score, 100)

    def test_atcoder(self):
        contest, participation, cp_a, cp_b = self.make_contest('fmt_atcoder', 'atcoder')
        self.submit(participation, cp_a, [(None, 100, 100)], 15)
        participation.recompute_results()
        participation.refresh_from_db()
        self.assertEqual(participation.score, 100)

    def test_default(self):
        contest, participation, cp_a, cp_b = self.make_contest('fmt_default', 'default')
        self.submit(participation, cp_b, [(None, 60, 100)], 15)
        participation.recompute_results()
        participation.refresh_from_db()
        self.assertEqual(participation.score, 60)
