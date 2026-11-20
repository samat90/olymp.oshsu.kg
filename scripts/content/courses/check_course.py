"""Runs every code sample of the test questions and compares the output with the marked answer.

    python scripts/content/courses/check_course.py [python]
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def load(folder):
    modules = []
    for name in sorted(os.listdir(folder)):
        if name.startswith('m') and name.endswith('.py'):
            scope = {}
            exec(compile(open(os.path.join(folder, name), encoding='utf-8').read(), name, 'exec'), scope)
            modules.append((name, scope['MODULE']))
    return modules


def run(code):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'x.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        p = subprocess.run([sys.executable, '-I', path], cwd=tmp, capture_output=True, timeout=10,
                           env={'PYTHONIOENCODING': 'utf-8', 'PATH': os.environ.get('PATH', '')})
        return p.returncode, p.stdout.decode('utf-8'), p.stderr.decode('utf-8')


def main(name):
    bad = 0
    total = 0
    for fname, module in load(os.path.join(HERE, name)):
        for lesson in module['lessons']:
            for block in lesson['blocks']:
                if block['type'] != 'test':
                    continue
                for n, q in enumerate(block['questions'], 1):
                    where = '%s / %s / q%d' % (fname, lesson['title'], n)
                    kind = q.get('type', 'single')
                    opts = q['options']
                    if len(set(opts)) != len(opts):
                        print('DUPLICATE OPTIONS', where)
                        bad += 1
                    if kind in ('single', 'multi'):
                        ans = q['answer'] if isinstance(q['answer'], list) else [q['answer']]
                        if any(not 0 <= a < len(opts) for a in ans):
                            print('BAD ANSWER INDEX', where)
                            bad += 1
                    total += 1
                    if not q.get('code') or not q['text'].startswith('Что выведет'):
                        continue
                    code, out, err = run(q['code'])
                    right = opts[q['answer']] if kind == 'single' else None
                    if right is None:
                        continue
                    if code != 0:
                        error_name = err.strip().splitlines()[-1] if err.strip() else ''
                        if not (right.startswith('Ошибка') or right.split(':')[0].split()[0] in error_name):
                            print('RAISED BUT ANSWER IS NOT AN ERROR', where, error_name)
                            bad += 1
                        continue
                    got = out[:-1] if out.endswith('\n') else out
                    if got != right:
                        print('MISMATCH', where, 'got %r, marked %r' % (got, right))
                        bad += 1
    print('questions:', total, 'problems:', bad)
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else 'python') else 0)
