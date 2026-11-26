"""Quiz statistics.

A game counts when it is finished and somebody who stayed in it answered at least one question: games
closed in the lobby or finished without a single answer are not plays. A participation is one player of
such a game with at least one answer.

The totals shown in lists are stored on the quiz and recounted from the games themselves (never
incremented), so they stay right after any change and can be rebuilt at any time.
"""
import logging

from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Exists, Max, OuterRef, Q
from django.db.models.signals import post_delete
from django.dispatch import receiver

from judge.models.quiz import Answer, GameSession, Player, Question, Quiz

logger = logging.getLogger('judge.quiz')

DETAIL_TTL = 60


def detail_key(quiz_id):
    return 'qz:stats:%d' % quiz_id


def counted_players(quiz_id, Player=Player, Answer=Answer):
    """The participations of a quiz. The models are parameters for the backfill migration."""
    return Player.objects.filter(
        Exists(Answer.objects.filter(player_id=OuterRef('pk'))),
        game__quiz_id=quiz_id, game__status=GameSession.FINISHED, is_removed=False)


def answers_by_question(players, Answer=Answer):
    """{question id: (answers, correct answers)} over these participations."""
    rows = Answer.objects.filter(player__in=players.values('id')).values('question_key') \
        .annotate(answered=Count('id'), correct=Count('id', filter=Q(is_correct=True)))
    return {row['question_key']: (row['answered'], row['correct']) for row in rows}


def unscored_keys(quiz_id, keys, Answer_=Answer, Question_=Question):
    """The ids among `keys` of polls, word clouds and open questions: their answers are never "correct".
    A question deleted since then is looked up in the snapshots of the games."""
    types = dict(Question_.objects.filter(id__in=keys).values_list('id', 'type'))
    for key in set(keys) - set(types):
        # One game in which it was answered is enough.
        snapshot = Answer_.objects.filter(question_key=key, player__game__quiz_id=quiz_id) \
            .values_list('player__game__snapshot', flat=True).first()
        types[key] = ((snapshot or {}).get(str(key)) or {}).get('type')
    return {key for key, type in types.items() if type in Question.UNSCORED}


def different_players(participations):
    """A user is one player however often they play; a guest is known by the token in their browser."""
    rows = participations.order_by()    # the model's ordering would spoil DISTINCT
    guests = rows.filter(profile__isnull=True)
    return rows.filter(profile__isnull=False).values('profile_id').distinct().count() + \
        guests.exclude(token='').values('token').distinct().count() + guests.filter(token='').count()


def totals(quiz_id, models=None):
    """The stored counters of one quiz, counted from its games."""
    m = models or {'Player': Player, 'Answer': Answer, 'Question': Question}
    players = counted_players(quiz_id, m['Player'], m['Answer'])
    solo = Q(game__mode=GameSession.SOLO)
    games = players.aggregate(
        hosted_plays=Count('game_id', filter=~solo, distinct=True),
        solo_plays=Count('game_id', filter=solo, distinct=True),
        participations=Count('id'),
        hosted_participations=Count('id', filter=~solo),
        last_played=Max('game__finished'))
    answers = answers_by_question(players, m['Answer'])
    skip = unscored_keys(quiz_id, list(answers), m['Answer'], m['Question']) if answers else set()
    scored = [pair for key, pair in answers.items() if key not in skip]
    return dict(games, plays=games['hosted_plays'] + games['solo_plays'], unique_players=different_players(players),
                answers_counted=sum(a for a, _c in scored), answers_correct=sum(c for _a, c in scored))


def recount(quiz_id):
    """Store fresh counters. The quiz row is locked first, so two games finishing at once cannot leave
    the older numbers behind. `updated` stays: playing a quiz does not change it."""
    with transaction.atomic():
        # NO KEY: new games and questions of the quiz do not wait for this lock.
        if not Quiz.objects.select_for_update(no_key=True).filter(id=quiz_id).values_list('id', flat=True):
            return
        Quiz.objects.filter(id=quiz_id).update(**totals(quiz_id))
    cache.delete(detail_key(quiz_id))


def recount_safely(quiz_id):
    """For the end of a game: statistics must never keep a game from finishing."""
    try:
        recount(quiz_id)
    except Exception:
        logger.exception('quiz %s: statistics were not updated', quiz_id)


def detail(quiz):
    """The best result and how hard each question is, for the quiz page (cached for a minute)."""
    data = cache.get(detail_key(quiz.id))
    if data is None:
        players = counted_players(quiz.id)
        best = players.order_by('-score', 'joined', 'id').values('nickname', 'score').first()
        scored = set(quiz.questions.exclude(type__in=Question.UNSCORED).values_list('id', flat=True))
        data = {'best': best, 'questions': {
            key: {'answered': answered, 'correct': correct, 'percent': percent(correct, answered)}
            for key, (answered, correct) in answers_by_question(players).items() if key in scored}}
        cache.set(detail_key(quiz.id), data, DETAIL_TTL)
    return data


@receiver(post_delete, sender=GameSession, dispatch_uid='quiz_stats_game_deleted')
def game_deleted(sender, instance, **kwargs):
    quiz_id = instance.quiz_id
    transaction.on_commit(lambda: recount_safely(quiz_id))


def percent(part, whole):
    """A whole percent, halves up."""
    return int(100 * part / whole + 0.5) if whole else None
