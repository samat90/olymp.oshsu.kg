import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from judge.utils.problem_codes import apply_plan, build_plan


class Command(BaseCommand):
    help = 'Plan, apply or reverse six-digit problem codes without changing primary keys.'

    def add_arguments(self, parser):
        parser.add_argument('--mode', choices=('plan', 'apply', 'rollback'), default='plan')
        parser.add_argument('--plan', required=True)

    def handle(self, *args, **options):
        path = Path(options['plan'])
        root = Path(settings.DMOJ_PROBLEM_DATA_ROOT)
        try:
            if options['mode'] == 'plan':
                plan = build_plan(root)
                with path.open('x', encoding='utf-8') as stream:
                    json.dump(plan, stream, ensure_ascii=False, indent=2)
                path.chmod(0o600)
            else:
                plan = json.loads(path.read_text(encoding='utf-8'))
                apply_plan(plan, root, rollback=options['mode'] == 'rollback',
                           journal=path.with_suffix('.journal.jsonl'))
        except (ValueError, OSError) as error:
            raise CommandError(str(error)) from error
        self.stdout.write('%s: %d problems' % (options['mode'], len(plan['rows'])))
