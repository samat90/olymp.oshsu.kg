import importlib.util
import os

from django.conf import settings
from django.db import migrations


def clean(apps, schema_editor):
    """The site has no formula renderer: show $...$ in the statements of the training set as plain text."""
    base = os.path.join(settings.BASE_DIR, 'problemsets', 'train2026')
    path = os.path.join(base, 'statement_math.py')
    names_file = os.path.join(base, 'names.txt')
    if not (os.path.exists(path) and os.path.exists(names_file)):
        return
    spec = importlib.util.spec_from_file_location('statement_math', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    names = {line.rstrip('\n').split('\t')[-1] for line in open(names_file, encoding='utf-8') if line.strip()}
    Problem = apps.get_model('judge', 'Problem')
    changed = 0
    for problem in Problem.objects.filter(name__in=names, description__contains='$').only('id', 'description'):
        text = module.clean_math(problem.description)
        if text != problem.description:
            Problem.objects.filter(pk=problem.pk).update(description=text)
            changed += 1
    print('  statements without raw $: %d' % changed)


class Migration(migrations.Migration):
    dependencies = [('judge', '0182_quiz_player_avatar')]
    operations = [migrations.RunPython(clean, migrations.RunPython.noop, elidable=True)]
