import os

from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import migrations


def flush(apps, schema_editor):
    """The rendered statements are cached for a day; drop the cached pages of the training set after 0183 changed them."""
    from judge.signals import EFFECTIVE_MATH_ENGINES
    names_file = os.path.join(settings.BASE_DIR, 'problemsets', 'train2026', 'names.txt')
    if not os.path.exists(names_file):
        return
    names = {line.rstrip('\n').split('\t')[-1] for line in open(names_file, encoding='utf-8') if line.strip()}
    Problem = apps.get_model('judge', 'Problem')
    keys = []
    for pk in Problem.objects.filter(name__in=names).values_list('pk', flat=True):
        for language, _ in settings.LANGUAGES:
            keys.append('generated-meta-problem:%s:%d' % (language, pk))
            keys.extend(make_template_fragment_key('problem_html', (pk, engine, language))
                        for engine in EFFECTIVE_MATH_ENGINES)
    for i in range(0, len(keys), 500):
        cache.delete_many(keys[i:i + 500])
    print('  cached statement pages dropped: %d' % len(keys))


class Migration(migrations.Migration):
    dependencies = [('judge', '0183_clean_statement_math')]
    operations = [migrations.RunPython(flush, migrations.RunPython.noop, elidable=True)]
