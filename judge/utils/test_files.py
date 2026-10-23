"""Pair input and answer files of a test archive."""
import os
import re

# (input suffix, answer suffix); checked in this order.
SUFFIX_PAIRS = [
    ('.in', '.out'),
    ('.in', '.ans'),
    ('.in', '.a'),
    ('.in', '.res'),
    ('.in', '.sol'),
    ('.dat', '.ans'),
    ('.txt', '.a'),
    ('', '.a'),
    ('', '.ans'),
    ('', '.out'),
]
WORD_PAIRS = [('input', 'output'), ('in', 'out')]


def natural_key(name):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', name)]


def is_hidden(name):
    return any(part.startswith(('.', '__MACOSX')) for part in name.split('/'))


def pair_test_files(names):
    """Return [(input, answer)] sorted naturally. Unpaired files are ignored."""
    files = [n for n in names if not n.endswith('/') and not is_hidden(n)]
    available = set(files)
    used = set()
    pairs = []

    for name in sorted(files, key=natural_key):
        if name in used:
            continue
        for in_suffix, out_suffix in SUFFIX_PAIRS:
            if in_suffix and not name.endswith(in_suffix):
                continue
            if not in_suffix and os.path.splitext(os.path.basename(name))[1]:
                continue
            stem = name[:-len(in_suffix)] if in_suffix else name
            answer = stem + out_suffix
            if answer in available and answer not in used and answer != name:
                pairs.append((name, answer))
                used.update((name, answer))
                break
        else:
            # input1.txt / output1.txt, test01.in.txt and the like
            base = os.path.basename(name)
            for a, b in WORD_PAIRS:
                match = re.search(r'(?<![a-z])%s(?![a-z])' % a, base, re.I)
                if not match:
                    continue
                answer = os.path.join(os.path.dirname(name),
                                      base[:match.start()] + b + base[match.end():]).replace('\\', '/')
                if answer in available and answer not in used:
                    pairs.append((name, answer))
                    used.update((name, answer))
                    break
    pairs.sort(key=lambda pair: natural_key(pair[0]))
    return pairs
