"""Helpers shared by the course files (loaded into every course.py and m*.py by load_courses)."""


def Q(text, options, answer, expl, code=None, type=None):
    """A test question. `answer` is an index, or a list of indexes for several correct options."""
    q = {'text': text, 'options': list(options), 'answer': answer, 'expl': expl}
    if code:
        q['code'] = code
    if type:
        q['type'] = type
    elif isinstance(answer, list):
        q['type'] = 'multi'
    return q


def QN(text, number, expl, code=None):
    """A question answered with a number."""
    return Q(text, [str(number)], 0, expl, code, type='number')


def QT(text, answers, expl, code=None):
    """A question answered with a short text (any of the accepted answers)."""
    return Q(text, answers, 0, expl, code, type='text')


def video(video_id, title, text=''):
    return {'type': 'video', 'title': title, 'video': 'https://www.youtube.com/watch?v=' + video_id, 'text': text}


def pair(title, theory, pitfalls, questions, videos=(), practice='', problems=(), task=None, short=None,
         test_title='Проверьте себя'):
    """A theory lesson (text, mistakes, videos, test) and a practice lesson (problems and a task)."""
    blocks = [{'type': 'text', 'text': theory}, {'type': 'text', 'title': 'Типичные ошибки', 'text': pitfalls}]
    blocks += [video(*v) for v in videos]
    blocks.append({'type': 'test', 'title': test_title, 'questions': questions})
    practice_blocks = []
    if practice:
        practice_blocks.append({'type': 'text', 'text': practice})
    for code, hint in problems:
        practice_blocks.append({'type': 'problem', 'code': code, 'text': hint})
    if task:
        practice_blocks.append({'type': 'assignment', 'title': task[0], 'points': 10, 'text': task[1]})
    return [{'title': title, 'blocks': blocks},
            {'title': 'Практика: ' + (short or title[0].lower() + title[1:]), 'required': False,
             'blocks': practice_blocks}]


def module(title, lessons):
    return {'title': title, 'lessons': lessons}
