"""Load test: one quiz game with many players polling the game state.

    QUIZ_PIN=123456 locust -f scripts/load/locustfile_quiz.py --host http://127.0.0.1:8080 -u 1000 -r 25 --headless

The game is created and started by scripts/load/quiz_load_driver.py (see run_quiz_load.sh).
Every virtual player joins as a guest, polls /state at the interval the server asks for,
gets each question (it comes with the state of the new phase) and answers after a human-like pause.
"""
import json
import os
import random
import re
import time

from locust import HttpUser, constant, events, task

PIN = os.environ.get('QUIZ_PIN', '')
CSRF_RE = re.compile(r"""name=["']csrfmiddlewaretoken["'] value=["']([^"']+)""")
counter = iter(range(1, 1000000))


def answer_for(question):
    t = question['type']
    options = [o['id'] for o in question.get('options', [])]
    if t in ('single', 'truefalse', 'poll') or (t == 'code' and options):
        return random.choice(options)
    if t == 'multi':
        return random.sample(options, random.randint(1, len(options)))
    if t == 'order':
        random.shuffle(options)
        return options
    if t == 'word':
        letters = question.get('letters', [])
        return ''.join(random.sample(letters, len(letters))) if random.random() < .5 else 'АЛГОРИТМ'
    if t == 'slider':
        s = question['slider']
        return random.uniform(float(s['min']), float(s['max']))
    if t == 'pin':
        return {'x': random.uniform(0, 100), 'y': random.uniform(0, 100)}
    return random.choice(['42', 'Бишкек', 'python', 'цикл', 'массив'])


class Player(HttpUser):
    wait_time = constant(0)

    def on_start(self):
        self.nick = 'Игрок%d_%d' % (os.getpid() % 1000, next(counter))
        page = self.client.get('/quiz/join/?pin=%s' % PIN, name='join page')
        token = CSRF_RE.search(page.text)
        self.csrf = self.client.cookies.get('csrftoken', '')
        self.client.post('/quiz/join/', {
            'pin': PIN, 'nickname': self.nick, 'csrfmiddlewaretoken': token.group(1) if token else self.csrf,
        }, headers={'Referer': self.host + '/quiz/join/'}, name='join', allow_redirects=False)
        self.version = None
        self.phase = None
        self.index = -1
        self.answer_at = None
        self.question = None
        self.poll = 1.0
        self.done = False

    @task
    def play(self):
        if self.done:
            time.sleep(5)
            return
        now = time.time()
        if self.answer_at and now >= self.answer_at:
            self.answer_at = None
            with self.client.post('/quiz/g/%s/answer' % PIN,
                                  data=json.dumps({'i': self.index, 'value': answer_for(self.question)}),
                                  headers={'X-CSRFToken': self.csrf, 'Content-Type': 'application/json',
                                           'Referer': self.host + '/quiz/g/%s/' % PIN},
                                  name='answer', catch_response=True) as r:
                if r.status_code != 200:
                    r.failure('%s %s' % (r.status_code, r.text[:60]))
        url = '/quiz/g/%s/state' % PIN + ('?v=%s' % self.version if self.version else '')
        with self.client.get(url, name='state', catch_response=True) as r:
            if r.status_code != 200:
                r.failure('status %s' % r.status_code)
                time.sleep(2)
                return
            data = r.json()
        if data:
            self.version = data['v']
            self.poll = data['poll'] / 1000
            if data['ph'] != self.phase or data['i'] != self.index:
                self.phase, self.index = data['ph'], data['i']
                self.on_phase(data)
        time.sleep(self.poll * random.uniform(.9, 1.1))

    def on_phase(self, state):
        # The state response of a new phase already carries the question, the result or the final screen.
        if self.phase == 'question':
            self.question = state['question']
            # Answers open after the countdown; players think for a few seconds; some do not answer.
            if random.random() < .95:
                delay = max(state['start'] - state['now'], 0) + random.uniform(1, min(self.question['time'] - 1, 12))
                self.answer_at = time.time() + delay
        elif self.phase in ('reveal', 'leaderboard'):
            self.answer_at = None
        elif self.phase == 'finished':
            self.done = True


@events.quitting.add_listener
def summary(environment, **kwargs):
    stats = environment.stats
    for name in ('state', 'answer', 'join'):
        entry = stats.get(name, 'GET') if name != 'answer' and name != 'join' else stats.get(name, 'POST')
        if entry.num_requests:
            print('%-9s %7d req %5d fail  p50 %4d ms  p95 %4d ms  p99 %4d ms  max %5d ms' % (
                name, entry.num_requests, entry.num_failures, entry.get_response_time_percentile(.5),
                entry.get_response_time_percentile(.95), entry.get_response_time_percentile(.99),
                entry.max_response_time))
