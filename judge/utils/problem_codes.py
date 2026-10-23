import hashlib
import json
from pathlib import Path

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from judge.models import Comment, CommentLock, EFFECTIVE_MATH_ENGINES, Problem, ProblemCodeAlias, ProblemData
from judge.utils.problem_code_storage import check_storage, data_path, directory_digest, log_move, rename_storage


def record_digest(record):
    fields = dict(record)
    fields.pop('code')
    return hashlib.sha256(json.dumps(fields, sort_keys=True, cls=DjangoJSONEncoder).encode()).hexdigest()


def build_plan(root):
    rows = []
    records = list(Problem.objects.order_by('pk').values())
    old_codes = {row['code']: row['id'] for row in records}
    aliases = dict(ProblemCodeAlias.objects.values_list('code', 'problem_id'))
    for record in records:
        pk, old = record['id'], record['code']
        if not 1 <= pk <= 999999:
            raise ValueError('Problem key exceeds six-digit range: %s' % pk)
        new = '%06d' % pk
        if old_codes.get(new, pk) != pk or aliases.get(new, pk) != pk or aliases.get(old, pk) != pk:
            raise ValueError('A number or old code belongs to another problem: %s' % new)
        data = ProblemData.objects.filter(problem_id=pk).values('zipfile', 'generator').first()
        rows.append({'pk': pk, 'old_code': old, 'new_code': new,
                     'digest': directory_digest(data_path(root, old)),
                     'record_digest': record_digest(record), 'data': data,
                     'alias_existed': old in aliases})
    check_storage(rows, root)
    return {'version': 1, 'rows': rows}


def check_records(plan):
    rows = plan['rows']
    records = {row['id']: row for row in Problem.objects.values()}
    if set(records) != {row['pk'] for row in rows}:
        raise ValueError('Problem set changed after the plan was created')
    for row in rows:
        record = records[row['pk']]
        if record['code'] not in (row['old_code'], row['new_code']):
            raise ValueError('Problem code changed: %s' % row['pk'])
        if record_digest(record) != row['record_digest']:
            raise ValueError('Problem settings changed: %s' % row['pk'])
        data = ProblemData.objects.filter(problem_id=row['pk']).values('zipfile', 'generator').first()
        expected = row['data']
        if data is None or expected is None:
            if data != expected:
                raise ValueError('Problem data record changed: %s' % row['pk'])
        else:
            for field in ('zipfile', 'generator'):
                paths = {expected[field], replace_prefix(expected[field], row['old_code'], row['new_code'])}
                if data[field] not in paths:
                    raise ValueError('Problem data path changed: %s' % row['pk'])


def replace_prefix(value, old, new):
    if not value:
        return value
    if not value.startswith(old + '/'):
        raise ValueError('Unexpected data file path for problem: %s' % old)
    return new + value[len(old):]


def update_records(plan, rollback=False):
    for row in plan['rows']:
        pk, old, new = row['pk'], row['old_code'], row['new_code']
        if old == new:
            continue
        target = old if rollback else new
        # Files have already moved explicitly; do not invoke save's file hook.
        Problem.objects.filter(pk=pk).update(code=target)
        if row['data'] is not None:
            fields = row['data'] if rollback else {
                field: replace_prefix(value, old, new) for field, value in row['data'].items()}
            ProblemData.objects.filter(problem_id=pk).update(**fields)
        for prefix in ('p:', 's:'):
            before, after = (new, old) if rollback else (old, new)
            Comment.objects.filter(page=prefix + before).update(page=prefix + after)
            CommentLock.objects.filter(page=prefix + before).update(page=prefix + after)
        if rollback:
            if not row['alias_existed']:
                ProblemCodeAlias.objects.filter(code=old, problem_id=pk).delete()
        else:
            alias, _ = ProblemCodeAlias.objects.get_or_create(code=old, defaults={'problem_id': pk})
            if alias.problem_id != pk:
                raise ValueError('Old code belongs to another problem: %s' % old)


def apply_plan(plan, root, rollback=False, journal=None):
    if plan.get('version') != 1:
        raise ValueError('Unsupported problem numbering plan')
    moved = []
    try:
        with transaction.atomic():
            list(Problem.objects.select_for_update().values_list('pk', flat=True))
            check_records(plan)
            check_storage(plan['rows'], root, rollback)
            moved = rename_storage(plan['rows'], root, rollback, journal)
            update_records(plan, rollback)
    except Exception:
        for source, target in reversed(moved):
            target.rename(source)
            log_move(journal, target, source)
        raise
    # Sessions share this cache in production. Never flush the whole cache.
    keys = []
    for row in plan['rows']:
        pk = row['pk']
        keys.extend(make_template_fragment_key(name, (pk,)) for name in ('submission_problem', 'problem_feed'))
        for language, _ in settings.LANGUAGES:
            keys.append('generated-meta-problem:%s:%d' % (language, pk))
            keys.extend(make_template_fragment_key('problem_html', (pk, engine, language))
                        for engine in EFFECTIVE_MATH_ENGINES)
    cache.delete_many(keys)
