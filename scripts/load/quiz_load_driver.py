"""Creates a quiz game for the load test, starts it when the players are in and waits for the end.
FOR THE LAPTOP COPY ONLY.

    DJANGO_SETTINGS_MODULE=dmoj.load_settings python scripts/load/quiz_load_driver.py <pin file> <players> [mode]

Writes the PIN to <pin file> at once, then starts the game when <players> joined (or after 3 minutes).
Mode `auto` (default) moves on by timers; `screen` presses "Next" like a host would.
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.load_settings')

import django  # noqa: E402

django.setup()

from django.contrib.auth.models import User  # noqa: E402

from judge.models import GameSession, Quiz, QuizOption, QuizQuestion  # noqa: E402
from judge.utils import quiz_game as engine  # noqa: E402

QUESTIONS = [
    ('single', 'Сколько байт в килобайте?', [('1000', False), ('1024', True), ('512', False), ('2048', False)], {}),
    ('truefalse', 'Python — компилируемый язык?', [('Верно', False), ('Неверно', True)], {}),
    ('multi', 'Какие из них — языки программирования?',
     [('C++', True), ('HTML', False), ('Java', True), ('CSS', False)], {}),
    ('word', 'Собери слово', [], {'word': 'АЛГОРИТМ'}),
    ('order', 'Расставь по возрастанию', [('бит', False), ('байт', False), ('килобайт', False),
                                          ('мегабайт', False)], {}),
    ('code', 'Что выведет код?', [('3', False), ('5', True), ('8', False)], {'input': False}),
    ('text', 'Столица Кыргызстана?', [], {'answers': ['Бишкек'], 'tolerance': 0}),
    ('slider', 'Сколько будет 6 * 7?', [], {'min': 0, 'max': 100, 'step': 1, 'answer': 42, 'tolerance': 1}),
    ('poll', 'Любимый язык?', [('Python', False), ('C++', False), ('Pascal', False)], {}),
    ('cloud', 'Одно слово о программировании', [], {}),
]


def make_quiz(author):
    quiz = Quiz.objects.filter(key='loadquiz').first()
    if quiz is not None:
        return quiz
    quiz = Quiz.objects.create(author=author, title='Нагрузочная викторина', key='loadquiz', access=Quiz.LINK)
    for n, (t, text, options, data) in enumerate(QUESTIONS):
        q = QuizQuestion.objects.create(quiz=quiz, order=n, type=t, text=text, time_limit=15, data=data,
                                        code='print(2 + 3)' if t == 'code' else '', code_language='python')
        for m, (option, ok) in enumerate(options):
            QuizOption.objects.create(question=q, order=m, text=option, is_correct=ok)
    return quiz


def main():
    pin_file, wanted = sys.argv[1], int(sys.argv[2])
    mode = sys.argv[3] if len(sys.argv) > 3 else GameSession.AUTO
    host = User.objects.get(username='devadmin').profile
    game = engine.create_game(make_quiz(host), host, mode, {'guests': True})
    with open(pin_file, 'w') as f:
        f.write(game.pin)
    print('pin', game.pin, flush=True)
    started = time.time()
    while engine.player_count(game.id) < wanted and time.time() - started < 180:
        time.sleep(1)
    print('players', engine.player_count(game.id), 'after %.0f s' % (time.time() - started), flush=True)
    t0 = time.time()
    state = engine.start(game.pin)
    phase = None
    while state['ph'] != GameSession.FINISHED and time.time() - t0 < 900:
        # Players' polls move the game on; this is only a fallback if they have stopped.
        state = engine.advance_if_due(engine.fresh_state(game.pin))
        if (state['ph'], state['i']) != phase:
            phase = (state['ph'], state['i'])
            answered = engine.answered_count(game.id, state['i'])
            print('%6.1f s  %-11s q%-2d answered %d' % (time.time() - t0, state['ph'], state['i'] + 1, answered),
                  flush=True)
        if mode != GameSession.AUTO and state['ph'] in (GameSession.REVEAL, GameSession.LEADERBOARD) and \
                time.time() - state['ts'] > 5:
            engine.next_step(game.pin)
        time.sleep(0.5)
    game.refresh_from_db()
    print('finished: status %s, players %d, answers %d' % (
        game.status, game.players.count(), sum(p.answers.count() for p in game.players.all())), flush=True)


if __name__ == '__main__':
    main()
