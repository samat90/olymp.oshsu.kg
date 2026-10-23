"""Admin page: create a problem from a statement file and a test archive."""
import io
import os
import tempfile
import uuid
import zipfile

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _, gettext_lazy

from judge.models import Language, Problem, ProblemData, ProblemGroup, ProblemTestCase
from judge.utils.problem_data import ProblemDataCompiler
from judge.utils.problem_import import build_tests_zip, read_upload

MAX_STATEMENT = 512 * 1024
MAX_ARCHIVE = 64 * 1024 * 1024
TMP_DIR = os.path.join(tempfile.gettempdir(), 'olymp-import')


class UploadForm(forms.Form):
    statement = forms.FileField(label=gettext_lazy('Statement file (.md or .txt)'), required=False)
    archive = forms.FileField(label=gettext_lazy('Archive with tests (.zip)'), required=False,
                              help_text=gettext_lazy('May also contain the statement file itself.'))

    def clean(self):
        data = super().clean()
        statement, archive = data.get('statement'), data.get('archive')
        if not statement and not archive:
            raise forms.ValidationError(_('Attach a statement file, a zip archive or both.'))
        if statement and statement.size > MAX_STATEMENT:
            raise forms.ValidationError(_('The statement file is too big.'))
        if archive and archive.size > MAX_ARCHIVE:
            raise forms.ValidationError(_('The archive is larger than 64 MB.'))
        if archive and not archive.name.lower().endswith('.zip'):
            raise forms.ValidationError(_('Tests must be in a .zip archive.'))
        return data


class ReviewForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput)
    name = forms.CharField(max_length=100, label=gettext_lazy('Problem name'))
    time_limit = forms.FloatField(min_value=0.1, max_value=20, label=gettext_lazy('Time limit, seconds'))
    memory_mb = forms.IntegerField(min_value=16, max_value=1024, label=gettext_lazy('Memory limit, MB'))
    points = forms.FloatField(min_value=1, initial=100, label=gettext_lazy('Points'))
    is_public = forms.BooleanField(required=False, label=gettext_lazy('Show in the public problem list'),
                                   help_text=gettext_lazy('Leave it off for olympiad problems: they open '
                                                          'automatically after the contest if the contest says so.'))
    description = forms.CharField(label=gettext_lazy('Statement (Markdown)'), widget=forms.Textarea(
        attrs={'rows': 22, 'style': 'width: 100%; font-family: monospace'}))


def _store(parsed):
    """Keep the tests between the two steps as a zip in a private temp folder."""
    os.makedirs(TMP_DIR, mode=0o700, exist_ok=True)
    token = uuid.uuid4().hex
    with open(os.path.join(TMP_DIR, token), 'wb') as f:
        f.write(build_tests_zip(parsed.tests))
    return token


def _load(token):
    if not token.isalnum() or len(token) != 32:
        return None
    try:
        with open(os.path.join(TMP_DIR, token), 'rb') as f:
            archive = zipfile.ZipFile(io.BytesIO(f.read()))
    except (OSError, zipfile.BadZipFile):
        return None
    names = sorted(archive.namelist())
    inputs = [n for n in names if n.endswith('.in')]
    return [(archive.read(n), archive.read(n[:-3] + '.out')) for n in inputs]


def _forget(token):
    try:
        os.remove(os.path.join(TMP_DIR, token))
    except OSError:
        pass


@staff_member_required
def import_problem(request):
    if not request.user.has_perm('judge.add_problem'):
        raise PermissionDenied()

    if request.method == 'POST' and 'token' in request.POST:
        review = ReviewForm(request.POST)
        tests = _load(request.POST.get('token', ''))
        if tests is None:
            messages.error(request, _('The uploaded files expired. Please upload them again.'))
            return HttpResponseRedirect(reverse('admin_import_problem'))
        if review.is_valid():
            problem = create_problem(request, review.cleaned_data, tests)
            _forget(review.cleaned_data['token'])
            messages.success(request, _('Problem %(code)s "%(name)s" was created with %(n)d tests.') % {
                'code': problem.code, 'name': problem.name, 'n': len(tests)})
            return HttpResponseRedirect(reverse('admin:judge_problem_change', args=(problem.id,)))
        return render(request, 'admin/import_problem.html', {
            'title': _('Import a problem'), 'review': review, 'tests_count': len(tests),
        })

    upload = UploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and upload.is_valid():
        statement = upload.cleaned_data.get('statement')
        archive = upload.cleaned_data.get('archive')
        parsed = read_upload(statement.name if statement else '', statement.read() if statement else None,
                             archive.read() if archive else None)
        if not parsed.description.strip():
            for warning in parsed.warnings:
                messages.error(request, warning)
            return render(request, 'admin/import_problem.html', {'title': _('Import a problem'), 'upload': upload})
        token = _store(parsed)
        review = ReviewForm(initial={
            'token': token, 'name': parsed.name, 'time_limit': parsed.time_limit,
            'memory_mb': max(16, parsed.memory_limit // 1024), 'points': parsed.points,
            'description': parsed.description,
        })
        return render(request, 'admin/import_problem.html', {
            'title': _('Import a problem'), 'review': review, 'parsed': parsed,
            'tests_count': len(parsed.tests), 'tests_preview': [
                (inp[:200].decode('utf-8', 'replace'), out[:200].decode('utf-8', 'replace'))
                for inp, out in parsed.tests[:3]
            ],
        })
    return render(request, 'admin/import_problem.html', {'title': _('Import a problem'), 'upload': upload})


def create_problem(request, data, tests):
    with transaction.atomic():
        problem = Problem(
            code='imp' + uuid.uuid4().hex[:12],  # replaced by a six-digit number on save
            name=data['name'],
            description=data['description'],
            time_limit=data['time_limit'],
            memory_limit=data['memory_mb'] * 1024,
            points=data['points'],
            partial=True,
            is_public=data['is_public'],
            group=ProblemGroup.objects.order_by('id').first(),
        )
        problem.save()
        problem.allowed_languages.set(Language.objects.all())
        if getattr(request, 'profile', None) is not None:
            problem.authors.add(request.profile)

        if tests:
            problem_data = ProblemData.objects.create(problem=problem)
            problem_data.zipfile.save('tests.zip', ContentFile(build_tests_zip(tests)), save=True)
            width = max(2, len(str(len(tests))))
            ProblemTestCase.objects.bulk_create([
                ProblemTestCase(dataset=problem, order=i, type='C', input_file='%0*d.in' % (width, i),
                                output_file='%0*d.out' % (width, i), points=1, is_pretest=False)
                for i in range(1, len(tests) + 1)
            ])
            valid_files = []
            for i in range(1, len(tests) + 1):
                valid_files += ['%0*d.in' % (width, i), '%0*d.out' % (width, i)]

    if tests:
        ProblemDataCompiler.generate(problem, problem_data, problem.cases.order_by('order'), valid_files)
    return problem
