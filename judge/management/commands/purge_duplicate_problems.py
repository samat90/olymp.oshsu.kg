from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from judge.models import ContestProblem, Problem, Profile, Submission


def parse_codes(text):
    codes = set()
    for part in text.replace('\n', ',').split(','):
        part = part.strip()
        if not part:
            continue
        lo, _, hi = part.partition('-')
        for n in range(int(lo), int(hi or lo) + 1):
            codes.add('%06d' % n)
    return codes


class Command(BaseCommand):
    help = 'Report (default) or delete the repeated archive problems listed in a ranges file.'

    def add_arguments(self, parser):
        parser.add_argument('ranges_file')
        parser.add_argument('--apply', action='store_true')
        parser.add_argument('--force', action='store_true',
                            help='delete even if submissions or contest links exist')

    def handle(self, ranges_file, apply, force, **options):
        with open(ranges_file, encoding='utf-8') as f:
            codes = parse_codes(f.read())
        problems = Problem.objects.filter(code__in=codes)
        ids = list(problems.values_list('id', flat=True))
        subs = Submission.objects.filter(problem_id__in=ids)
        users = list(subs.values_list('user_id', flat=True).distinct())
        contests = ContestProblem.objects.filter(problem_id__in=ids)
        out = self.stdout.write
        out('codes in file: %d, found in DB: %d' % (len(codes), len(ids)))
        out('submissions: %d, users: %d' % (subs.count(), len(users)))
        out('contest links: %d' % contests.count())
        out('problems kept: %d' % Problem.objects.exclude(id__in=ids).count())
        if not apply:
            out('dry run, nothing deleted')
            return
        if (subs.exists() or contests.exists()) and not force:
            raise CommandError('submissions/contest links exist; rerun with --force after approval')
        with transaction.atomic():
            problems.delete()
        for profile in Profile.objects.filter(id__in=users):
            profile.calculate_points()
        out('deleted %d problems, points recalculated for %d users' % (len(ids), len(users)))
