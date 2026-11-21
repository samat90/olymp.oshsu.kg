"""«Условия использования» и «Конфиденциальность»: тексты на русском, кыргызском и английском."""
from django.shortcuts import render
from django.utils.translation import get_language

TITLES = {
    'tos': {'ru': 'Условия использования', 'ky': 'Колдонуу шарттары', 'en': 'Terms of use'},
    'privacy': {'ru': 'Конфиденциальность', 'ky': 'Купуялуулук', 'en': 'Privacy policy'},
}


def text_language(request):
    """Language of the legal text: Russian and Kyrgyz have their own, every other language gets English."""
    code = (get_language() or 'en').split('-')[0]
    return code if code in ('ru', 'ky') else 'en'


def legal_page(request, page):
    lang = text_language(request)
    return render(request, 'legal/%s_%s.html' % (page, lang), {
        'title': TITLES[page][lang], 'page': page, 'lang': lang,
    })


def tos(request):
    return legal_page(request, 'tos')


def privacy(request):
    return legal_page(request, 'privacy')
