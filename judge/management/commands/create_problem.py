from django.core.management.base import BaseCommand

from judge.models import Language, Problem, ProblemGroup, ProblemType


class Command(BaseCommand):
    help = 'create an empty problem'

    def add_arguments(self, parser):
        parser.add_argument('code', help='problem code')
        parser.add_argument('name', help='problem title')
        parser.add_argument('body', help='problem description')
        parser.add_argument('type', help='problem type')
        parser.add_argument('group', help='problem group')
        parser.add_argument('--time-limit', type=float, default=1)
        parser.add_argument('--memory-limit', type=int, default=262144)
        parser.add_argument('--points', type=float, default=100)

    def handle(self, *args, **options):
        problem = Problem()
        problem.code = options['code']
        problem.name = options['name']
        problem.description = options['body']
        problem.time_limit = options['time_limit']
        problem.memory_limit = options['memory_limit']
        problem.points = options['points']
        problem.group = ProblemGroup.objects.get(name=options['group'])
        problem.save()
        problem.types.set([ProblemType.objects.get(name=options['type'])])
        problem.allowed_languages.set(Language.objects.filter(key__in=['CPP17', 'CPP20', 'PY3', 'CSHARP']))
        self.stdout.write(problem.code)
