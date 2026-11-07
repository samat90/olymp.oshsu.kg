"""Run every code example of the programming quizzes and compare the output with the correct answer.

Needs python3, g++, javac/java, mcs/mono and node (the WSL dev stand has them): python3 check_prog.py
"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_prog import QUIZZES

CPP = '#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n%s\n}\n'
JAVA = 'import java.util.*;\npublic class Main {\npublic static void main(String[] args) throws Exception {\n%s\n}\n}\n'
CS = ('using System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Text;\n'
      'class Program {\nstatic void Main() {\n%s\n}\n}\n')
ENV = dict(os.environ, LANG='C.UTF-8', LC_ALL='C.UTF-8', PYTHONIOENCODING='utf-8')


def sh(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, env=ENV, timeout=60)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


def run(lang, code, d):
    def write(name, text):
        with open(os.path.join(d, name), 'w', encoding='utf-8') as f:
            f.write(text)
    if lang == 'python':
        write('a.py', code)
        return sh(['python3', 'a.py'], d)
    if lang == 'javascript':
        write('a.js', code)
        return sh(['node', 'a.js'], d)
    if lang == 'cpp':
        write('a.cpp', code if 'int main' in code else CPP % code)
        rc, out, err = sh(['g++', '-std=c++17', '-o', 'a', 'a.cpp'], d)
        return (rc, out, 'COMPILE ' + err) if rc else sh(['./a'], d)
    if lang == 'java':
        write('Main.java', code if 'class Main' in code else JAVA % code)
        rc, out, err = sh(['javac', '-encoding', 'UTF-8', 'Main.java'], d)
        return (rc, out, 'COMPILE ' + err) if rc else sh(['java', '-cp', '.', 'Main'], d)
    if lang == 'csharp':
        write('a.cs', code if 'static void Main' in code else CS % code)
        rc, out, err = sh(['mcs', '-out:a.exe', 'a.cs'], d)
        return (rc, out, 'COMPILE ' + err) if rc else sh(['mono', 'a.exe'], d)
    raise ValueError(lang)


def expected(q):
    if q['out'] is not None:
        return q['out']
    if q['type'] == 'order':
        return '\n'.join(q['opts'])
    if q['type'] == 'text':
        return q['answers'][0]
    return q['opts'][0]


bad = total = 0
for quiz in QUIZZES:
    for i, q in enumerate(quiz['questions'], 1):
        if not q['code']:
            continue
        total += 1
        with tempfile.TemporaryDirectory() as d:
            rc, out, err = run(q['lang'], q['code'], d)
        want = expected(q)
        if want == 'EXC':
            ok = rc != 0 and not err.startswith('COMPILE')
        else:
            ok = rc == 0 and ' '.join(out.split()) == ' '.join(want.split())
        if not ok:
            bad += 1
            print('FAIL %s #%d: want %r, got %r (rc %d) %s' % (quiz['key'], i, want, out, rc, err.strip()[:300]))
print('checked %d, failed %d' % (total, bad))
