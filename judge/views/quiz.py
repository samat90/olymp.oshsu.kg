"""Quiz section: catalog, launching games, joining by PIN, the game itself (HTTP polling), reports."""
import functools
import json
import logging
import secrets
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Max, Q
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.middleware.csrf import CsrfViewMiddleware
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from judge.models import GameSession, Quiz, QuizAnswer, QuizPlayer, QuizQuestion, QuizReport
from judge.utils import quiz_game as engine
from judge.utils.quiz_game import GameError

logger = logging.getLogger('judge.quiz')
COOKIE_SALT = 'quiz-player'
GUEST_COOKIE = 'qz_guest'
CATALOG_PAGE = 24


def player_cookie(pin):
    return 'qz_%s' % pin


def short_circuit(view):
    """Hot polling views skip all middleware; errors become JSON (the HTML error page needs the middleware)."""
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except Exception:
            logger.exception('quiz API error')
            return JsonResponse({'error': 'Ошибка сервера'}, status=500)
    wrapper.short_circuit_middleware = True
    return wrapper


def json_error(message, status=400):
    return JsonResponse({'error': message}, status=status)


def client_ip(request):
    return request.META.get('REMOTE_ADDR', '')


def cookie_ids(request, pin):
    """(game id, player id) from the signed player cookie, or None. No database."""
    try:
        value = request.get_signed_cookie(player_cookie(pin), salt=COOKIE_SALT)
        game_id, player_id = (int(x) for x in value.split(':'))
    except (KeyError, ValueError, TypeError, signing.BadSignature):
        return None
    return game_id, player_id


def current_player_id(request, state):
    """The player id from the signed cookie, checked against this game."""
    ids = cookie_ids(request, state['pin'])
    return ids[1] if ids and ids[0] == state['id'] else None


def set_player_cookie(response, game, player):
    response.set_signed_cookie(player_cookie(game.pin), '%d:%d' % (game.id, player.id), salt=COOKIE_SALT,
                               max_age=12 * 3600, httponly=True, samesite='Lax',
                               secure=getattr(settings, 'SESSION_COOKIE_SECURE', False))


def is_host(request, state):
    if not request.user.is_authenticated:
        return False
    host_key = engine.k('host', state['id'])
    host_id = cache.get(host_key)
    if host_id is None:
        host_id = GameSession.objects.filter(id=state['id']).values_list('host_id', flat=True).first() or 0
        cache.set(host_key, host_id, engine.TTL)
    return host_id == request.profile.id or request.user.is_superuser


# ---------------------------------------------------------------- catalog and quiz pages

def visible_quizzes():
    return Quiz.objects.filter(access=Quiz.PUBLIC, is_hidden=False, is_deleted=False) \
        .annotate(question_count=Count('questions')) \
        .filter(question_count__gt=0).select_related('author__user')


def catalog(request):
    quizzes = visible_quizzes()
    query = request.GET.get('q', '').strip()[:100]
    subject = request.GET.get('subject', '').strip()[:60]
    if query:
        quizzes = quizzes.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                 Q(subject__icontains=query))
    if subject:
        quizzes = quizzes.filter(subject__iexact=subject)
    order = request.GET.get('order')
    quizzes = quizzes.order_by('-plays', '-updated') if order == 'popular' else quizzes.order_by('-updated')
    page = Paginator(quizzes, CATALOG_PAGE).get_page(request.GET.get('page'))
    subjects = cache.get('qz:subjects')
    if subjects is None:
        subjects = list(visible_quizzes().exclude(subject='').values('subject').annotate(c=Count('id'))
                        .order_by('-c').values_list('subject', flat=True)[:20])
        cache.set('qz:subjects', subjects, 300)
    return render(request, 'quiz/catalog.html', {
        'title': 'Викторина', 'page': page, 'query': query, 'subject': subject, 'subjects': subjects,
        'order': order or 'new', 'disabled': engine.games_disabled(),
    })


@login_required
def my_quizzes(request):
    profile = request.profile
    quizzes = Quiz.objects.filter(author=profile, is_deleted=False).annotate(question_count=Count('questions')) \
        .order_by('-updated')
    hosted = GameSession.objects.filter(host=profile).select_related('quiz') \
        .annotate(player_count=Count('players')).order_by('-created')[:30]
    played = QuizPlayer.objects.filter(profile=profile).select_related('game__quiz') \
        .order_by('-joined')[:30]
    return render(request, 'quiz/my.html', {
        'title': 'Мои викторины', 'quizzes': quizzes, 'hosted': hosted, 'played': played,
    })


def get_quiz(request, key):
    quiz = get_object_or_404(Quiz.objects.select_related('author__user'), key=key)
    if not quiz.can_view(request.user):
        raise Http404()
    return quiz


def quiz_records(quiz, limit=20):
    """Best solo results: one row per user or guest nickname."""
    rows = QuizPlayer.objects.filter(game__quiz=quiz, game__mode=GameSession.SOLO,
                                     game__status=GameSession.FINISHED, is_removed=False)
    best = list(rows.values('profile', 'nickname').annotate(best=Max('score')).order_by('-best')[:limit])
    return [{'place': place, 'nickname': b['nickname'], 'score': b['best'], 'is_user': b['profile'] is not None}
            for place, b in enumerate(best, 1)]


def quiz_detail(request, key):
    quiz = get_quiz(request, key)
    questions = list(quiz.questions.all())
    records = cache.get('qz:records:%d' % quiz.id)
    if records is None:
        records = quiz_records(quiz)
        cache.set('qz:records:%d' % quiz.id, records, 60)
    return render(request, 'quiz/detail.html', {
        'title': quiz.title, 'quiz': quiz, 'questions': questions, 'records': records,
        'can_edit': quiz.can_edit(request.user), 'modes': GameSession.MODES,
        'type_names': dict(QuizQuestion.TYPES), 'disabled': engine.games_disabled(),
        'max_players': GameSession.MAX_PLAYERS,
    })


@login_required
@require_POST
def launch(request, key):
    """Create a hosted game from the launch form and go to the host screen."""
    quiz = get_quiz(request, key)
    disabled = engine.games_disabled()
    if disabled and not request.user.is_superuser:
        return render(request, 'quiz/message.html', {'title': 'Викторина', 'message': disabled}, status=403)
    mode = request.POST.get('mode')
    if mode not in (GameSession.HOST_SCREEN, GameSession.HOST_REMOTE, GameSession.AUTO):
        mode = GameSession.HOST_SCREEN
    options = {
        'shuffle_questions': request.POST.get('shuffle_questions') == 'on',
        'shuffle_answers': request.POST.get('shuffle_answers') == 'on',
        'music': request.POST.get('music', 'on') == 'on',
        'guests': request.POST.get('guests', 'on') == 'on',
    }
    try:
        game = engine.create_game(quiz, request.profile, mode, options)
    except GameError as e:
        return render(request, 'quiz/message.html', {'title': quiz.title, 'message': str(e)}, status=400)
    return redirect('quiz_host', pin=game.pin)


def solo(request, key):
    """Play alone: a game with one player that moves on when the player is ready."""
    quiz = get_quiz(request, key)
    if request.method != 'POST':
        return redirect('quiz_detail', key=quiz.key)
    disabled = engine.games_disabled()
    if disabled and not request.user.is_superuser:
        return render(request, 'quiz/message.html', {'title': 'Викторина', 'message': disabled}, status=403)
    profile = request.profile if request.user.is_authenticated else None
    nickname = profile.user.username if profile else request.POST.get('nickname', '').strip()
    if profile is None and not engine.nickname_ok(' '.join(nickname.split())[:24]):
        return render(request, 'quiz/message.html', {'title': quiz.title, 'message': 'Выберите другой ник'},
                      status=400)
    try:
        game = engine.create_game(quiz, None, GameSession.SOLO)
        state = engine.get_state(game.pin)
        player, _new = engine.join(state, profile, nickname, secrets.token_hex(16), client_ip(request))
    except GameError as e:
        return render(request, 'quiz/message.html', {'title': quiz.title, 'message': str(e)}, status=400)
    response = redirect('quiz_play', pin=game.pin)
    set_player_cookie(response, game, player)
    return response


@require_POST
def complain(request, key):
    quiz = get_quiz(request, key)
    reason = request.POST.get('reason', '').strip()[:1000]
    throttle = 'qz:report:%s' % (request.profile.id if request.user.is_authenticated else client_ip(request))
    if reason and cache.add(throttle, 1, 60):
        QuizReport.objects.create(quiz=quiz, author=request.profile if request.user.is_authenticated else None,
                                  reason=reason)
    return render(request, 'quiz/message.html', {
        'title': quiz.title, 'message': 'Спасибо, жалоба отправлена администраторам.',
        'back': reverse('quiz_detail', args=[quiz.key])})


# ---------------------------------------------------------------- joining

@ensure_csrf_cookie
def join(request):
    """Step 1: PIN (the QR code opens this page with ?pin=). Step 2: nickname for guests."""
    pin = ''.join(ch for ch in (request.POST.get('pin') or request.GET.get('pin') or '') if ch.isdigit())[:6]
    context = {'title': 'Войти в игру', 'pin': pin, 'error': '', 'step': 'pin', 'nickname': ''}
    if not pin or (request.method != 'POST' and not request.GET.get('pin')):
        return render(request, 'quiz/join.html', context)
    state = engine.get_state(pin) if len(pin) == 6 else None
    if state is None or state['mode'] == GameSession.SOLO:
        context['error'] = 'Игра с таким PIN не найдена'
        return render(request, 'quiz/join.html', context, status=404 if request.method == 'POST' else 200)
    player_id = current_player_id(request, state)
    if player_id is not None and not engine.is_kicked(state['id'], player_id):
        return redirect('quiz_play', pin=pin)
    if request.user.is_authenticated:
        nickname = request.user.username
    else:
        nickname = request.POST.get('nickname', '').strip()
        if not nickname:
            context['step'] = 'nick'
            return render(request, 'quiz/join.html', context)
    token = request.COOKIES.get(GUEST_COOKIE, '')
    if len(token) != 32 or not token.isalnum():
        token = secrets.token_hex(16)
    try:
        player, _new = engine.join(state, request.profile if request.user.is_authenticated else None, nickname,
                                   token, client_ip(request))
    except GameError as e:
        context.update(error=str(e), step='nick' if not request.user.is_authenticated else 'pin', nickname=nickname)
        return render(request, 'quiz/join.html', context, status=400)
    game = GameSession.objects.get(id=state['id'])
    response = redirect('quiz_play', pin=pin)
    set_player_cookie(response, game, player)
    if not request.user.is_authenticated:
        response.set_cookie(GUEST_COOKIE, token, max_age=30 * 86400, httponly=True, samesite='Lax',
                            secure=getattr(settings, 'SESSION_COOKIE_SECURE', False))
    return response


def qr_code(request, pin):
    """SVG QR code that opens the join page with this PIN."""
    import qrcode
    import qrcode.image.svg
    url = request.build_absolute_uri(reverse('quiz_join') + '?pin=' + pin)
    image = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1)
    buf = BytesIO()
    image.save(buf)
    response = HttpResponse(buf.getvalue(), content_type='image/svg+xml')
    response['Cache-Control'] = 'public, max-age=3600'
    return response


# ---------------------------------------------------------------- the game pages

def game_page_context(state, game, role):
    return {
        'title': game.quiz.title, 'game': game, 'quiz': game.quiz, 'role': role, 'pin': state['pin'],
        'join_url': reverse('quiz_join'),
        'config': {
            'pin': state['pin'], 'mode': state['mode'], 'role': role, 'theme': game.quiz.theme,
            'title': game.quiz.title, 'music': game.settings.get('music', True),
            'urls': {
                'state': reverse('quiz_state', args=[state['pin']]),
                'question': reverse('quiz_question', args=[state['pin']]),
                'answer': reverse('quiz_answer', args=[state['pin']]),
                'result': reverse('quiz_result', args=[state['pin']]),
                'final': reverse('quiz_final', args=[state['pin']]),
                'next': reverse('quiz_solo_next', args=[state['pin']]),
                'host_state': reverse('quiz_host_state', args=[state['pin']]),
                'host_action': reverse('quiz_host_action', args=[state['pin']]),
                'qr': reverse('quiz_qr', args=[state['pin']]),
                'join': reverse('quiz_join'),
                'report': reverse('quiz_game_report', args=[game.id]),
                'quiz': reverse('quiz_detail', args=[game.quiz.key]),
            },
        },
    }


@ensure_csrf_cookie
def play(request, pin):
    state = engine.get_state(pin)
    if state is None:
        raise Http404()
    player_id = current_player_id(request, state)
    if player_id is None:
        return redirect(reverse('quiz_join') + '?pin=' + pin)
    player = QuizPlayer.objects.filter(id=player_id, game_id=state['id']).first()
    if player is None or player.is_removed:
        response = redirect(reverse('quiz_join') + '?pin=' + pin)
        response.delete_cookie(player_cookie(pin))
        return response
    game = GameSession.objects.select_related('quiz').get(id=state['id'])
    context = game_page_context(state, game, 'player')
    context['player'] = player
    context['config'].update(nickname=player.nickname, player=player.id)
    return render(request, 'quiz/play.html', context)


@login_required
@ensure_csrf_cookie
def host(request, pin):
    state = engine.get_state(pin)
    if state is None or state['mode'] == GameSession.SOLO:
        raise Http404()
    if not is_host(request, state):
        return HttpResponseForbidden('Только ведущий может открыть эту страницу')
    game = GameSession.objects.select_related('quiz').get(id=state['id'])
    view = request.GET.get('view')
    role = 'remote' if view == 'remote' or (view != 'screen' and state['mode'] == GameSession.HOST_REMOTE) \
        else 'screen'
    context = game_page_context(state, game, role)
    context['join_absolute'] = request.build_absolute_uri(reverse('quiz_join'))
    return render(request, 'quiz/host.html', context)


# ---------------------------------------------------------------- polling API (players)

@short_circuit
def state_view(request, pin):
    """GET ?v=N. The hot path: one cache round trip, no middleware, no database. `{}` when nothing changed."""
    ids = cookie_ids(request, pin)
    keys = [engine.k('s', pin)]
    if ids:
        keys += [engine.k('np', ids[0]), engine.k('x', ids[0], ids[1])]
    got = cache.get_many(keys)
    state = got.get(keys[0])
    if state is None:
        state = engine.get_state(pin)
        if state is None:
            return JsonResponse({'error': 'Игра не найдена', 'gone': True}, status=404)
    state = engine.advance_if_due(state)
    player_id = players = None
    if ids and ids[0] == state['id']:
        player_id = ids[1]
        if got.get(keys[2]):
            return JsonResponse({'kicked': True})
        players = got.get(keys[1])
    if request.GET.get('v') == str(state['v']):
        response = JsonResponse({})
    else:
        data = engine.public_state(state, players)
        if request.GET.get('full') != '0':
            engine.with_details(state, data, player_id)
        response = JsonResponse(data)
    response['Cache-Control'] = 'no-store'
    return response


@short_circuit
def question_view(request, pin):
    """The current question without its answer. Records when this player received it."""
    state = cache.get(engine.k('s', pin)) or engine.get_state(pin)
    if state is None:
        return json_error('Игра не найдена', 404)
    if state['ph'] not in (GameSession.QUESTION, GameSession.REVEAL, GameSession.LEADERBOARD) or state['i'] < 0:
        return json_error('Сейчас нет вопроса', 409)
    player_id = current_player_id(request, state)
    payload = engine.get_question(state['id'], state['i'])
    if player_id is not None and state['ph'] == GameSession.QUESTION:
        engine.mark_seen(state['id'], state['i'], player_id)
        payload = dict(payload, answered=cache.get(engine.k('a', state['id'], state['i'], player_id)) is not None)
    response = JsonResponse(payload)
    response['Cache-Control'] = 'no-store'
    return response


def csrf_failed(request):
    """CSRF check for short-circuited views (they skip the middleware)."""
    return CsrfViewMiddleware(lambda r: None).process_view(request, None, (), {})


@short_circuit
def answer_view(request, pin):
    """POST {"i": question number, "value": answer}. Checked and stored at once; the result comes at the reveal."""
    if request.method != 'POST':
        return json_error('POST', 405)
    if csrf_failed(request):
        return json_error('CSRF', 403)
    state = cache.get(engine.k('s', pin)) or engine.get_state(pin)
    if state is None:
        return json_error('Игра не найдена', 404)
    player_id = current_player_id(request, state)
    if player_id is None:
        return json_error('Вы не в этой игре', 403)
    try:
        body = json.loads(request.body or b'{}')
        index = int(body['i'])
        value = body['value']
    except (ValueError, KeyError, TypeError):
        return json_error('Неверный запрос')
    if index != state['i']:
        return json_error('Этот вопрос уже закрыт', 409)
    status, data = engine.submit_answer(state, player_id, value)
    return JsonResponse(data, status=status)


@short_circuit
def result_view(request, pin):
    """After the reveal: the correct answer, statistics and this player's result."""
    state = cache.get(engine.k('s', pin)) or engine.get_state(pin)
    if state is None:
        return json_error('Игра не найдена', 404)
    if state['ph'] not in (GameSession.REVEAL, GameSession.LEADERBOARD, GameSession.FINISHED) or state['i'] < 0:
        return json_error('Разбор ещё не начался', 409)
    data = {'reveal': engine.reveal_data(state['id'], state['i']), 'me': None,
            'leaderboard': engine.leaderboard_data(state['id'])}
    player_id = current_player_id(request, state)
    if player_id is not None:
        data['me'] = engine.my_result(state['id'], player_id)
    response = JsonResponse(data)
    response['Cache-Control'] = 'no-store'
    return response


@short_circuit
def final_view(request, pin):
    """The podium, the leaderboard and this player's answers with the right ones (prepared at the finish)."""
    state = cache.get(engine.k('s', pin)) or engine.get_state(pin)
    if state is None or state['ph'] != GameSession.FINISHED:
        return json_error('Игра ещё идёт', 409)
    return JsonResponse(engine.final_data(state['id'], current_player_id(request, state)))


@short_circuit
def solo_next(request, pin):
    """Solo game: the player moves on when ready."""
    if request.method != 'POST':
        return json_error('POST', 405)
    if csrf_failed(request):
        return json_error('CSRF', 403)
    state = engine.get_state(pin)
    if state is None or state['mode'] != GameSession.SOLO:
        return json_error('Игра не найдена', 404)
    if current_player_id(request, state) is None:
        return json_error('Вы не в этой игре', 403)
    try:
        state = engine.next_step(pin)
    except GameError as e:
        return json_error(str(e), 409)
    return JsonResponse(engine.with_details(state, engine.public_state(state), current_player_id(request, state)))


# ---------------------------------------------------------------- host API

def host_state(request, pin):
    """Everything the host screen needs, polled every second: state, counts, the players in the lobby."""
    state = engine.get_state(pin)
    if state is None:
        return json_error('Игра не найдена', 404)
    if not is_host(request, state):
        return json_error('Только ведущий', 403)
    state = engine.advance_if_due(state)
    data = engine.public_state(state)
    data['players'] = engine.player_count(state['id'])
    data['answered'] = engine.answered_count(state['id'], state['i']) if state['i'] >= 0 else 0
    since = int(request.GET.get('since') or 0) if (request.GET.get('since') or '0').isdigit() else 0
    if state['ph'] == GameSession.LOBBY or request.GET.get('list'):
        rows = QuizPlayer.objects.filter(game_id=state['id'], is_removed=False, id__gt=since) \
            .order_by('id').values('id', 'nickname')[:300]
        data['joined'] = list(rows)
    if request.GET.get('v') == str(state['v']):
        data['same'] = True
    else:
        if state['i'] >= 0 and state['ph'] != GameSession.LOBBY:
            data['question'] = engine.get_question(state['id'], state['i'])
            key = engine.get_key(state['id'], state['i'])
            data['key'] = {'correct': key.get('correct'), 'answers': key.get('answers'), 'word': key.get('word'),
                           'answer': key.get('answer'), 'x': key.get('x'), 'y': key.get('y'), 'r': key.get('r')}
        if state['ph'] in (GameSession.REVEAL, GameSession.LEADERBOARD, GameSession.FINISHED):
            data['reveal'] = engine.reveal_data(state['id'], state['i'])
            data['leaderboard'] = engine.leaderboard_data(state['id'])
    response = JsonResponse(data)
    response['Cache-Control'] = 'no-store'
    return response


@require_POST
def host_action(request, pin):
    """POST action=start|next|skip|pause|resume|end|kick (player=id)|hide (answer=id)."""
    state = engine.get_state(pin)
    if state is None:
        return json_error('Игра не найдена', 404)
    if not is_host(request, state):
        return json_error('Только ведущий', 403)
    action = request.POST.get('action')
    try:
        if action == 'start':
            state = engine.start(pin)
        elif action == 'next':
            state = engine.next_step(pin)
        elif action == 'skip':
            state = engine.skip(pin)
        elif action in ('pause', 'resume'):
            state = engine.pause(pin, action == 'pause')
        elif action == 'end':
            state = engine.end_game(pin)
        elif action == 'kick':
            engine.remove_player(state, int(request.POST.get('player', 0)))
        else:
            return json_error('Неизвестное действие')
    except (GameError, ValueError) as e:
        return json_error(str(e), 409)
    return JsonResponse(engine.public_state(state))


# ---------------------------------------------------------------- reports for the host

def game_for_report(request, game_id):
    game = get_object_or_404(GameSession.objects.select_related('quiz'), id=game_id)
    if not request.user.is_authenticated or not (game.host_id == request.profile.id or request.user.is_superuser or
                                                 game.quiz.author_id == request.profile.id):
        raise Http404()
    return game


class SnapshotQuestion:
    """A question deleted after the game, as it was at the start."""
    is_deleted = True

    def __init__(self, qid, data):
        self.id = qid
        self.type = data.get('type', '')
        self.text = data.get('text', '')
        self.scored = data.get('scored', True)
        self.type_name = data.get('type_name', '')

    def get_type_display(self):
        return '%s (удалён)' % self.type_name


def report_rows(game):
    questions = {q.id: q for q in QuizQuestion.objects.filter(id__in=game.question_ids)}
    snapshot = game.snapshot or {}
    ordered = []
    for qid in game.question_ids:
        if qid in questions:
            ordered.append(questions[qid])
        elif str(qid) in snapshot:
            ordered.append(SnapshotQuestion(qid, snapshot[str(qid)]))
    players = list(QuizPlayer.objects.filter(game=game).order_by('is_removed', '-score', 'joined'))
    answers = {}
    for a in QuizAnswer.objects.filter(player__game=game):
        answers[(a.player_id, a.question_key)] = a
    stats = []
    for number, q in enumerate(ordered, 1):
        given = [answers[(p.id, q.id)] for p in players if (p.id, q.id) in answers]
        stats.append({'n': number, 'question': q, 'answered': len(given),
                      'correct': sum(1 for a in given if a.is_correct),
                      'avg_ms': int(sum(a.time_ms for a in given) / len(given)) if given else 0})
    return ordered, players, answers, stats


@login_required
def game_report(request, game_id):
    game = game_for_report(request, game_id)
    questions, players, answers, stats = report_rows(game)
    table = [{'player': p, 'cells': [answers.get((p.id, q.id)) for q in questions]} for p in players]
    return render(request, 'quiz/report.html', {
        'title': 'Отчёт: %s' % game.quiz.title, 'game': game, 'questions': questions, 'table': table,
        'stats': stats,
    })


@login_required
def game_report_xlsx(request, game_id):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    game = game_for_report(request, game_id)
    questions, players, answers, stats = report_rows(game)
    book = Workbook()
    sheet = book.active
    sheet.title = 'Игроки'
    sheet.append(['Место', 'Ник', 'Пользователь', 'Очки', 'Верных'] +
                 ['В%d' % n for n in range(1, len(questions) + 1)])
    for place, p in enumerate(players, 1):
        row = [p.rank or place, p.nickname, p.profile.user.username if p.profile_id else '', p.score, p.correct]
        for q in questions:
            a = answers.get((p.id, q.id))
            row.append('' if a is None else a.points)
        sheet.append(row)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    green = PatternFill('solid', fgColor='C8EED9')
    red = PatternFill('solid', fgColor='F8D0D6')
    for r, p in enumerate(players, 2):
        for c, q in enumerate(questions, 6):
            a = answers.get((p.id, q.id))
            if a is not None and q.scored:
                sheet.cell(row=r, column=c).fill = green if a.is_correct else red
    second = book.create_sheet('Вопросы')
    second.append(['№', 'Тип', 'Вопрос', 'Ответили', 'Верно', '% верных', 'Среднее время, с'])
    for s in stats:
        q = s['question']
        second.append([s['n'], q.get_type_display(), q.text[:200], s['answered'], s['correct'],
                       round(100 * s['correct'] / s['answered']) if s['answered'] else 0, round(s['avg_ms'] / 1000, 1)])
    for cell in second[1]:
        cell.font = Font(bold=True)
    buf = BytesIO()
    book.save(buf)
    response = HttpResponse(buf.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="quiz-%d.xlsx"' % game.id
    return response


def records(request, key):
    quiz = get_quiz(request, key)
    return render(request, 'quiz/records.html', {'title': 'Рекорды: %s' % quiz.title, 'quiz': quiz,
                                                 'records': quiz_records(quiz, 100)})


@never_cache
def pin_lookup(request):
    """Short JSON check for the join form: does a game with this PIN exist?"""
    pin = request.GET.get('pin', '')
    state = engine.get_state(pin) if len(pin) == 6 and pin.isdigit() else None
    return JsonResponse({'ok': state is not None and state['mode'] != GameSession.SOLO})
