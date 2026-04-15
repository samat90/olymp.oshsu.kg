"""Remove LaTeX math delimiters — just leave the content.

$X$ → X (or `X` if it's a single identifier, to keep monospace)
\\(X\\) → X
$$X$$ → X
\\[X\\] → X"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

import django
django.setup()

from judge.models import Problem


def strip_math(text: str) -> str:
    # \(...\) inline — non-greedy, allow any chars including inner parens
    text = re.sub(r'\\\((.+?)\\\)', r'\1', text)
    # \[...\] block
    text = re.sub(r'\\\[(.+?)\\\]', r'\1', text, flags=re.DOTALL)
    # $$...$$ block
    text = re.sub(r'\$\$([^$]+?)\$\$', r'\1', text, flags=re.DOTALL)
    # $...$ inline (single-line only, to avoid eating content)
    text = re.sub(r'\$([^\$\n]+?)\$', r'\1', text)
    # Replace LaTeX escapes like \le, \ge, \cdot with plain text
    text = text.replace(r'\le', '≤').replace(r'\ge', '≥')
    text = text.replace(r'\leq', '≤').replace(r'\geq', '≥')
    text = text.replace(r'\cdot', '·').replace(r'\times', '×')
    text = text.replace(r'\ldots', '…').replace(r'\dots', '…')
    text = text.replace(r'\bmod', 'mod')
    text = text.replace(r'\gcd', 'gcd')
    text = text.replace(r'\mathrm{lcm}', 'lcm').replace(r'\mathrm', '')
    text = text.replace(r'\tau', 'τ')
    # Power: 10^9 as-is, but 10^{18} → 10^18
    text = re.sub(r'\^\{(-?\d+)\}', r'^\1', text)
    text = re.sub(r'\^\{([A-Za-z])\}', r'^\1', text)
    # _{x} → _x
    text = re.sub(r'_\{(-?\w+)\}', r'_\1', text)
    return text


count = 0
for p in Problem.objects.all():
    orig = p.description
    new = strip_math(orig)
    if new != orig:
        p.description = new
        p.save(update_fields=['description'])
        count += 1
        print(f'fixed {p.code}')

print(f'Total fixed: {count}')
