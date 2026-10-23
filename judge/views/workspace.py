"""Online editor: run tokens and the personal workspace with files and folders."""
import json
import re

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

from judge.models import Language, Problem, WorkspaceFile
from judge.models.workspace import MAX_DEPTH, MAX_FILE_SIZE, MAX_FILES_PER_USER
from judge.utils.runner import make_token, public_url, runner_enabled
from judge.utils.views import generic_message

NAME_RE = re.compile(r'^[^\\/:*?"<>|\x00-\x1f]{1,100}$')
# When two languages share an extension, the first one listed wins.
PREFERRED = ['CPP17', 'CPP20', 'C', 'PY3', 'JAVA8', 'JAVA', 'CSHARP', 'MONOCS', 'NODEJS', 'GO', 'KOTLIN', 'PAS']


def in_live_contest(request):
    participation = getattr(request, 'participation', None)
    return bool(participation is not None and participation.live and not participation.ended)


def available_languages():
    return list(Language.objects.filter(judges__online=True).distinct().order_by('name'))


def editor_language_info(languages):
    """What the editor needs to know about each language."""
    return [{
        'id': lang.id,
        'key': lang.key,
        'name': lang.name,
        'ace': lang.ace,
        'ext': lang.extension,
        'template': lang.template,
    } for lang in languages]


def language_for_name(name, languages):
    ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    matches = [lang for lang in languages if lang.extension.lower() == ext]
    if not matches:
        return ''
    matches.sort(key=lambda lang: PREFERRED.index(lang.key) if lang.key in PREFERRED else len(PREFERRED))
    return matches[0].key


def json_error(message, status=400):
    return JsonResponse({'ok': False, 'error': message}, status=status)


def read_json(request):
    try:
        return json.loads(request.body or b'{}')
    except ValueError:
        return {}


@login_required
@require_POST
def runner_token(request):
    if not runner_enabled():
        return json_error(_('Code runner is not configured.'), 503)

    data = read_json(request)
    code = data.get('problem')
    live = in_live_contest(request)

    if code:
        try:
            problem = Problem.objects.get(code=code)
        except Problem.DoesNotExist:
            return json_error(_('Problem not found.'), 404)
        if not problem.is_accessible_by(request.user):
            return json_error(_('Problem not found.'), 404)
        if live and not problem.contests.filter(contest_id=request.participation.contest_id).exists():
            return json_error(_('During the contest you can only run code for contest problems.'), 403)
        languages = list(problem.allowed_languages.values_list('key', flat=True))
        time_limit = problem.time_limit
        memory_limit = problem.memory_limit
    else:
        if live:
            return json_error(_('The sandbox is closed during the contest.'), 403)
        languages = [lang.key for lang in available_languages()]
        time_limit = None
        memory_limit = None

    token, expires = make_token(request.user.id, languages, time_limit, memory_limit)
    return JsonResponse({'ok': True, 'token': token, 'expires': expires, 'url': public_url()})


@login_required
def workspace(request):
    if in_live_contest(request):
        return generic_message(request, _('Sandbox is unavailable'),
                               _('The sandbox is closed while you are taking part in a contest. '
                                 'Use the editor on the problem page.'))
    languages = available_languages()
    return render(request, 'workspace/index.html', {
        'title': _('Sandbox'),
        'languages_json': json.dumps(editor_language_info(languages)),
        'runner_enabled': runner_enabled(),
        'limits': {'files': MAX_FILES_PER_USER, 'size': MAX_FILE_SIZE},
    })


def shared_file(request, key):
    file = get_object_or_404(WorkspaceFile.objects.select_related('owner__user'), share_key=key, is_folder=False)
    languages = available_languages()
    return render(request, 'workspace/shared.html', {
        'title': file.name,
        'file': file,
        'file_json': json.dumps(file.as_dict(with_content=True)),
        'languages_json': json.dumps(editor_language_info(languages)),
    })


def workspace_api(view):
    """Login, no contest in progress, JSON in and out."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if in_live_contest(request):
            return json_error(_('The sandbox is closed during the contest.'), 403)
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper


def get_own(request, file_id, folder=None):
    qs = WorkspaceFile.objects.filter(owner=request.profile)
    if folder is not None:
        qs = qs.filter(is_folder=folder)
    try:
        return qs.get(id=file_id)
    except (WorkspaceFile.DoesNotExist, ValueError, TypeError):
        raise Http404()


def clean_name(name):
    name = (name or '').strip()
    if not NAME_RE.match(name) or name in ('.', '..'):
        return None
    return name


@workspace_api
@require_GET
def api_list(request):
    files = WorkspaceFile.objects.filter(owner=request.profile).defer('content', 'stdin')
    return JsonResponse({'ok': True, 'files': [f.as_dict() for f in files]})


@workspace_api
@require_GET
def api_get(request, file_id):
    return JsonResponse({'ok': True, 'file': get_own(request, file_id).as_dict(with_content=True)})


@workspace_api
@require_POST
def api_create(request):
    data = read_json(request)
    name = clean_name(data.get('name'))
    if name is None:
        return json_error(_('Invalid name.'))
    parent = None
    if data.get('parent'):
        parent = get_own(request, data['parent'], folder=True)
        if parent.depth() + 1 >= MAX_DEPTH:
            return json_error(_('Folders are nested too deep.'))
    if WorkspaceFile.objects.filter(owner=request.profile).count() >= MAX_FILES_PER_USER:
        return json_error(_('You have too many files. Delete some first.'))

    is_folder = bool(data.get('folder'))
    language = ''
    content = ''
    if not is_folder:
        languages = available_languages()
        language = data.get('language') or language_for_name(name, languages)
        if language not in {lang.key for lang in languages}:
            language = language_for_name(name, languages)
        template = next((lang.template for lang in languages if lang.key == language), '')
        content = data.get('content') if isinstance(data.get('content'), str) else template
        if len(content.encode()) > MAX_FILE_SIZE:
            return json_error(_('The file is larger than 64 KB.'))
    try:
        with transaction.atomic():
            file = WorkspaceFile.objects.create(owner=request.profile, parent=parent, name=name, is_folder=is_folder,
                                                language=language, content=content)
    except IntegrityError:
        return json_error(_('A file with this name already exists here.'))
    return JsonResponse({'ok': True, 'file': file.as_dict(with_content=True)})


@workspace_api
@require_POST
def api_save(request, file_id):
    file = get_own(request, file_id, folder=False)
    data = read_json(request)
    fields = []
    if isinstance(data.get('content'), str):
        if len(data['content'].encode()) > MAX_FILE_SIZE:
            return json_error(_('The file is larger than 64 KB.'))
        file.content = data['content']
        fields.append('content')
    if isinstance(data.get('stdin'), str):
        if len(data['stdin'].encode()) > MAX_FILE_SIZE:
            return json_error(_('The input is larger than 64 KB.'))
        file.stdin = data['stdin']
        fields.append('stdin')
    if isinstance(data.get('language'), str):
        if data['language'] in {lang.key for lang in available_languages()}:
            file.language = data['language']
            fields.append('language')
    if fields:
        file.save(update_fields=fields + ['modified'])
    return JsonResponse({'ok': True, 'file': file.as_dict()})


@workspace_api
@require_POST
def api_rename(request, file_id):
    file = get_own(request, file_id)
    name = clean_name(read_json(request).get('name'))
    if name is None:
        return json_error(_('Invalid name.'))
    file.name = name
    fields = ['name', 'modified']
    if not file.is_folder:
        new_language = language_for_name(name, available_languages())
        if new_language:
            file.language = new_language
            fields.append('language')
    try:
        with transaction.atomic():
            file.save(update_fields=fields)
    except IntegrityError:
        return json_error(_('A file with this name already exists here.'))
    return JsonResponse({'ok': True, 'file': file.as_dict()})


@workspace_api
@require_POST
def api_move(request, file_id):
    file = get_own(request, file_id)
    target = read_json(request).get('parent')
    parent = get_own(request, target, folder=True) if target else None
    if parent is not None:
        if file.is_folder and parent.is_inside(file):
            return json_error(_('A folder cannot be moved into itself.'))
        if parent.depth() + 1 >= MAX_DEPTH:
            return json_error(_('Folders are nested too deep.'))
    file.parent = parent
    try:
        with transaction.atomic():
            file.save(update_fields=['parent', 'modified'])
    except IntegrityError:
        return json_error(_('A file with this name already exists here.'))
    return JsonResponse({'ok': True, 'file': file.as_dict()})


@workspace_api
@require_POST
def api_delete(request, file_id):
    get_own(request, file_id).delete()
    return JsonResponse({'ok': True})


@workspace_api
@require_POST
def api_share(request, file_id):
    file = get_own(request, file_id, folder=False)
    if read_json(request).get('on', True):
        file.make_share_key()
    else:
        file.share_key = None
    file.save(update_fields=['share_key'])
    return JsonResponse({'ok': True, 'file': file.as_dict(with_content=True)})


@workspace_api
@require_POST
def api_fork(request, key):
    try:
        source = WorkspaceFile.objects.get(share_key=key, is_folder=False)
    except ObjectDoesNotExist:
        raise Http404()
    if WorkspaceFile.objects.filter(owner=request.profile).count() >= MAX_FILES_PER_USER:
        return json_error(_('You have too many files. Delete some first.'))
    base, dot, ext = source.name.rpartition('.')
    if not dot:
        base, ext = source.name, ''
    for i in range(0, 100):
        name = source.name if i == 0 else '%s (%d)%s%s' % (base, i, dot, ext)
        try:
            with transaction.atomic():
                file = WorkspaceFile.objects.create(owner=request.profile, name=name[:100], language=source.language,
                                                    content=source.content, stdin=source.stdin)
            return JsonResponse({'ok': True, 'file': file.as_dict()})
        except IntegrityError:
            continue
    return json_error(_('A file with this name already exists here.'))
