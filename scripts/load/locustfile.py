"""Load test: participants of one contest during an olympiad.

    locust -f scripts/load/locustfile.py --host http://127.0.0.1:8080 -u 1000 -r 20 --headless -t 5m

Accounts load0001..load1000 (password load-pass-2026) and the contest "load1000"
are created by scripts/load/seed_load.py.
"""
import os
import random
import re

from locust import HttpUser, between, task

CONTEST = 'load1000'
PROBLEMS = ['000001', '000002', '000003', '001057']
SOLUTION = 'n = int(input())\nprint(n * (n + 1) // 2)\n'
CSRF_RE = re.compile(r"""name=["']csrfmiddlewaretoken["'] value=["']([^"']+)""")

counter = iter(range(1, 100000))


class Participant(HttpUser):
    # Seconds between two pages of one participant. Students mostly type code in the editor,
    # so 20-40 s is realistic; 5-15 s is a stress test.
    wait_time = between(int(os.environ.get('WAIT_MIN', 20)), int(os.environ.get('WAIT_MAX', 40)))

    def on_start(self):
        n = next(counter) % 1000 + 1
        self.username = 'load%04d' % n
        page = self.client.get('/accounts/login/', name='login page')
        token = CSRF_RE.search(page.text)
        self.client.post('/accounts/login/', {
            'username': self.username, 'password': 'load-pass-2026',
            'csrfmiddlewaretoken': token.group(1) if token else '',
        }, headers={'Referer': self.host + '/accounts/login/'}, name='login')

    @task(30)
    def solve_page(self):
        self.client.get('/problem/%s/submit' % random.choice(PROBLEMS), name='solve page')

    @task(10)
    def problem_page(self):
        self.client.get('/problem/%s' % random.choice(PROBLEMS), name='problem page')

    @task(10)
    def contest_page(self):
        self.client.get('/contest/%s' % CONTEST, name='contest page')

    @task(15)
    def ranking(self):
        self.client.get('/contest/%s/ranking/' % CONTEST, name='ranking')

    @task(10)
    def my_submissions(self):
        self.client.get('/contest/%s/submissions/%s/' % (CONTEST, self.username), name='my submissions')

    @task(5)
    def runner_token(self):
        csrf = self.client.cookies.get('csrftoken', '')
        self.client.post('/runner/token/', json={'problem': random.choice(PROBLEMS)},
                         headers={'X-CSRFToken': csrf, 'Referer': self.host + '/'}, name='runner token')

    @task(3)
    def submit(self):
        problem = random.choice(PROBLEMS)
        page = self.client.get('/problem/%s/submit' % problem, name='solve page')
        token = CSRF_RE.search(page.text)
        lang = re.search(r'<option value="(\d+)" data-key="PY3"', page.text)
        if not token or not lang:
            return
        self.client.post('/problem/%s/submit' % problem, {
            'csrfmiddlewaretoken': token.group(1), 'language': lang.group(1), 'source': SOLUTION,
        }, headers={'Referer': self.host + '/problem/%s/submit' % problem}, name='submit')
