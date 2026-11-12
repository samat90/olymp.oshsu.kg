# Compact question DSL for the themed quizzes.
# S: single (first option is correct), TF: true/false, M: multi ('*' marks correct),
# O: order (options in the correct order), W: build a word, T: type the answer, SL: slider.
# img: 'en:Article' / 'ru:Статья' (lead free picture of a Wikipedia article) or 'c:File name.jpg' (Wikimedia Commons).
def S(text, right, *wrong, img=None, w=1, t=20, e=''):
    assert len(wrong) == 3, text
    return dict(type='single', text=text, opts=[right, *wrong], img=img, w=w, t=t, e=e)
def TF(text, value, img=None, w=1, t=15, e=''):
    return dict(type='truefalse', text=text, opts=[value], img=img, w=w, t=t, e=e)
def M(text, opts, img=None, w=1, t=30, e=''):
    return dict(type='multi', text=text, opts=opts, img=img, w=w, t=t, e=e)
def O(text, opts, img=None, w=1, t=30, e=''):
    return dict(type='order', text=text, opts=opts, img=img, w=w, t=t, e=e)
def W(text, word, img=None, w=1, t=30, e=''):
    return dict(type='word', text=text, word=word, img=img, w=w, t=t, e=e)
def T(text, answers, img=None, w=1, t=30, e=''):
    return dict(type='text', text=text, answers=answers, img=img, w=w, t=t, e=e)
def SL(text, lo, hi, step, answer, unit='', tol=0, img=None, w=1, t=25, e=''):
    return dict(type='slider', text=text, slider=dict(min=lo, max=hi, step=step, answer=answer, unit=unit, tolerance=tol), img=img, w=w, t=t, e=e)
def Q(key, title, subject, theme, description, cover, questions):
    return dict(key=key, title=title, subject=subject, theme=theme, description=description, cover=cover, questions=questions)
def C(text, code, lang, right, *wrong, img=None, w=1, t=30, e=''):
    # "What does this program print / where is the bug": code block + 4 options (first is correct).
    assert len(wrong) == 3, text
    return dict(type='code', text=text, code=code, lang=lang, opts=[right, *wrong], img=img, w=w, t=t, e=e)
