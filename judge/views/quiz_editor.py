"""Quiz editor: creating, editing, copying and deleting quizzes; a JSON API for the editor page."""
import copy
import json
import logging
import random
import secrets
import threading
from functools import wraps
from types import SimpleNamespace

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import close_old_connections, transaction
from django.db.models import Max
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy as _l
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from judge.models import Quiz, QuizOption, QuizQuestion
from judge.utils import quiz_ai, quiz_images as images
from judge.utils.quiz_images import ImageError
from judge.utils.quiz_import import LANGUAGES, MAX_QUESTIONS, QuestionError, clean_question, problems, read_rows, \
    template_bytes

MAX_QUIZZES = 50
KEY_ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'
RESERVED_KEYS = {'my', 'join', 'new', 'qr', 'g', 'game', 'import-template', 'edit', 'api', 'copy', 'delete',
                 'launch', 'solo', 'records', 'complain', 'static', 'admin', 'ai'}
NEW_TITLE = 'Новая викторина'


def choices(pairs):
    """Model choices with their labels in the current language, ready for JSON."""
    return [(value, str(label)) for value, label in pairs]


TYPE_INFO = {
    QuizQuestion.SINGLE: ('fa-dot-circle-o', _l('Один верный из 2–4')),
    QuizQuestion.TRUEFALSE: ('fa-adjust', _l('Утверждение: верно или нет')),
    QuizQuestion.MULTI: ('fa-check-square-o', _l('Несколько верных из 2–6')),
    QuizQuestion.WORD: ('fa-font', _l('Собрать слово из букв')),
    QuizQuestion.ORDER: ('fa-sort-amount-asc', _l('Расставить 3–6 пунктов')),
    QuizQuestion.CODE: ('fa-code', _l('Код: варианты или ввод')),
    QuizQuestion.TEXT: ('fa-keyboard-o', _l('Ввести ответ с клавиатуры')),
    QuizQuestion.SLIDER: ('fa-sliders', _l('Число на шкале')),
    QuizQuestion.PIN: ('fa-map-marker', _l('Отметить место на картинке')),
    QuizQuestion.POLL: ('fa-bar-chart', _l('Мнение, без очков')),
    QuizQuestion.CLOUD: ('fa-cloud', _l('Облако слов, без очков')),
    QuizQuestion.OPEN: ('fa-comment-o', _l('Свободный ответ, без очков')),
}
DEFAULTS = {
    QuizQuestion.SINGLE: ({}, 4), QuizQuestion.MULTI: ({}, 4), QuizQuestion.ORDER: ({}, 4),
    QuizQuestion.POLL: ({}, 3), QuizQuestion.CODE: ({'input': False}, 4), QuizQuestion.TRUEFALSE: ({}, 2),
    QuizQuestion.WORD: ({'word': ''}, 0), QuizQuestion.TEXT: ({'answers': [], 'tolerance': 0}, 0),
    QuizQuestion.SLIDER: ({'min': 0, 'max': 100, 'step': 1, 'answer': 50, 'tolerance': 5, 'unit': ''}, 0),
    QuizQuestion.PIN: ({'x': 50, 'y': 50, 'r': 10}, 0), QuizQuestion.CLOUD: ({}, 0), QuizQuestion.OPEN: ({}, 0),
}


def new_key():
    while True:
        key = ''.join(secrets.choice(KEY_ALPHABET) for _ in range(8))
        if key not in RESERVED_KEYS and not Quiz.objects.filter(key=key).exists():
            return key


def json_error(message, status=400, field=''):
    return JsonResponse({'error': message, 'field': field}, status=status)


def touch(quiz):
    Quiz.objects.filter(id=quiz.id).update(updated=timezone.now())


def quiz_limit_reached(request):
    return not request.user.is_superuser and \
        Quiz.objects.filter(author=request.profile, is_deleted=False).count() >= MAX_QUIZZES


def message(request, text, status=400, back=None):
    return render(request, 'quiz/message.html', {'title': _('Викторина'), 'message': text,
                                                 'back': back or reverse('quiz_my')}, status=status)


# ---------------------------------------------------------------- serialisation

def image_url(field):
    return field.url if field else ''


def question_fields(question):
    return {'type': question.type, 'text': question.text, 'code': question.code, 'data': question.data or {}}


def option_dict(option):
    return {'id': option.id, 'text': option.text, 'image': image_url(option.image), 'is_correct': option.is_correct}


def question_dict(question):
    options = list(question.options.all())
    plain = [{'text': o.text, 'is_correct': o.is_correct, 'has_image': bool(o.image)} for o in options]
    return {
        'id': question.id, 'order': question.order, 'type': question.type, 'text': question.text,
        'code': question.code, 'code_language': question.code_language, 'image': image_url(question.image),
        'time_limit': question.time_limit, 'weight': question.weight, 'explanation': question.explanation,
        'data': question.data or {}, 'options': [option_dict(o) for o in options],
        'problems': problems(question_fields(question), plain, bool(question.image)),
    }


def quiz_dict(quiz):
    return {'key': quiz.key, 'title': quiz.title, 'description': quiz.description, 'subject': quiz.subject,
            'theme': quiz.theme, 'access': quiz.access, 'cover': image_url(quiz.cover), 'is_hidden': quiz.is_hidden,
            'plays': quiz.plays}


def questions_of(quiz):
    return list(quiz.questions.prefetch_related('options'))


def renumber(quiz):
    for order, question_id in enumerate(quiz.questions.order_by('order', 'id').values_list('id', flat=True)):
        QuizQuestion.objects.filter(id=question_id).exclude(order=order).update(order=order)


# ---------------------------------------------------------------- pages

@login_required
def new_quiz(request):
    """Create an empty quiz and open its editor. An untouched empty draft is reused instead of making another."""
    recent = Quiz.objects.filter(author=request.profile, title__in={NEW_TITLE, _(NEW_TITLE)}, questions__isnull=True,
                                 is_deleted=False).order_by('-created').first()
    if recent is not None:
        return redirect('quiz_edit', key=recent.key)
    if quiz_limit_reached(request):
        return message(request, _('У вас уже %d викторин. Удалите ненужные, чтобы создать новую.') % MAX_QUIZZES)
    quiz = Quiz.objects.create(author=request.profile, title=_(NEW_TITLE), key=new_key())
    return redirect('quiz_edit', key=quiz.key)


def own_quiz(request, key):
    quiz = get_object_or_404(Quiz, key=key)
    if not quiz.can_edit(request.user):
        if quiz.can_view(request.user):
            raise PermissionDenied()
        raise Http404()
    return quiz


@login_required
@ensure_csrf_cookie
def edit(request, key):
    quiz = own_quiz(request, key)
    api = reverse('quiz_api_data', args=[quiz.key])
    config = {
        'quiz': quiz_dict(quiz), 'questions': [question_dict(q) for q in questions_of(quiz)],
        'types': [{'code': code, 'name': str(name), 'icon': TYPE_INFO[code][0], 'hint': str(TYPE_INFO[code][1]),
                   'scored': code not in QuizQuestion.UNSCORED} for code, name in QuizQuestion.TYPES],
        'languages': LANGUAGES, 'themes': choices(Quiz.THEMES), 'access': choices(Quiz.ACCESS),
        'weights': choices(QuizQuestion.WEIGHTS),
        'maxQuestions': MAX_QUESTIONS,
        'urls': {'api': api, 'play': reverse('quiz_detail', args=[quiz.key]),
                 'template': reverse('quiz_import_template'), 'delete': reverse('quiz_delete', args=[quiz.key]),
                 'my': reverse('quiz_my')},
    }
    return render(request, 'quiz/editor.html', {'title': _('Редактор: %s') % quiz.title, 'quiz': quiz,
                                                'config': config})


@login_required
@require_POST
def copy_quiz(request, key):
    source = get_object_or_404(Quiz, key=key, is_deleted=False)
    own = source.can_edit(request.user)
    if not own and (source.is_hidden or source.access != Quiz.PUBLIC):
        raise Http404()
    if quiz_limit_reached(request):
        return message(request, _('У вас уже %d викторин. Удалите ненужные, чтобы скопировать.') % MAX_QUIZZES)
    with transaction.atomic():
        quiz = Quiz.objects.create(
            author=request.profile, title=(_('Копия: %s') % source.title)[:120], description=source.description,
            subject=source.subject, theme=source.theme, access=Quiz.PUBLIC, key=new_key(), copied_from=source,
            cover=images.copy_file(source.cover))
        for question in questions_of(source):
            copy_question(question, quiz, question.order)
    return redirect('quiz_edit', key=quiz.key)


@login_required
@require_POST
def delete_quiz(request, key):
    quiz = own_quiz(request, key)
    if quiz.games.exists():
        # Games were played: their reports keep the quiz; it only disappears from the site.
        Quiz.objects.filter(id=quiz.id).update(is_deleted=True)
    else:
        quiz.delete()
    return redirect('quiz_my')


def import_template(request):
    response = HttpResponse(template_bytes(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="quiz-template.xlsx"'
    return response


# ---------------------------------------------------------------- JSON API

def editor_api(method):
    """Login, method and author checks for the editor API; editor errors become JSON with status 400."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, key, *args, **kwargs):
            if not request.user.is_authenticated:
                return json_error(_('Войдите на сайт'), 403)
            if request.method != method:
                return json_error(method, 405)
            quiz = Quiz.objects.filter(key=key).first()
            if quiz is None or not quiz.can_edit(request.user):
                return json_error(_('Нет доступа к этой викторине'), 404)
            try:
                return view(request, quiz, *args, **kwargs)
            except QuestionError as e:
                return json_error(str(e), field=e.field)
            except ImageError as e:
                return json_error(str(e), field='image')
            except Http404:
                return json_error(_('Вопрос не найден'), 404)
        return wrapper
    return decorator


def read_json(request):
    try:
        body = json.loads(request.body or b'{}')
    except ValueError:
        raise QuestionError(_('Неверный запрос'))
    if not isinstance(body, dict):
        raise QuestionError(_('Неверный запрос'))
    return body


def get_question(quiz, question_id):
    question = QuizQuestion.objects.filter(quiz=quiz, id=question_id).prefetch_related('options').first()
    if question is None:
        raise Http404()
    return question


@editor_api('GET')
def api_data(request, quiz):
    return JsonResponse({'quiz': quiz_dict(quiz), 'questions': [question_dict(q) for q in questions_of(quiz)]})


@editor_api('POST')
def api_settings(request, quiz):
    """{title, description, subject, theme, access} → {quiz}"""
    body = read_json(request)
    title = ' '.join(str(body.get('title', quiz.title)).split())
    if not title:
        raise QuestionError(_('Введите название'), 'title')
    if len(title) > 120:
        raise QuestionError(_('Название: не больше 120 символов'), 'title')
    description = str(body.get('description', quiz.description)).replace('\r\n', '\n').strip()
    if len(description) > 2000:
        raise QuestionError(_('Описание: не больше 2000 символов'), 'description')
    subject = ' '.join(str(body.get('subject', quiz.subject)).split())
    if len(subject) > 60:
        raise QuestionError(_('Предмет: не больше 60 символов'), 'subject')
    theme = body.get('theme', quiz.theme)
    if theme not in dict(Quiz.THEMES):
        raise QuestionError(_('Неизвестная тема'), 'theme')
    access = body.get('access', quiz.access)
    if access not in dict(Quiz.ACCESS):
        raise QuestionError(_('Неверный доступ'), 'access')
    quiz.title, quiz.description, quiz.subject, quiz.theme, quiz.access = title, description, subject, theme, access
    quiz.save()
    return JsonResponse({'quiz': quiz_dict(quiz)})


@editor_api('POST')
def api_cover(request, quiz):
    """multipart: image=<file> or remove=1 → {quiz}"""
    if request.POST.get('remove'):
        images.clear(quiz, 'cover')
    else:
        images.store(quiz, 'cover', request.FILES.get('image'))
    return JsonResponse({'quiz': quiz_dict(quiz)})


def save_options(question, options):
    existing = {o.id: o for o in question.options.all()}
    for order, item in enumerate(options):
        option = existing.pop(item['id'], None) if item['id'] else None
        if option is None:
            option = QuizOption(question=question)
        option.order, option.text, option.is_correct = order, item['text'], item['is_correct']
        if question.type == QuizQuestion.TRUEFALSE and option.image:
            images.delete_file(option.image)
            option.image = ''
        option.save()
    for option in existing.values():
        option.delete()


@editor_api('POST')
def api_question_add(request, quiz):
    """{type, after: question id or null} → {question, order: [ids]}"""
    body = read_json(request)
    type = body.get('type')
    if type not in DEFAULTS:
        raise QuestionError(_('Неизвестный тип вопроса'), 'type')
    if quiz.questions.count() >= MAX_QUESTIONS:
        raise QuestionError(_('Не больше %d вопросов в викторине') % MAX_QUESTIONS)
    data, option_count = DEFAULTS[type]
    with transaction.atomic():
        order = new_position(quiz, body.get('after'))
        question = QuizQuestion.objects.create(
            quiz=quiz, order=order, type=type, data=copy.deepcopy(data),
            code_language='python' if type == QuizQuestion.CODE else '',
            time_limit=60 if type == QuizQuestion.OPEN else 30 if type == QuizQuestion.CODE else 20)
        if type == QuizQuestion.TRUEFALSE:
            QuizOption.objects.bulk_create([QuizOption(question=question, order=0, text='Верно', is_correct=True),
                                            QuizOption(question=question, order=1, text='Неверно')])
        else:
            QuizOption.objects.bulk_create([QuizOption(question=question, order=i) for i in range(option_count)])
        renumber(quiz)
    touch(quiz)
    return JsonResponse({'question': question_dict(get_question(quiz, question.id)), 'order': order_ids(quiz)})


def new_position(quiz, after):
    """Order for a question put after the question `after` (or at the end); later ones move down."""
    target = quiz.questions.filter(id=after).values_list('order', flat=True).first() if after else None
    if target is None:
        return (quiz.questions.aggregate(m=Max('order'))['m'] or 0) + 1
    for question in quiz.questions.filter(order__gt=target).order_by('-order'):
        QuizQuestion.objects.filter(id=question.id).update(order=question.order + 1)
    return target + 1


def order_ids(quiz):
    return list(quiz.questions.order_by('order', 'id').values_list('id', flat=True))


@editor_api('POST')
def api_question_save(request, quiz, question_id):
    """The whole question: {type, text, code, code_language, time_limit, weight, explanation, data,
    options: [{id|null, text, is_correct}]} → {question} (normalised, with new option ids and problems)."""
    question = get_question(quiz, question_id)
    fields, options = clean_question(read_json(request))
    with transaction.atomic():
        for name, value in fields.items():
            setattr(question, name, value)
        question.save()
        save_options(question, options)
    touch(quiz)
    return JsonResponse({'question': question_dict(get_question(quiz, question.id))})


@editor_api('POST')
def api_question_delete(request, quiz, question_id):
    question = get_question(quiz, question_id)
    with transaction.atomic():
        question.delete()
        renumber(quiz)
    touch(quiz)
    return JsonResponse({'ok': True, 'order': order_ids(quiz)})


def copy_question(source, quiz, order):
    question = QuizQuestion.objects.create(
        quiz=quiz, order=order, type=source.type, text=source.text, code=source.code,
        code_language=source.code_language, time_limit=source.time_limit, weight=source.weight,
        explanation=source.explanation, data=copy.deepcopy(source.data), image=images.copy_file(source.image))
    QuizOption.objects.bulk_create([
        QuizOption(question=question, order=o.order, text=o.text, is_correct=o.is_correct,
                   image=images.copy_file(o.image)) for o in source.options.all()])
    return question


@editor_api('POST')
def api_question_duplicate(request, quiz, question_id):
    source = get_question(quiz, question_id)
    if quiz.questions.count() >= MAX_QUESTIONS:
        raise QuestionError(_('Не больше %d вопросов в викторине') % MAX_QUESTIONS)
    with transaction.atomic():
        question = copy_question(source, quiz, new_position(quiz, source.id))
        renumber(quiz)
    touch(quiz)
    return JsonResponse({'question': question_dict(get_question(quiz, question.id)), 'order': order_ids(quiz)})


@editor_api('POST')
def api_question_image(request, quiz, question_id):
    """multipart: image=<file> or remove=1, option=<option id> for an option picture → {question}"""
    question = get_question(quiz, question_id)
    target, field = question, 'image'
    if request.POST.get('option'):
        try:
            target = question.options.get(id=int(request.POST['option']))
        except (ValueError, QuizOption.DoesNotExist):
            return json_error(_('Вариант не найден'), 404)
        if question.type == QuizQuestion.TRUEFALSE:
            raise ImageError(_('У вариантов «Верно / Неверно» нет картинок'))
    if request.POST.get('remove'):
        images.clear(target, field)
    else:
        images.store(target, field, request.FILES.get('image'))
    touch(quiz)
    return JsonResponse({'question': question_dict(get_question(quiz, question.id))})


@editor_api('POST')
def api_reorder(request, quiz):
    """{ids: [all question ids in the new order]} → {order}"""
    ids = read_json(request).get('ids')
    current = order_ids(quiz)
    if not isinstance(ids, list) or sorted(map(str, ids)) != sorted(map(str, current)) or len(set(ids)) != len(ids):
        raise QuestionError(_('Список вопросов устарел, обновите страницу'))
    with transaction.atomic():
        for order, question_id in enumerate(ids):
            QuizQuestion.objects.filter(quiz=quiz, id=question_id).update(order=order)
    touch(quiz)
    return JsonResponse({'order': order_ids(quiz)})


@editor_api('GET')
def api_question_preview(request, quiz, question_id):
    """The question exactly as the game sends it to a phone (shuffled options, rendered markdown)."""
    from judge.utils.quiz_game import question_payload

    question = get_question(quiz, question_id)
    ids = order_ids(quiz)
    game = SimpleNamespace(id=0, settings={}, question_ids=ids)
    payload = question_payload(game, question, ids.index(question.id))
    return JsonResponse({'question': payload, 'theme': quiz.theme})


@editor_api('POST')
def api_import(request, quiz):
    """multipart: file=<xlsx> → {added, errors: [{row, error}], questions: [...]}"""
    upload = request.FILES.get('file')
    if upload is None:
        raise QuestionError(_('Выберите файл'))
    rows = read_rows(upload)
    room = MAX_QUESTIONS - quiz.questions.count()
    added, errors = 0, []
    with transaction.atomic():
        order = (quiz.questions.aggregate(m=Max('order'))['m'] or 0) + 1
        for row, result in rows:
            if isinstance(result, QuestionError):
                errors.append({'row': row, 'error': str(result)})
                continue
            if added >= room:
                errors.append({'row': row, 'error': _('Не больше %d вопросов в викторине') % MAX_QUESTIONS})
                continue
            fields, options = result
            question = QuizQuestion.objects.create(quiz=quiz, order=order, **fields)
            QuizOption.objects.bulk_create([QuizOption(question=question, order=i, text=o['text'],
                                                       is_correct=o['is_correct']) for i, o in enumerate(options)])
            order += 1
            added += 1
        renumber(quiz)
    if added:
        touch(quiz)
    return JsonResponse({'added': added, 'errors': errors,
                         'questions': [question_dict(q) for q in questions_of(quiz)]})


# ---------------------------------------------------------------- quizzes written by AI

logger = logging.getLogger('judge.quiz_ai')
AI_LEVELS = ('easy', 'medium', 'hard')
AI_LANGUAGES = ('ru', 'ky', 'en')
AI_COUNTS = (5, 10, 15, 20, 25, 30)
AI_ERRORS = {
    'failed': _l('ИИ сейчас не отвечает. Попробуйте ещё раз через минуту.'),
    'limit': _l('Лимит на сегодня исчерпан, попробуйте завтра.'),
    'lost': _l('Генерация прервалась. Попробуйте ещё раз.'),
}


def ai_limit(name, misc_key, default):
    try:
        return int(quiz_ai.config(name, misc_key, str(default)))
    except ValueError:
        return default


def ai_take_quota(request):
    """Count one generation for the user and the site today; False when a daily limit is reached."""
    day = timezone.localdate().isoformat()
    keys = [('qz:ai:site:' + day, ai_limit('QUIZ_AI_SITE_LIMIT', 'ai_site_limit', 200))]
    if not request.user.is_superuser:
        keys.append(('qz:ai:user:%d:%s' % (request.profile.id, day),
                     ai_limit('QUIZ_AI_USER_LIMIT', 'ai_user_limit', 10)))
    for key, limit in keys:
        cache.add(key, 0, 2 * 86400)
        if cache.get(key, 0) >= limit:
            return False
    for key, _limit in keys:
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, 2 * 86400)
    return True


def save_ai_quiz(profile_id, result):
    with transaction.atomic():
        quiz = Quiz.objects.create(
            author_id=profile_id, title=result['title'] or _(NEW_TITLE), description=result['description'],
            subject=result['subject'], theme=random.choice([code for code, _name in Quiz.THEMES]),
            access=Quiz.LINK, key=new_key())
        for order, (fields, options) in enumerate(result['questions']):
            question = QuizQuestion.objects.create(quiz=quiz, order=order, **fields)
            QuizOption.objects.bulk_create([QuizOption(question=question, order=i, text=o['text'],
                                                       is_correct=o['is_correct']) for i, o in enumerate(options)])
    return quiz


def run_ai_job(job, profile_id, params):
    """Runs in a thread: the request has already answered, the page asks ai_status every few seconds."""
    key = 'qz:ai:job:' + job
    close_old_connections()
    try:
        quiz = save_ai_quiz(profile_id, quiz_ai.generate(**params))
        cache.set(key, {'profile': profile_id, 'status': 'done', 'key': quiz.key}, 3600)
    except quiz_ai.AIError:
        cache.set(key, {'profile': profile_id, 'status': 'error', 'error': 'failed'}, 3600)
    except Exception:
        logger.exception('quiz AI job failed')
        cache.set(key, {'profile': profile_id, 'status': 'error', 'error': 'failed'}, 3600)
    finally:
        cache.delete('qz:ai:busy:%d' % profile_id)
        close_old_connections()


@login_required
@require_POST
def ai_start(request):
    """{topic, details, count, language, level} → {job}; the quiz is written in the background."""
    try:
        body = read_json(request)
    except QuestionError as e:
        return json_error(str(e))
    topic = ' '.join(str(body.get('topic') or '').split())[:200]
    details = str(body.get('details') or '').strip()[:1000]
    if not topic:
        return json_error(_('Напишите тему'), field='topic')
    try:
        count = int(body.get('count') or 10)
    except (TypeError, ValueError):
        count = 10
    count = min(AI_COUNTS, key=lambda c: abs(c - count))
    language = body.get('language') if body.get('language') in AI_LANGUAGES else 'ru'
    level = body.get('level') if body.get('level') in AI_LEVELS else 'medium'
    if not quiz_ai.is_configured():
        return json_error(_('ИИ пока не подключён. Обратитесь к администратору.'), 503)
    if quiz_limit_reached(request):
        return json_error(_('У вас уже %d викторин. Удалите ненужные, чтобы создать новую.') % MAX_QUIZZES)
    busy = 'qz:ai:busy:%d' % request.profile.id
    if not cache.add(busy, 1, 300):
        return json_error(_('Предыдущая викторина ещё создаётся, подождите.'), 429)
    if not ai_take_quota(request):
        cache.delete(busy)
        return json_error(str(AI_ERRORS['limit']), 429)
    job = secrets.token_urlsafe(12)
    cache.set('qz:ai:job:' + job, {'profile': request.profile.id, 'status': 'running'}, 3600)
    params = {'topic': topic, 'details': details, 'count': count, 'language': language, 'level': level}
    threading.Thread(target=run_ai_job, args=(job, request.profile.id, params), daemon=True).start()
    return JsonResponse({'job': job, 'status': reverse('quiz_ai_status', args=[job])})


@login_required
def ai_status(request, job):
    state = cache.get('qz:ai:job:' + job)
    if not state or state.get('profile') != request.profile.id:
        return JsonResponse({'status': 'error', 'error': str(AI_ERRORS['lost'])})
    if state['status'] == 'done':
        return JsonResponse({'status': 'done', 'url': reverse('quiz_edit', args=[state['key']])})
    if state['status'] == 'error':
        return JsonResponse({'status': 'error', 'error': str(AI_ERRORS.get(state.get('error'), AI_ERRORS['failed']))})
    return JsonResponse({'status': 'running'})
