"""«Руководство пользователя»: инструкции со снимками экрана на русском, кыргызском и английском."""
from django.shortcuts import render
from django.utils.translation import get_language

TITLES = {'ru': 'Руководство пользователя', 'ky': 'Колдонуучунун колдонмосу', 'en': 'User guide'}


def guide_language():
    """Русский и кыргызский тексты свои, остальные языки получают английский."""
    code = (get_language() or 'en').split('-')[0]
    return code if code in ('ru', 'ky') else 'en'


def guide(request):
    lang = guide_language()
    return render(request, 'guide/guide_%s.html' % lang, {'title': TITLES[lang], 'lang': lang})
