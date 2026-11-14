"""Turns $...$ formulas of a statement into plain text with Unicode signs.

The site has no formula renderer (MATHOID is off), so `$n \\le 10^5$` showed up with raw dollar signs.
`clean_math` rewrites every balanced $...$ into a code span such as `n ≤ 10⁵`.
"""
import re

COMMANDS = {
    'le': '≤', 'leq': '≤', 'leqslant': '≤', 'ge': '≥', 'geq': '≥', 'geqslant': '≥', 'ne': '≠', 'neq': '≠',
    'cdot': '·', 'times': '×', 'dots': '…', 'ldots': '…', 'cdots': '…', 'to': '→', 'rightarrow': '→',
    'bmod': ' mod ', 'pmod': ' mod ', 'mod': ' mod ', 'oplus': '⊕', 'lfloor': '⌊', 'rfloor': '⌋', 'lceil': '⌈',
    'rceil': '⌉', 'sum': 'Σ', 'infty': '∞', 'in': '∈', 'lt': '<', 'gt': '>', 'mid': '|', 'equiv': '≡',
    'approx': '≈', 'pm': '±', 'min': 'min', 'max': 'max', 'gcd': 'gcd', 'log': 'log', 'lg': 'lg', 'ln': 'ln',
    'left': '', 'right': '', 'bigl': '', 'bigr': '', 'Bigl': '', 'Bigr': '', 'quad': ' ', 'qquad': ' ',
    'lbrace': '{', 'rbrace': '}', 'vert': '|', 'lvert': '|', 'rvert': '|', 'land': '∧', 'lor': '∨', 'cup': '∪',
    'cap': '∩', 'subset': '⊂', 'subseteq': '⊆', 'emptyset': '∅', 'varnothing': '∅', 'forall': '∀', 'exists': '∃',
    'Rightarrow': '⇒', 'Leftrightarrow': '⇔', 'll': '≪', 'gg': '≫', 'neg': '¬', 'prod': 'Π', 'binom': 'C',
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'varepsilon': 'ε', 'epsilon': 'ε', 'lambda': 'λ',
    'mu': 'μ', 'pi': 'π', 'sigma': 'σ', 'phi': 'φ', 'varphi': 'φ', 'theta': 'θ', 'omega': 'ω', 'ell': 'l',
    'angle': '∠', 'circ': '°', 'ge ': '≥', 'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'dot': '·',
}
SUP = dict(zip('0123456789+-=()n', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ'))
SUP.update({'i': 'ⁱ', 'k': 'ᵏ', 'm': 'ᵐ'})
SUB = dict(zip('0123456789+-=()', '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎'))
SUB.update({'a': 'ₐ', 'e': 'ₑ', 'h': 'ₕ', 'i': 'ᵢ', 'j': 'ⱼ', 'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ', 'o': 'ₒ',
            'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ', 'u': 'ᵤ', 'v': 'ᵥ', 'x': 'ₓ'})


def _group(s, i):
    """Return (content, next index) of the argument starting at s[i]: {...} or one character."""
    while i < len(s) and s[i] == ' ':
        i += 1
    if i >= len(s):
        return '', i
    if s[i] == '{':
        depth, j = 0, i
        while j < len(s):
            depth += s[j] == '{'
            depth -= s[j] == '}'
            j += 1
            if depth == 0:
                break
        return s[i + 1:j - 1], j
    if s[i] == '\\':
        m = re.match(r'\\[a-zA-Z]+', s[i:])
        if m:
            return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def _convert(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == '\\':
            m = re.match(r'\\([a-zA-Z]+)', s[i:])
            if not m:  # \, \; \! \  \{ \} \\
                nxt = s[i + 1:i + 2]
                out.append({'{': '{', '}': '}', '%': '%', '$': '$', '&': '&'}.get(nxt, ' ' if nxt in ',;! ' else ''))
                i += 2
                continue
            name = m.group(1)
            i += len(m.group(0))
            if name in ('text', 'mathrm', 'operatorname', 'mathbf', 'textbf', 'mathit', 'mathcal'):
                arg, i = _group(s, i)
                out.append(_convert(arg))
            elif name == 'sqrt':
                arg, i = _group(s, i)
                out.append('√(%s)' % _convert(arg))
            elif name in ('frac', 'dfrac', 'tfrac'):
                a, i = _group(s, i)
                b, i = _group(s, i)
                out.append('(%s)/(%s)' % (_convert(a), _convert(b)))
            elif name == 'binom':
                a, i = _group(s, i)
                b, i = _group(s, i)
                out.append('C(%s, %s)' % (_convert(a), _convert(b)))
            else:
                out.append(COMMANDS.get(name, name))
        elif c in '^_':
            arg, i = _group(s, i + 1)
            arg = _convert(arg)
            table = SUP if c == '^' else SUB
            if arg and all(ch in table for ch in arg):
                out.append(''.join(table[ch] for ch in arg))
            else:
                out.append(c + ('(%s)' % arg if len(arg) > 1 else arg))
        elif c in '{}':
            i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def _tidy(s):
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s.replace('`', "'")


def clean_math(text):
    """Replace balanced $...$ and $$...$$ formulas by Unicode text in code spans. Unbalanced text is left alone."""
    if '$' not in text:
        return text

    def inline(m):
        body = _tidy(_convert(m.group(1)))
        return '`%s`' % body if body else ''
    text = re.sub(r'\$\$(.+?)\$\$', lambda m: inline(m), text, flags=re.S)
    return re.sub(r'\$([^$\n]+?)\$', inline, text)
