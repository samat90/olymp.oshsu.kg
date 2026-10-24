"""Load test: an ordinary day, 1000 students practising (no olympiad).

They browse the problem archive, open problems, run code in the editor and in the
Compiler section (also interactively in the terminal), submit solutions and look at
their submissions. Problem codes are read from PROBLEMS_FILE (one code per line).

    locust -f scripts/load/locustfile_everyday.py --host http://127.0.0.1:8080 -u 1000 -r 5 --headless -t 10m
"""
import json
import os
import random
import re
import time

from locust import HttpUser, between, events, task

CSRF_RE = re.compile(r"""name=["']csrfmiddlewaretoken["'] value=["']([^"']+)""")
LANG_RE = re.compile(r'<option value="(\d+)" data-key="(\w+)"')
RUNNER_WS = os.environ.get('RUNNER_WS', 'ws://127.0.0.1:9910/session')
PROBLEMS = [line.strip() for line in open(os.environ.get('PROBLEMS_FILE', '/tmp/public_problems.txt')) if line.strip()]

PROGRAMS = {
    'PY3': 'import sys\ndata = sys.stdin.read().split()\nprint(sum(int(x) for x in data if x.lstrip("-").isdigit()))\n',
    'CPP17': '#include <bits/stdc++.h>\nusing namespace std;\nint main(){long long s=0,x;while(cin>>x)s+=x;cout<<s<<endl;}\n',
    'JAVA': 'import java.util.*;\npublic class Main{public static void main(String[] a){Scanner s=new Scanner(System.in);'
            'long t=0;while(s.hasNextLong())t+=s.nextLong();System.out.println(t);}}\n',
    'GO': 'package main\nimport "fmt"\nfunc main(){var s,x int64\nfor{if _,e:=fmt.Scan(&x);e!=nil{break};s+=x}\n'
          'fmt.Println(s)}\n',
}
INTERACTIVE = {
    'PY3': 'name = input("Как вас зовут? ")\nn = int(input("Число: "))\nprint("Привет,", name, n * n)\n',
    'CPP17': '#include <iostream>\nint main(){int a,b;std::cout<<"a b: ";std::cin>>a>>b;std::cout<<a+b<<std::endl;}\n',
}
# Java is left out: on the laptop the judge has JAVA while the site lists JAVA8.
LANG_WEIGHTS = [('PY3', 5), ('CPP17', 4), ('GO', 1)]

counter = iter(range(1, 100000))


def pick_language():
    keys = [k for k, w in LANG_WEIGHTS for _ in range(w)]
    return random.choice(keys)


class Student(HttpUser):
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
        self.token = None
        self.token_exp = 0
        self.file_id = None

    def csrf(self):
        return self.client.cookies.get('csrftoken', '')

    def runner_token(self, problem=None):
        if problem or not self.token or self.token_exp - time.time() < 30:
            r = self.client.post('/runner/token/', json={'problem': problem}, name='runner token',
                                 headers={'X-CSRFToken': self.csrf(), 'Referer': self.host + '/'})
            try:
                data = r.json()
            except ValueError:
                return None
            if not data.get('ok'):
                return None
            if problem:
                return data['token']
            self.token, self.token_exp = data['token'], data['expires']
        return self.token

    # ---- browsing ----

    @task(8)
    def problem_list(self):
        page = random.randint(1, 3)
        self.client.get('/problems/?page=%d' % page, name='problem list')

    @task(10)
    def problem_page(self):
        self.client.get('/problem/%s' % random.choice(PROBLEMS), name='problem page')

    @task(4)
    def home(self):
        self.client.get('/', name='home')

    @task(4)
    def my_submissions(self):
        self.client.get('/submissions/user/%s/' % self.username, name='my submissions')

    @task(2)
    def status_page(self):
        self.client.get('/submissions/', name='all submissions')

    # ---- solving a problem in the editor ----

    @task(10)
    def solve_and_run(self):
        code = random.choice(PROBLEMS)
        self.client.get('/problem/%s/submit' % code, name='solve page')
        token = self.runner_token(code)
        if not token:
            return
        lang = pick_language()
        self.client.post('http://127.0.0.1:9910/run', json={
            'token': token, 'language': lang, 'source': PROGRAMS[lang], 'stdins': ['1 2\n', '3 4\n'],
        }, name='editor: test on samples')

    @task(5)
    def submit(self):
        code = random.choice(PROBLEMS)
        page = self.client.get('/problem/%s/submit' % code, name='solve page')
        csrf = CSRF_RE.search(page.text)
        langs = dict((key, value) for value, key in LANG_RE.findall(page.text))
        lang = pick_language()
        if not csrf or lang not in langs:
            return
        self.client.post('/problem/%s/submit' % code, {
            'csrfmiddlewaretoken': csrf.group(1), 'language': langs[lang], 'source': PROGRAMS[lang],
        }, headers={'Referer': self.host + '/problem/%s/submit' % code}, name='submit')

    # ---- the Compiler section ----

    @task(6)
    def compiler_run(self):
        self.client.get('/compiler/', name='compiler page')
        self.client.get('/compiler/api/files/', name='compiler: list files')
        lang = pick_language()
        if self.file_id is None:
            r = self.client.post('/compiler/api/files/new/', json={
                'name': 'main%d.%s' % (random.randint(1, 10 ** 6), {'PY3': 'py', 'CPP17': 'cpp', 'JAVA': 'java',
                                                                      'GO': 'go'}[lang]),
                'content': PROGRAMS[lang], 'language': lang,
            }, headers={'X-CSRFToken': self.csrf(), 'Referer': self.host + '/compiler/'}, name='compiler: new file')
            try:
                self.file_id = r.json()['file']['id']
            except (ValueError, KeyError, TypeError):
                return
        self.client.post('/compiler/api/files/%d/save/' % self.file_id, json={'content': PROGRAMS[lang]},
                         headers={'X-CSRFToken': self.csrf(), 'Referer': self.host + '/compiler/'},
                         name='compiler: autosave')
        token = self.runner_token()
        if token:
            self.client.post('http://127.0.0.1:9910/run', json={
                'token': token, 'language': lang, 'source': PROGRAMS[lang], 'stdin': '5 7 9\n',
            }, name='compiler: run with input')

    @task(4)
    def compiler_terminal(self):
        """Interactive run: the student answers the program's questions in the terminal."""
        import websocket
        token = self.runner_token()
        if not token:
            return
        lang = random.choice(list(INTERACTIVE))
        start = time.time()
        error = None
        received = 0
        try:
            ws = websocket.create_connection(RUNNER_WS, timeout=60)
            ws.send(json.dumps({'token': token, 'language': lang, 'source': INTERACTIVE[lang]}))
            answers = ['Студент\n', '12\n'] if lang == 'PY3' else ['3 4\n']
            while True:
                message = json.loads(ws.recv())
                received += 1
                if message['type'] == 'out' and answers:
                    time.sleep(random.uniform(0.5, 2))      # the student reads and types
                    ws.send(json.dumps({'type': 'in', 'data': answers.pop(0)}))
                elif message['type'] == 'compile_error':
                    error = message.get('output', '')[:60]
                    break
                elif message['type'] == 'exit':
                    if message.get('verdict') != 'OK':
                        error = 'verdict ' + str(message.get('verdict'))
                    break
            ws.close()
        except Exception as e:  # noqa: BLE001
            error = str(e)[:80]
        events.request.fire(request_type='WS', name='compiler: terminal session',
                            response_time=(time.time() - start) * 1000, response_length=received,
                            exception=Exception(error) if error else None, context={})
