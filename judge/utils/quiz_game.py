"""Live quiz games: the game state lives in the cache, answers and results in the database.

Players poll a tiny state record (phase, question number, version, times) that is read from the
cache only. When the version changes they fetch the question or their result, also from the cache.
Phase changes are made by the host's buttons or, when a timer runs out, by the first request that
notices it (guarded by a cache lock), so no background worker is needed.

Cache keys (G = game id):
    qz:s:<pin>            state dict (see new_state)
    qz:np:G               number of players in the game
    qz:na:G:i             number of answers to question i
    qz:q:G:i / qz:k:G:i   question for players (no correct answer) / answer key for checking
    qz:seen:G:i:P         when player P received question i
    qz:a:G:i:P            player P has answered question i
    qz:me:G:P             player P's last result, score, place and streak
    qz:r:G:i              reveal data: correct answer, statistics, explanation
    qz:lb:G               leaderboard (top players)
    qz:x:G:P              player P was removed by the host
"""
import random
import secrets
import time
from collections import Counter
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from judge.jinja2.markdown import markdown
from judge.models.interface import MiscConfig
from judge.models.quiz import Answer, GameSession, Player, Question, Quiz
from judge.utils import quiz_scoring as scoring

TTL = 6 * 3600
COUNTDOWN = 3            # seconds of "get ready" before answers open
GRACE = 1.5              # answers sent in time but delivered late (network, busy server) still count
AUTO_REVEAL = 7          # automatic mode: seconds on the reveal and on the leaderboard
AUTO_BOARD = 6
LEADERBOARD_SIZE = 10
OPEN_SHOWN = 60
MAX_PLAYERS = GameSession.MAX_PLAYERS
JOINS_PER_IP = getattr(settings, 'QUIZ_JOINS_PER_IP', 1500)   # per 10 minutes; classrooms share one IP


class GameError(Exception):
    pass


def k(*parts):
    return 'qz:' + ':'.join(str(p) for p in parts)


def now():
    return time.time()


def poll_interval(players):
    if players <= 200:
        return 1000
    if players <= 500:
        return 1500
    return 2000


def games_disabled():
    """Admins can stop new games for a while (an olympiad): misc config `quiz_disabled`."""
    value = cache.get('qz:disabled')
    if value is None:
        value = MiscConfig.objects.filter(key='quiz_disabled').values_list('value', flat=True).first() or ''
        cache.set('qz:disabled', value, 30)
    return value.strip()


# ---------------------------------------------------------------- creating games

def new_pin():
    for _attempt in range(50):
        pin = '%06d' % random.SystemRandom().randint(100000, 999999)
        # Games left unfinished for half a day no longer hold their PIN.
        recent = GameSession.objects.filter(pin=pin, created__gte=timezone.now() - timedelta(hours=12))
        if not recent.exclude(status=GameSession.FINISHED).exists() and cache.get(k('s', pin)) is None:
            return pin
    raise GameError('Не удалось подобрать PIN, попробуйте ещё раз')


def create_game(quiz, host, mode, options=None):
    options = options or {}
    questions = list(quiz.questions.values_list('id', flat=True))
    if not questions:
        raise GameError('В викторине нет вопросов')
    broken = unfinished_questions(quiz)
    if broken:
        raise GameError('Не готовы вопросы %s: допишите их в редакторе' % ', '.join(map(str, broken)))
    if options.get('shuffle_questions'):
        random.shuffle(questions)
    game_settings = {
        'shuffle_answers': bool(options.get('shuffle_answers')),
        'shuffle_questions': bool(options.get('shuffle_questions')),
        'music': options.get('music', True) is not False,
        'guests': options.get('guests', True) is not False,
        'max_players': min(int(options.get('max_players') or MAX_PLAYERS), MAX_PLAYERS),
    }
    if mode == GameSession.SOLO:
        game_settings['max_players'] = 1
    game = GameSession.objects.create(quiz=quiz, host=host if mode != GameSession.SOLO else None, pin=new_pin(),
                                      mode=mode, settings=game_settings, question_ids=questions,
                                      snapshot=snapshot(quiz))
    cache.set(k('s', game.pin), new_state(game), TTL)
    cache.set(k('np', game.id), 0, TTL)
    return game


def snapshot(quiz):
    """The questions as they were at the start, for reports after a question is edited or deleted."""
    data = {}
    for q in quiz.questions.prefetch_related('options'):
        data[str(q.id)] = {'type': q.type, 'type_name': q.get_type_display(), 'text': q.text[:500],
                           'scored': q.scored, 'correct': correct_text(q),
                           'options': {str(o.id): o.text or 'картинка %d' % (n + 1)
                                       for n, o in enumerate(q.options.all())}}
    return data


def unfinished_questions(quiz):
    """Numbers of questions that cannot be played yet (no right answer, empty option, pin without picture...)."""
    from judge.utils.quiz_import import problems
    broken = []
    for number, q in enumerate(quiz.questions.prefetch_related('options'), 1):
        options = [{'text': o.text, 'is_correct': o.is_correct, 'has_image': bool(o.image)} for o in q.options.all()]
        fields = {'type': q.type, 'text': q.text, 'code': q.code, 'data': q.data or {}}
        if problems(fields, options, bool(q.image)):
            broken.append(number)
    return broken


def new_state(game):
    return {'id': game.id, 'pin': game.pin, 'mode': game.mode, 'ph': game.status, 'i': game.current,
            'n': len(game.question_ids), 'v': 1, 'ts': now(), 'start': 0, 'end': 0, 'paused': None,
            'music': game.settings.get('music', True), 'theme': game.quiz.theme}


def get_state(pin):
    """The state from the cache; rebuilt from the database only if the cache lost it."""
    state = cache.get(k('s', pin))
    if state is not None:
        return state
    game = GameSession.objects.filter(pin=pin, created__gte=timezone.now() - timedelta(hours=12)) \
        .exclude(status=GameSession.FINISHED).select_related('quiz').order_by('-created').first()
    if game is None:
        game = GameSession.objects.filter(pin=pin, finished__gte=timezone.now() - timedelta(hours=6)) \
            .select_related('quiz').order_by('-created').first()
        if game is None:
            return None
    state = new_state(game)
    state['v'] = 1000 + int(now()) % 100000   # newer than anything clients have seen
    if game.status == GameSession.QUESTION:
        # The timer is lost with the cache: close the question now.
        state['ph'] = GameSession.QUESTION
        state['start'] = state['end'] = now() - 1
    cache.set(k('s', pin), state, TTL)
    if cache.get(k('np', game.id)) is None:
        cache.set(k('np', game.id), game.players.filter(is_removed=False).count(), TTL)
    if game.current >= 0:
        prepare_question(game, game.current)
    return state


def save_state(state, keep_ts=False):
    state['v'] += 1
    if not keep_ts:
        state['ts'] = now()
    cache.set(k('s', state['pin']), state, TTL)
    return state


def with_details(state, data, player_id):
    """On a version change the player gets what the new phase needs in the same response:
    the question (stamped as received) or the results, so 1000 phones make one request, not two."""
    ph, index, game_id = state['ph'], state['i'], state['id']
    if ph == GameSession.QUESTION and index >= 0:
        question = get_question(game_id, index)
        if player_id is not None:
            mark_seen(game_id, index, player_id)
            question = dict(question, answered=cache.get(k('a', game_id, index, player_id)) is not None)
        data['question'] = question
    elif ph in (GameSession.REVEAL, GameSession.LEADERBOARD) and index >= 0:
        data['result'] = {'reveal': reveal_data(game_id, index), 'leaderboard': leaderboard_data(game_id),
                          'me': my_result(game_id, player_id) if player_id is not None else None}
    elif ph == GameSession.FINISHED:
        data['final'] = final_data(game_id, player_id)
    return data


def player_count(game_id):
    return cache.get(k('np', game_id)) or 0


def public_state(state, players=None):
    """What every player polls. No database queries."""
    if players is None:
        players = player_count(state['id'])
    return {'v': state['v'], 'ph': state['ph'], 'i': state['i'], 'n': state['n'], 'now': round(now(), 3),
            'start': state['start'], 'end': state['end'], 'paused': state['paused'], 'mode': state['mode'],
            'poll': poll_interval(players)}


# ---------------------------------------------------------------- the lock around phase changes

class phase_lock:
    def __init__(self, game_id):
        self.key = k('lock', game_id)

    def __enter__(self):
        for _attempt in range(40):
            if cache.add(self.key, 1, 30):
                return self
            time.sleep(0.05)
        raise GameError('Игра занята, попробуйте ещё раз')

    def __exit__(self, *exc):
        cache.delete(self.key)


def fresh_state(pin):
    state = cache.get(k('s', pin))
    if state is None:
        state = get_state(pin)
    if state is None:
        raise GameError('Игра не найдена')
    return state


def load_game(state):
    return GameSession.objects.select_related('quiz').get(id=state['id'])


# ---------------------------------------------------------------- questions

def shuffled(items, seed):
    items = list(items)
    random.Random(seed).shuffle(items)
    return items


def image_url(field):
    return field.url if field else ''


def question_payload(game, question, index):
    data = question.data or {}
    options = list(question.options.all())
    seed = '%d:%d' % (game.id, question.id)
    t = question.type
    if t == Question.ORDER or (game.settings.get('shuffle_answers') and t in (Question.SINGLE, Question.MULTI,
                                                                              Question.CODE)):
        options = shuffled(options, seed)
        if t == Question.ORDER and len(options) > 1 and [o.id for o in options] == \
                [o.id for o in question.options.all()]:
            options = options[1:] + options[:1]
    payload = {
        'i': index, 'n': len(game.question_ids), 'id': question.id, 'type': t, 'type_name': question.get_type_display(),
        'text': str(markdown(question.text, 'comment')) if question.text else '',
        'code': question.code, 'lang': question.code_language, 'image': image_url(question.image),
        'time': question.time_limit, 'weight': question.weight, 'scored': question.scored,
        'options': [{'id': o.id, 'text': o.text, 'image': image_url(o.image)} for o in options],
    }
    if t == Question.WORD:
        letters = list(scoring.normalize_text(data.get('word', '')).replace(' ', '').upper())
        mixed = shuffled(letters, seed)
        if len(letters) > 1 and mixed == letters:
            mixed = mixed[1:] + mixed[:1]
        payload['letters'] = mixed
        payload['options'] = []
    elif t in (Question.TEXT, Question.CLOUD, Question.OPEN) or (t == Question.CODE and data.get('input')):
        payload['input'] = True
        payload['options'] = []
    elif t == Question.SLIDER:
        payload['slider'] = {'min': data.get('min', 0), 'max': data.get('max', 100), 'step': data.get('step', 1),
                             'unit': data.get('unit', '')}
        payload['options'] = []
    elif t == Question.PIN:
        payload['options'] = []
    return payload


def prepare_question(game, index):
    question = Question.objects.prefetch_related('options').get(id=game.question_ids[index])
    payload = question_payload(game, question, index)
    key = scoring.build_key(question)
    cache.set_many({k('q', game.id, index): payload, k('k', game.id, index): key}, TTL)
    return payload, key


def get_question(game_id, index):
    payload = cache.get(k('q', game_id, index))
    if payload is None:
        game = GameSession.objects.select_related('quiz').get(id=game_id)
        payload, _key = prepare_question(game, index)
    return payload


def get_key(game_id, index):
    key = cache.get(k('k', game_id, index))
    if key is None:
        game = GameSession.objects.select_related('quiz').get(id=game_id)
        _payload, key = prepare_question(game, index)
    return key


def mark_seen(game_id, index, player_id):
    cache.add(k('seen', game_id, index, player_id), now(), TTL)


# ---------------------------------------------------------------- phase changes

def start(pin):
    with phase_lock_for(pin) as state:
        if state['ph'] != GameSession.LOBBY:
            return state
        if state['mode'] != GameSession.SOLO and player_count(state['id']) == 0:
            raise GameError('Пока нет ни одного игрока')
        return open_question(state, 0)


class phase_lock_for:
    """Lock the game by PIN and give the current state."""

    def __init__(self, pin):
        self.pin = pin

    def __enter__(self):
        state = fresh_state(self.pin)
        self.lock = phase_lock(state['id'])
        self.lock.__enter__()
        return fresh_state(self.pin)

    def __exit__(self, *exc):
        self.lock.__exit__(*exc)


def open_question(state, index):
    game = load_game(state)
    payload, key = prepare_question(game, index)
    opened = now() + COUNTDOWN
    state.update({'ph': GameSession.QUESTION, 'i': index, 'start': round(opened, 3),
                  'end': round(opened + key['time'], 3), 'paused': None})
    cache.set(k('na', game.id, index), 0, TTL)
    GameSession.objects.filter(id=game.id).update(status=GameSession.QUESTION, current=index,
                                                  phase_started=timezone.now())
    return save_state(state)


def close_question(state):
    """Question -> reveal: count everyone's points, places and statistics."""
    game = load_game(state)
    index = state['i']
    key = get_key(game.id, index)
    question = Question.objects.prefetch_related('options').get(id=key['id'])
    answers = {a.player_id: a for a in Answer.objects.filter(player__game=game, question_key=key['id'])}
    players = list(Player.objects.filter(game=game, is_removed=False))
    old_rank = {p.id: p.rank for p in players}
    is_scored = scoring.scored(key)
    for p in players:
        a = answers.get(p.id)
        if a is not None:
            p.score += a.points
            if a.is_correct:
                p.correct += 1
        if is_scored:
            p.streak = p.streak + 1 if a is not None and a.is_correct else 0
    players.sort(key=lambda p: (-p.score, p.joined))
    for place, p in enumerate(players, 1):
        p.rank = place
    with transaction.atomic():
        Player.objects.bulk_update(players, ['score', 'streak', 'correct', 'rank'], batch_size=500)
        GameSession.objects.filter(id=game.id).update(status=GameSession.REVEAL, phase_started=timezone.now())

    total = len(players)
    results = {}
    for p in players:
        a = answers.get(p.id)
        results[k('me', game.id, p.id)] = {
            'i': index, 'answered': a is not None, 'correct': bool(a and a.is_correct),
            'fraction': round(a.fraction, 3) if a else 0, 'points': a.points if a else 0,
            'score': p.score, 'rank': p.rank, 'total': total, 'streak': p.streak, 'scored': is_scored,
            'value': a.value if a else None,
        }
    cache.set_many(results, TTL)
    cache.set(k('r', game.id, index), reveal_payload(question, key, list(answers.values()), len(players)), TTL)
    cache.set(k('lb', game.id), leaderboard(players, old_rank, answers), TTL)
    state.update({'ph': GameSession.REVEAL, 'paused': None})
    return save_state(state)


def reveal_payload(question, key, answers, players):
    t = question.type
    data = question.data or {}
    payload = {'i': None, 'type': t, 'answered': len(answers), 'players': players,
               'correct_count': sum(1 for a in answers if a.is_correct),
               'explanation': str(markdown(question.explanation, 'comment')) if question.explanation else ''}
    if t in (Question.SINGLE, Question.TRUEFALSE, Question.MULTI, Question.POLL, Question.CODE) and key['options'] \
            and not key.get('input'):
        counts = Counter()
        for a in answers:
            for option in (a.value if isinstance(a.value, list) else [a.value]):
                counts[option] += 1
        payload['counts'] = {str(o): counts.get(o, 0) for o in key['options']}
        payload['correct'] = key['correct'] if t != Question.POLL else []
    elif t == Question.ORDER:
        payload['correct'] = key['correct']
    elif t == Question.WORD:
        payload['correct'] = scoring.normalize_text(data.get('word', '')).upper()
    elif t in (Question.TEXT, Question.CODE):
        payload['correct'] = [str(a) for a in data.get('answers', [])]
        payload['top'] = Counter(scoring.normalize_text(a.value) for a in answers if a.value).most_common(8)
    elif t == Question.SLIDER:
        payload['correct'] = key['answer']
        payload['tolerance'] = key['tolerance']
        values = sorted(a.value for a in answers if isinstance(a.value, (int, float)))
        payload['values'] = values[:MAX_PLAYERS]
    elif t == Question.PIN:
        payload['correct'] = {'x': key['x'], 'y': key['y'], 'r': key['r']}
        payload['points'] = [a.value for a in answers if isinstance(a.value, dict)][:300]
    elif t == Question.CLOUD:
        payload['words'] = Counter(scoring.normalize_text(a.value) for a in answers if a.value).most_common(50)
    elif t == Question.OPEN:
        payload['texts'] = [{'id': a.id, 'text': a.value} for a in answers if a.value][:OPEN_SHOWN]
    return payload


def leaderboard(players, old_rank, answers):
    top = []
    for p in players[:LEADERBOARD_SIZE]:
        a = answers.get(p.id)
        top.append({'id': p.id, 'nick': p.nickname, 'score': p.score, 'rank': p.rank,
                    'prev': old_rank.get(p.id), 'delta': a.points if a else 0, 'streak': p.streak})
    return {'top': top, 'total': len(players)}


def show_leaderboard(state):
    GameSession.objects.filter(id=state['id']).update(status=GameSession.LEADERBOARD, phase_started=timezone.now())
    state.update({'ph': GameSession.LEADERBOARD, 'paused': None})
    return save_state(state)


def finish(state):
    game = load_game(state)
    players = list(Player.objects.filter(game=game, is_removed=False).order_by('-score', 'joined'))
    for place, p in enumerate(players, 1):
        p.rank = place
    with transaction.atomic():
        Player.objects.bulk_update(players, ['rank'], batch_size=500)
        GameSession.objects.filter(id=game.id).update(status=GameSession.FINISHED, finished=timezone.now(),
                                                      phase_started=timezone.now())
        Quiz.objects.filter(id=game.quiz_id).update(plays=F('plays') + 1)
    cache.set(k('lb', game.id), leaderboard(players, {}, {}), TTL)
    prepare_finals(game, players)
    state.update({'ph': GameSession.FINISHED, 'paused': None})
    return save_state(state)


def prepare_finals(game, players):
    """Everyone's final screen at once (two queries), so the last poll of 1000 phones reads only the cache."""
    questions = {q.id: q for q in Question.objects.filter(id__in=game.question_ids).prefetch_related('options')}
    ordered = [(n, questions[qid]) for n, qid in enumerate(game.question_ids, 1) if qid in questions]
    answers = {}
    for a in Answer.objects.filter(player__game=game):
        answers[(a.player_id, a.question_key)] = a
    cache.set(k('final', game.id), {
        'top': [{'id': p.id, 'nickname': p.nickname, 'score': p.score, 'correct': p.correct, 'rank': p.rank}
                for p in players[:10]],
        'total': len(players), 'questions': len(game.question_ids)}, TTL)
    correct = {q.id: correct_text(q) for _n, q in ordered}
    mine = {}
    for p in players:
        mistakes = []
        for n, q in ordered:
            if not q.scored:
                continue
            a = answers.get((p.id, q.id))
            if a is not None and a.is_correct:
                continue
            mistakes.append({'n': n, 'text': q.text[:300], 'type': q.type,
                             'given': answer_text(q, a.value) if a else None,
                             'correct': correct[q.id], 'explanation': q.explanation[:500]})
        mine[k('fin', game.id, p.id)] = {
            'me': {'nickname': p.nickname, 'score': p.score, 'correct': p.correct, 'rank': p.rank},
            'mistakes': mistakes}
    cache.set_many(mine, TTL)


def final_data(game_id, player_id):
    data = cache.get(k('final', game_id))
    if data is None or (player_id is not None and cache.get(k('fin', game_id, player_id)) is None):
        game = GameSession.objects.get(id=game_id)
        prepare_finals(game, list(Player.objects.filter(game=game, is_removed=False).order_by('-score', 'joined')))
        data = cache.get(k('final', game_id))
    mine = cache.get(k('fin', game_id, player_id)) if player_id is not None else None
    return dict(data, **(mine or {'me': None, 'mistakes': []}))


def answer_text(question, value):
    options = {o.id: o.text or 'картинка %d' % (n + 1) for n, o in enumerate(question.options.all())}
    if isinstance(value, list):
        return ', '.join(options.get(v, '?') for v in value)
    if isinstance(value, dict):
        return '(%s; %s)' % (value.get('x'), value.get('y'))
    if isinstance(value, int) and question.type in (Question.SINGLE, Question.TRUEFALSE,
                                                    Question.CODE, Question.POLL):
        return options.get(value, '?')
    return str(value)


def correct_text(question):
    data = question.data or {}
    options = list(question.options.all())
    t = question.type
    if t == Question.ORDER:
        return ' → '.join(o.text for o in options)
    if t == Question.WORD:
        return str(data.get('word', '')).upper()
    if t == Question.TEXT or (t == Question.CODE and data.get('input')):
        return ' / '.join(str(a) for a in data.get('answers', []))
    if t == Question.SLIDER:
        return str(data.get('answer', ''))
    if t == Question.PIN:
        return 'отмеченная область на картинке'
    return ', '.join(o.text or 'картинка %d' % (n + 1) for n, o in enumerate(options) if o.is_correct)


def next_step(pin):
    """The host's "Next": reveal -> leaderboard -> next question -> ... -> finished."""
    with phase_lock_for(pin) as state:
        ph = state['ph']
        if ph == GameSession.LOBBY:
            if state['mode'] != GameSession.SOLO and player_count(state['id']) == 0:
                raise GameError('Пока нет ни одного игрока')
            return open_question(state, 0)
        if ph == GameSession.QUESTION:
            return close_question(state)
        if ph == GameSession.REVEAL and state['mode'] != GameSession.SOLO:
            return show_leaderboard(state)
        if ph in (GameSession.REVEAL, GameSession.LEADERBOARD):
            if state['i'] + 1 < state['n']:
                return open_question(state, state['i'] + 1)
            return finish(state)
        return state


def skip(pin):
    """Close the current question right away (the answers given so far count)."""
    with phase_lock_for(pin) as state:
        if state['ph'] == GameSession.QUESTION:
            return close_question(state)
        return state


def end_game(pin):
    with phase_lock_for(pin) as state:
        if state['ph'] == GameSession.QUESTION:
            close_question(state)
        if state['ph'] != GameSession.FINISHED:
            return finish(state)
        return state


def pause(pin, on):
    with phase_lock_for(pin) as state:
        t = now()
        if on and state['paused'] is None:
            state['paused'] = {'at': round(t, 3)}
        elif not on and state['paused'] is not None:
            shift = t - state['paused']['at']
            if state['ph'] == GameSession.QUESTION:
                state['start'] = round(state['start'] + shift, 3)
                state['end'] = round(state['end'] + shift, 3)
            state['ts'] += shift
            state['paused'] = None
        else:
            return state
        return save_state(state, keep_ts=True)


def advance_if_due(state):
    """Called on every poll: move on when a timer ran out. Cheap when nothing is due."""
    if state['paused'] is not None:
        return state
    t = now()
    ph = state['ph']
    due = (ph == GameSession.QUESTION and t > state['end'] + GRACE) or \
          (state['mode'] == GameSession.AUTO and ((ph == GameSession.REVEAL and t > state['ts'] + AUTO_REVEAL) or
                                                  (ph == GameSession.LEADERBOARD and t > state['ts'] + AUTO_BOARD)))
    if not due:
        return state
    # Only one request does the work; the others keep showing the current phase for a moment.
    if not cache.add(k('due', state['id'], state['v']), 1, 60):
        return state
    try:
        with phase_lock(state['id']):
            current = fresh_state(state['pin'])
            if current['v'] != state['v']:
                return current
            if ph == GameSession.QUESTION:
                return close_question(current)
            if ph == GameSession.REVEAL:
                return show_leaderboard(current)
            if current['i'] + 1 < current['n']:
                return open_question(current, current['i'] + 1)
            return finish(current)
    except GameError:
        return state


# ---------------------------------------------------------------- players

def nickname_ok(nick):
    from judge.utils.quiz_words import is_rude
    return 1 <= len(nick) <= 24 and not is_rude(nick)


def join(state, profile, nickname, token, ip):
    """A Player for this user or guest; the same one again on reconnect."""
    game_id = state['id']
    game = GameSession.objects.get(id=game_id)
    if profile is not None:
        player = Player.objects.filter(game_id=game_id, profile=profile).first()
    else:
        player = Player.objects.filter(game_id=game_id, token=token).first() if token else None
    if player is not None:
        if player.is_removed:
            raise GameError('Ведущий удалил вас из игры')
        return player, False
    if state['ph'] == GameSession.FINISHED:
        raise GameError('Игра уже закончилась')
    if profile is None and not game.settings.get('guests', True):
        raise GameError('В эту игру можно войти только с аккаунтом')
    ip_key = k('ip', ip)
    cache.add(ip_key, 0, 600)
    try:
        if cache.incr(ip_key) > JOINS_PER_IP:
            raise GameError('Слишком много входов с этого адреса, подождите')
    except ValueError:
        pass
    nickname = ' '.join(nickname.split())[:24]
    if not nickname_ok(nickname):
        raise GameError('Выберите другой ник')
    limit = game.settings.get('max_players', MAX_PLAYERS)
    count_key = k('np', game_id)
    cache.add(count_key, Player.objects.filter(game_id=game_id, is_removed=False).count(), TTL)
    if cache.incr(count_key) > limit:
        cache.decr(count_key)
        raise GameError('В игре уже %d игроков, это максимум' % limit)
    if Player.objects.filter(game_id=game_id, nickname__iexact=nickname, is_removed=False).exists():
        cache.decr(count_key)
        raise GameError('Этот ник уже занят')
    try:
        player = Player.objects.create(game_id=game_id, profile=profile, nickname=nickname,
                                       token='' if profile is not None else (token or secrets.token_hex(16)))
    except IntegrityError:
        cache.decr(count_key)
        raise GameError('Не получилось войти, попробуйте ещё раз')
    return player, True


def remove_player(state, player_id):
    updated = Player.objects.filter(game_id=state['id'], id=player_id, is_removed=False).update(is_removed=True)
    if updated:
        cache.set(k('x', state['id'], player_id), 1, TTL)
        try:
            cache.decr(k('np', state['id']))
        except ValueError:
            pass
        current = cache.get(k('s', state['pin'])) or state
        if current['ph'] == GameSession.QUESTION:
            index = current['i']
            if cache.get(k('a', current['id'], index, player_id)):
                try:
                    cache.decr(k('na', current['id'], index))
                except ValueError:
                    pass
            if answered_count(current['id'], index) >= player_count(current['id']) > 0:
                # The removed player was the last one we were waiting for.
                try:
                    with phase_lock(current['id']):
                        latest = fresh_state(current['pin'])
                        if latest['ph'] == GameSession.QUESTION and latest['i'] == index:
                            close_question(latest)
                except GameError:
                    pass
    return bool(updated)


def is_kicked(game_id, player_id):
    return bool(cache.get(k('x', game_id, player_id)))


def submit_answer(state, player_id, raw_value):
    """Check and store one answer. Returns (http status, response dict)."""
    t = now()
    if state['ph'] != GameSession.QUESTION:
        return 409, {'error': 'Сейчас нельзя отвечать'}
    if t > state['end'] + GRACE:
        return 409, {'error': 'Время вышло'}
    if t < state['start'] - 0.05:
        return 409, {'error': 'Ещё рано'}
    if state['paused'] is not None:
        return 409, {'error': 'Игра на паузе'}
    game_id, index = state['id'], state['i']
    names = {'x': k('x', game_id, player_id), 'key': k('k', game_id, index),
             'seen': k('seen', game_id, index, player_id), 'me': k('me', game_id, player_id)}
    got = cache.get_many(list(names.values()))
    if got.get(names['x']):
        return 403, {'error': 'Вы удалены из игры'}
    key = got.get(names['key']) or get_key(game_id, index)
    value = scoring.clean_value(key, raw_value)
    if value is None:
        return 400, {'error': 'Неверный ответ'}
    if not cache.add(k('a', game_id, index, player_id), 1, TTL):
        return 409, {'error': 'Ответ уже принят'}
    seen = got.get(names['seen']) or state['start']
    # Capped at the time limit: an answer delivered late never earns more than the slowest one in time.
    elapsed = min(max(t - max(seen, state['start']), 0), key['time'])
    fraction, correct = scoring.check(key, value)
    me = got.get(names['me']) or {}
    points = scoring.points(key, fraction, correct, elapsed, me.get('streak', 0))
    try:
        Answer.objects.create(player_id=player_id, question_id=key['id'], question_key=key['id'], value=value,
                              is_correct=correct, fraction=fraction, points=points, time_ms=int(elapsed * 1000))
    except IntegrityError:
        return 409, {'error': 'Ответ уже принят'}
    try:
        answered = cache.incr(k('na', game_id, index))
    except ValueError:
        answered = 1
        cache.set(k('na', game_id, index), 1, TTL)
    if state['mode'] == GameSession.SOLO or answered >= player_count(game_id):
        # Everyone has answered: no need to wait for the timer.
        try:
            with phase_lock(game_id):
                current = fresh_state(state['pin'])
                if current['ph'] == GameSession.QUESTION and current['i'] == index:
                    close_question(current)
        except GameError:
            pass
    return 200, {'ok': True}


def answered_count(game_id, index):
    return cache.get(k('na', game_id, index)) or 0


def my_result(game_id, player_id):
    return cache.get(k('me', game_id, player_id))


def reveal_data(game_id, index):
    data = cache.get(k('r', game_id, index))
    if data is not None:
        data = dict(data, i=index)
    return data


def leaderboard_data(game_id):
    return cache.get(k('lb', game_id)) or {'top': [], 'total': 0}
