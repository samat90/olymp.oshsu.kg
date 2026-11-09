"""Quizzes written by a language model: Google Gemini (free tier), Groq as the spare.

Keys live outside git: settings QUIZ_AI_GEMINI_KEY / QUIZ_AI_GROQ_KEY (local_settings.py or the environment)
or the misc config items `ai_gemini_key` / `ai_groq_key` in the admin. The model answers with JSON; every
question goes through the editor's own checks (clean_question), broken ones are dropped.
"""
import json
import logging
import os
import random
import re
import time

import requests
from django.conf import settings

from judge.models.interface import MiscConfig
from judge.models.quiz import Question
from judge.utils.quiz_import import QuestionError, clean_question, problems

logger = logging.getLogger('judge.quiz_ai')

GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent'
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
# 3-flash-preview answers in ~15 s; the newest flash is often overloaded (503 or no answer). 2.5 is closed to new keys.
GEMINI_MODELS = ('gemini-3-flash-preview', 'gemini-flash-latest', 'gemini-flash-lite-latest')
GROQ_MODELS = ('openai/gpt-oss-120b',)  # spare only: fast, but weaker on facts, especially in Kyrgyz
BATCH = 10            # questions asked in one request: shorter answers, fewer broken ones
TIMEOUT = 60          # seconds for one request (10 questions take ~15 s; an overloaded model may never answer)
MIN_COUNT, MAX_COUNT = 3, 30
MAX_DETAILS = 5000    # characters of the author's description (may hold ready questions)
LANGUAGE_NAMES = {'ru': 'русском', 'ky': 'кыргызском (кириллица)', 'en': 'английском'}
LEVELS = {'easy': 'лёгкие, для начинающих', 'medium': 'средней сложности', 'hard': 'сложные, с подвохом, для сильных'}
AI_TYPES = (Question.SINGLE, Question.TRUEFALSE, Question.MULTI, Question.ORDER, Question.TEXT, Question.SLIDER,
            Question.WORD, Question.CODE)
TIMES = {Question.SINGLE: 20, Question.TRUEFALSE: 15, Question.MULTI: 30, Question.ORDER: 30, Question.TEXT: 30,
         Question.SLIDER: 25, Question.WORD: 30, Question.CODE: 40}


class AIError(Exception):
    """Generation failed (the details go to the log)."""


class RateLimited(AIError):
    def __init__(self, wait):
        super().__init__('rate limited, wait %ss' % wait)
        self.wait = wait


def config(name, misc_key=None, default=''):
    value = getattr(settings, name, None) or os.environ.get(name)
    if not value and misc_key:
        value = MiscConfig.objects.filter(key=misc_key).values_list('value', flat=True).first()
    return str(value or default).strip()


def providers():
    """[(name, key, models)] in the order they are tried."""
    found = []
    gemini = config('QUIZ_AI_GEMINI_KEY', 'ai_gemini_key')
    if gemini:
        model = config('QUIZ_AI_GEMINI_MODEL', 'ai_gemini_model')
        found.append(('gemini', gemini, (model,) if model else GEMINI_MODELS))
    groq = config('QUIZ_AI_GROQ_KEY', 'ai_groq_key')
    if groq:
        model = config('QUIZ_AI_GROQ_MODEL', 'ai_groq_model')
        found.append(('groq', groq, (model,) if model else GROQ_MODELS))
    return found


def is_configured():
    return bool(providers())


def proxies():
    proxy = config('QUIZ_AI_PROXY', 'ai_proxy')
    return {'https': proxy, 'http': proxy} if proxy else None


# ---------------------------------------------------------------- prompt

SYSTEM = """Ты автор живых викторин для школьников и студентов Кыргызстана (игроки отвечают на телефонах на время).
Стиль автора: вопросы интересные и с подвохом, неверные варианты правдоподобные, без очевидных ответов.
Где уместно, используй кыргызские имена (Айбек, Нурлан, Айгерим, Бакыт, Жылдыз, Эрмек, Асель, Тилек) и места
Кыргызстана (Ош, Бишкек, Иссык-Куль, Нарын, Талас, Сулайман-Тоо, Ала-Арча); никогда не пиши «Иванов Иван».
Факты должны быть точными и проверяемыми: если не уверен в факте, не используй его.
Ответ: ТОЛЬКО JSON-объект, без markdown и пояснений вокруг."""

FORMAT = """Формат ответа:
{"title": "короткое название викторины (до 80 символов)",
 "description": "одно предложение о викторине",
 "subject": "предмет одним-двумя словами",
 "questions": [ ... ]}
Каждый вопрос — объект с полями "type", "text" (до 300 символов), "explanation" (1–2 предложения: почему ответ верный),
"weight" (1 обычный, 2 двойные очки, 0 без очков) и полями своего типа:
- "single": "options": [{"text": "...", "correct": true}, ...] — 4 варианта, ровно один верный;
- "multi": "options" — 4–5 вариантов, верных 2–3;
- "truefalse": "answer": true или false (утверждение в "text");
- "order": "options": [{"text": "..."}, ...] — 4–5 пунктов СТРОГО в правильном порядке
  (в "text" сказать, по какому признаку);
- "text": "answers": ["ответ", "вариант написания"] — короткий ответ (одно слово или число);
- "slider": "min", "max", "step", "answer", "tolerance", "unit" — число на шкале (год, высота, процент);
- "word": "word": "СЛОВО" — собрать слово из букв (одно слово до 12 букв, в "text" — подсказка);
- "code": "code": "программа", "language": "python" | "cpp" | "java" | "pascal" | "csharp" | "javascript",
  "options" — 4 варианта вывода программы, ровно один верный. Только если тема про программирование.
Варианты ответа — до 80 символов. Ответы на разные вопросы не должны подсказывать друг друга."""


AUTHOR_RULE = (
    'Если в описании автора есть готовые вопросы, сначала используй их: каждый — отдельным вопросом, '
    'формулировку автора сохрани (исправь только явные опечатки), подбери подходящий тип, напиши верные '
    'варианты или ответы и пояснение. Вопросы автора, которые ещё не использованы, идут первыми. '
    'Только потом добавляй свои вопросы, чтобы набралось нужное количество.')


def user_prompt(topic, details, count, language, level, done):
    lines = [
        'Тема: %s' % topic,
        'Описание и пожелания автора (может содержать готовые вопросы):\n%s' % details if details else '',
        AUTHOR_RULE if details else '',
        'Составь %d вопросов на %s языке. Сложность: %s.' % (count, LANGUAGE_NAMES[language], LEVELS[level]),
        'Типы вопросов смешивай: больше всего "single", также "truefalse", "multi", "order", "text", '
        '"slider", "word"; "code" только для тем о программировании.',
    ]
    if count >= 6 and not done:
        lines.append('Один вопрос сделай с двойными очками (weight 2), один — без очков, для разминки (weight 0).')
    if done:
        lines.append('Эти вопросы уже есть, не повторяй их и их факты:\n- ' + '\n- '.join(done))
    lines.append(FORMAT)
    return '\n'.join(line for line in lines if line)


# ---------------------------------------------------------------- the providers

def post(url, headers, body):
    try:
        response = requests.post(url, headers=headers, json=body, timeout=TIMEOUT, proxies=proxies())
    except requests.RequestException as e:
        raise AIError('network: %s' % e.__class__.__name__)
    if response.status_code == 429:
        wait = response.headers.get('retry-after') or ''
        raise RateLimited(float(wait) if wait.replace('.', '', 1).isdigit() else 20)
    if response.status_code != 200:
        raise AIError('HTTP %d: %s' % (response.status_code, response.text[:300]))
    try:
        return response.json()
    except ValueError:
        raise AIError('not JSON')


def ask_gemini(key, model, system, prompt):
    body = {
        'systemInstruction': {'parts': [{'text': system}]},
        'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0.9, 'responseMimeType': 'application/json', 'maxOutputTokens': 16384},
    }
    data = post(GEMINI_URL % model, {'x-goog-api-key': key}, body)
    try:
        parts = data['candidates'][0]['content']['parts']
    except (KeyError, IndexError, TypeError):
        raise AIError('gemini: no answer (%s)' % str(data)[:300])
    return ''.join(p.get('text', '') for p in parts if not p.get('thought'))


def ask_groq(key, model, system, prompt):
    body = {
        'model': model, 'temperature': 0.8, 'max_completion_tokens': 6000,
        'response_format': {'type': 'json_object'},
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}],
    }
    data = post(GROQ_URL, {'Authorization': 'Bearer %s' % key}, body)
    try:
        return data['choices'][0]['message']['content'] or ''
    except (KeyError, IndexError, TypeError):
        raise AIError('groq: no answer (%s)' % str(data)[:300])


ASK = {'gemini': 'ask_gemini', 'groq': 'ask_groq'}  # looked up at call time


def ask(prompt, deadline):
    """The model's JSON answer: providers and models in order; a rate limit is waited out once."""
    errors = []
    for name, key, models in providers():
        for model in models:
            for attempt in range(2):
                try:
                    data = parse_json(globals()[ASK[name]](key, model, SYSTEM, prompt))
                    logger.info('quiz AI: answered by %s/%s', name, model)
                    return data
                except RateLimited as e:
                    errors.append('%s/%s: %s' % (name, model, e))
                    if attempt or time.monotonic() + e.wait > deadline:
                        break
                    time.sleep(min(e.wait, 60))
                except AIError as e:
                    errors.append('%s/%s: %s' % (name, model, e))
                    break
    logger.warning('quiz AI failed: %s', '; '.join(errors) or 'no keys')
    raise AIError('all providers failed')


def parse_json(text):
    text = (text or '').strip()
    match = re.search(r'```(?:json)?\s*(.*?)```', text, re.S)
    if match:
        text = match.group(1)
    start, end = text.find('{'), text.rfind('}')
    if start < 0 or end < start:
        raise AIError('no JSON object')
    try:
        data = json.loads(text[start:end + 1])
    except ValueError:
        raise AIError('broken JSON')
    if not isinstance(data, dict) or not isinstance(data.get('questions'), list):
        raise AIError('no questions')
    return data


# ---------------------------------------------------------------- answers → editor questions

def short(value, limit):
    return ' '.join(str(value or '').split())[:limit]


def options_of(raw, correct=True):
    result = []
    for item in raw.get('options') or []:
        if isinstance(item, dict):
            text, ok = item.get('text'), item.get('correct', item.get('is_correct'))
        else:
            text, ok = item, False
        text = short(text, 300)
        if text:
            result.append({'text': text, 'is_correct': ok is True and correct})
    return result


def payload(raw):
    """A question from the model in the editor's format, or None."""
    if not isinstance(raw, dict):
        return None
    type = str(raw.get('type') or '').lower()
    if type not in AI_TYPES:
        return None
    try:
        weight = int(raw.get('weight', 1))
    except (TypeError, ValueError):
        weight = 1
    result = {'type': type, 'text': str(raw.get('text') or '').strip()[:2000],
              'explanation': str(raw.get('explanation') or '').strip()[:2000],
              'weight': weight if weight in (0, 1, 2) else 1, 'time_limit': TIMES[type], 'data': {}, 'options': []}
    if type in (Question.SINGLE, Question.MULTI, Question.CODE):
        options = options_of(raw)
        random.shuffle(options)
        result['options'] = options
    elif type == Question.ORDER:
        result['options'] = options_of(raw, correct=False)
    elif type == Question.TRUEFALSE:
        answer = raw.get('answer')
        if isinstance(answer, str):
            answer = answer.strip().lower() in ('true', 'да', 'верно', 'туура', '1')
        result['options'] = [{'text': '', 'is_correct': bool(answer)}, {'text': '', 'is_correct': not answer}]
    elif type == Question.TEXT:
        result['data'] = {'answers': raw.get('answers') or [], 'tolerance': 0}
    elif type == Question.WORD:
        result['data'] = {'word': raw.get('word') or ''}
    elif type == Question.SLIDER:
        result['data'] = {key: raw.get(key) for key in ('min', 'max', 'step', 'answer', 'tolerance', 'unit')}
    if type == Question.CODE:
        result['code'] = str(raw.get('code') or '').rstrip()[:4000]
        language = str(raw.get('language') or 'python').lower()
        result['code_language'] = language.replace('c++', 'cpp').replace('c#', 'csharp')
    return result


def clean(raw):
    """(fields, options) ready to save, or None when the question is broken."""
    question = payload(raw)
    if question is None:
        return None
    try:
        fields, options = clean_question(question)
    except QuestionError:
        return None
    if problems(fields, options, False):
        return None
    if fields['type'] == Question.MULTI and all(o['is_correct'] for o in options):
        return None
    return fields, options


def generate(topic, details, count, language, level):
    """{'title', 'description', 'subject', 'questions': [(fields, options)]}. Raises AIError."""
    count = max(MIN_COUNT, min(MAX_COUNT, count))
    deadline = time.monotonic() + 240
    meta, questions, seen = {}, [], set()
    for _round in range(5):
        need = count - len(questions)
        if need <= 0 or time.monotonic() > deadline:
            break
        done = [fields['text'][:120] for fields, _options in questions]
        try:
            data = ask(user_prompt(topic, details, min(need, BATCH), language, level, done), deadline)
        except AIError:
            if questions:
                break
            raise
        meta = meta or data
        before = len(questions)
        for raw in data['questions']:
            question = clean(raw)
            if question is None:
                continue
            text = question[0]['text'].lower()
            if text in seen:
                continue
            seen.add(text)
            questions.append(question)
            if len(questions) >= count:
                break
        if len(questions) == before:
            break
    if not questions:
        raise AIError('no usable questions')
    # One double-points question and one warm-up without points at most, as the prompt asks.
    for special in (2, 0):
        marked = [fields for fields, _options in questions if fields['weight'] == special]
        for fields in marked[1:] if len(questions) >= 6 else marked:
            fields['weight'] = 1
    return {'title': short(meta.get('title') or topic, 120), 'description': short(meta.get('description'), 2000),
            'subject': short(meta.get('subject'), 60), 'questions': questions}
