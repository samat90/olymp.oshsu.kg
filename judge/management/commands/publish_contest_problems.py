import json

from django.core.management.base import BaseCommand

from judge.utils.contest_publication import publish_finished_contest_problems


class Command(BaseCommand):
    help = 'Publish problems from finished contests into the public archive.'

    def handle(self, *args, **options):
        self.stdout.write(json.dumps(publish_finished_contest_problems()))
