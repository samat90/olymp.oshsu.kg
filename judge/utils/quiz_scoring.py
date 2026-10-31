"""Checking quiz answers and counting points.

A question is checked against its "key": a small dict built once per game from the Question
and its options (see build_key), so answering does not read the database.

Answer values sent by players, by question type:
    single, truefalse, poll, code (with options)  -> option id (int)
    multi                                         -> list of option ids
    order                                         -> list of all option ids in the player's order
    word, text, code (typed), cloud, open         -> string
    slider                                        -> number
    pin                                           -> {"x": 0..100, "y": 0..100}, percent of the image
"""
import math
import re

from judge.models.quiz import Question

BASE_POINTS = 1000
STREAK_STEP = 100
STREAK_MAX = 500
MAX_TEXT = {Question.CLOUD: 30, Question.OPEN: 300}
DEFAULT_MAX_TEXT = 100


def normalize_text(value):
    value = str(value).strip().casefold().replace('ё', 'е')
    value = re.sub(r'\s+', ' ', value)
    return value


def parse_number(value):
    try:
        number = float(str(value).strip().replace(',', '.').replace(' ', ''))
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def option_ids(question):
    return [o.id for o in question.options.all()]


def build_key(question):
    """Everything needed to check an answer to this question, without the database."""
    options = list(question.options.all())
    data = question.data or {}
    key = {'id': question.id, 'type': question.type, 'time': question.time_limit, 'weight': question.weight,
           'options': [o.id for o in options], 'correct': [o.id for o in options if o.is_correct]}
    t = question.type
    if t == Question.ORDER:
        key['correct'] = [o.id for o in options]
    elif t == Question.WORD:
        key['word'] = normalize_text(data.get('word', ''))
    elif t in (Question.TEXT, Question.CODE):
        key['answers'] = [normalize_text(a) for a in data.get('answers', []) if str(a).strip()]
        key['tolerance'] = abs(parse_number(data.get('tolerance', 0)) or 0)
        key['input'] = t == Question.TEXT or bool(data.get('input'))
    elif t == Question.SLIDER:
        lo, hi = parse_number(data.get('min', 0)) or 0, parse_number(data.get('max', 100))
        hi = 100 if hi is None else hi
        key.update({'min': lo, 'max': hi, 'answer': parse_number(data.get('answer', lo)) or 0,
                    'tolerance': abs(parse_number(data.get('tolerance', 0)) or 0)})
    elif t == Question.PIN:
        key.update({'x': parse_number(data.get('x', 50)) or 0, 'y': parse_number(data.get('y', 50)) or 0,
                    'r': max(parse_number(data.get('r', 10)) or 10, 1)})
    return key


def clean_value(key, value):
    """The answer in its stored form, or None if it does not fit the question."""
    t = key['type']
    try:
        if t in (Question.SINGLE, Question.TRUEFALSE, Question.POLL) or \
                (t == Question.CODE and not key.get('input')):
            value = int(value)
            return value if value in key['options'] else None
        if t == Question.MULTI:
            ids = sorted({int(v) for v in value})
            return ids if all(i in key['options'] for i in ids) else None
        if t == Question.ORDER:
            ids = [int(v) for v in value]
            return ids if sorted(ids) == sorted(key['options']) else None
        if t == Question.SLIDER:
            number = parse_number(value)
            return None if number is None else min(max(number, key['min']), key['max'])
        if t == Question.PIN:
            x, y = parse_number(value.get('x')), parse_number(value.get('y'))
            if x is None or y is None:
                return None
            return {'x': round(min(max(x, 0), 100), 2), 'y': round(min(max(y, 0), 100), 2)}
        if isinstance(value, (list, dict)):
            return None
        text = str(value).strip()
        if not text:
            return None
        return text[:MAX_TEXT.get(t, DEFAULT_MAX_TEXT)]
    except (TypeError, ValueError, AttributeError):
        return None


def text_matches(answer, accepted, tolerance):
    norm = normalize_text(answer)
    number = parse_number(norm)
    for a in accepted:
        if norm == a:
            return True
        expected = parse_number(a)
        if number is not None and expected is not None and abs(number - expected) <= tolerance + 1e-9:
            return True
    return False


def check(key, value):
    """(fraction of the full answer, fully correct) for a cleaned answer value."""
    t = key['type']
    if t in (Question.POLL, Question.CLOUD, Question.OPEN):
        return 0.0, False
    if t in (Question.SINGLE, Question.TRUEFALSE) or (t == Question.CODE and not key.get('input')):
        ok = value in key['correct']
        return float(ok), ok
    if t == Question.MULTI:
        correct = set(key['correct'])
        if not correct:
            return 0.0, False
        chosen = set(value)
        fraction = max(0.0, (len(chosen & correct) - len(chosen - correct)) / len(correct))
        return fraction, chosen == correct
    if t == Question.ORDER:
        ok = value == key['correct']
        return float(ok), ok
    if t == Question.WORD:
        ok = normalize_text(value) == key['word']
        return float(ok), ok
    if t in (Question.TEXT, Question.CODE):
        ok = text_matches(value, key['answers'], key['tolerance'])
        return float(ok), ok
    if t == Question.SLIDER:
        distance = abs(value - key['answer'])
        if distance <= key['tolerance'] + 1e-9:
            return 1.0, True
        # Partial points fade out over a fifth of the scale beyond the tolerance.
        spread = max((key['max'] - key['min']) * 0.2, 1e-9)
        return max(0.0, 1 - (distance - key['tolerance']) / spread), False
    if t == Question.PIN:
        ok = math.hypot(value['x'] - key['x'], value['y'] - key['y']) <= key['r']
        return float(ok), ok
    return 0.0, False


def scored(key):
    return key['type'] not in Question.UNSCORED and key['weight'] > 0


def points(key, fraction, correct, elapsed, streak):
    """Points for an answer given `elapsed` seconds after the question opened.

    `streak` is how many scored questions in a row the player answered right before this one.
    """
    if not scored(key) or fraction <= 0:
        return 0
    limit = max(key['time'], 1)
    elapsed = min(max(elapsed, 0), limit)
    base = BASE_POINTS * (1 - elapsed / (2 * limit)) * key['weight'] * fraction
    bonus = min(STREAK_STEP * streak, STREAK_MAX) if correct else 0
    return int(round(base)) + bonus
