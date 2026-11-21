"""Course certificate: an A4 landscape page drawn with Pillow (fonts and logo in resources/courses), saved as PDF."""
import os
from functools import lru_cache
from io import BytesIO

from django.conf import settings
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from judge.utils.course_logic import full_name, instructor_name, short_name

W, H = 2480, 1754  # A4 landscape at 300 dpi
PAPER = (251, 248, 240)
BURGUNDY = (138, 14, 10)
DARK = (92, 10, 8)
GOLD = (176, 138, 54)
INK = (40, 34, 30)
MUTED = (96, 84, 70)

TEXTS = {
    'ru': {
        'org': 'ОШСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ', 'platform': 'Платформа олимпиадного программирования OshSU Olymp',
        'head': 'СЕРТИФИКАТ', 'sub': 'о прохождении онлайн-курса', 'certify': 'Настоящим подтверждается, что',
        'completed': 'успешно освоил(а) программу курса', 'date': 'Дата выдачи', 'number': 'Регистрационный номер',
        'teacher': 'Преподаватель курса', 'verify': 'Проверка подлинности',
    },
    'ky': {
        'org': 'ОШ МАМЛЕКЕТТИК УНИВЕРСИТЕТИ', 'platform': 'OshSU Olymp олимпиадалык программалоо платформасы',
        'head': 'СЕРТИФИКАТ', 'sub': 'онлайн-курсту аяктаганы жөнүндө', 'certify': 'Ушуну менен тастыкталат:',
        'completed': 'төмөнкү курстун программасын ийгиликтүү өздөштүрдү', 'date': 'Берилген күнү',
        'number': 'Каттоо номери', 'teacher': 'Курстун окутуучусу', 'verify': 'Аныктыгын текшерүү',
    },
    'en': {
        'org': 'OSH STATE UNIVERSITY', 'platform': 'OshSU Olymp Competitive Programming Platform',
        'head': 'CERTIFICATE', 'sub': 'of online course completion', 'certify': 'This is to certify that',
        'completed': 'has successfully completed the course', 'date': 'Date of issue',
        'number': 'Registration number', 'teacher': 'Course instructor', 'verify': 'Verify authenticity',
    },
}
MONTHS = {
    'ru': ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
           'декабря'],
    'ky': ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь',
           'декабрь'],
}
FONTS = {'regular': 'LiberationSerif-Regular.ttf', 'bold': 'LiberationSerif-Bold.ttf',
         'italic': 'LiberationSerif-Italic.ttf'}
FALLBACK = {'regular': 'DejaVuSans.ttf', 'bold': 'DejaVuSans-Bold.ttf', 'italic': 'DejaVuSans.ttf'}
FONT_DIRS = (os.path.join(settings.BASE_DIR, 'resources', 'courses', 'fonts'),
             '/usr/share/fonts/truetype/liberation', '/usr/share/fonts/truetype/dejavu')


@lru_cache(maxsize=None)
def font(style, size):
    for names in (FONTS, FALLBACK):
        for folder in FONT_DIRS:
            path = os.path.join(folder, names[style])
            if os.path.isfile(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default()


@lru_cache(maxsize=1)
def logo():
    return Image.open(os.path.join(settings.BASE_DIR, 'resources', 'courses', 'oshsu-badge.png')).convert('RGBA')


def logo_height(height, opacity=1.0):
    mark = logo()
    mark = mark.resize((round(mark.width * height / mark.height), height), Image.LANCZOS)
    if opacity < 1:
        mark.putalpha(mark.getchannel('A').point(lambda a: round(a * opacity)))
    return mark


def fit(draw, text, style, size, width, minimum=40):
    """The largest font (down to `minimum`) in which the text fits the width."""
    while size > minimum:
        f = font(style, size)
        if draw.textlength(text, font=f) <= width:
            return f
        size -= 4
    return font(style, minimum)


def wrap(draw, text, f, width):
    lines, line = [], ''
    for word in text.split():
        trial = (line + ' ' + word).strip()
        if draw.textlength(trial, font=f) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines[:3]


def center(draw, y, text, f, fill, x=W / 2):
    draw.text((x, y), text, font=f, fill=fill, anchor='mt')


def spaced(draw, y, text, f, fill, tracking):
    """Text centred with extra space between letters."""
    widths = [draw.textlength(ch, font=f) for ch in text]
    x = (W - (sum(widths) + tracking * (len(text) - 1))) / 2
    base = y + f.getmetrics()[0]  # one baseline for all letters (a letter with a mark must not shift)
    for ch, width in zip(text, widths):
        draw.text((x, base), ch, font=f, fill=fill, anchor='ls')
        x += width + tracking


def rule(draw, y, half, gap=0):
    """A gold line with a diamond in the middle."""
    cx = W / 2
    draw.line((cx - half, y, cx - gap - 16, y), fill=GOLD, width=3)
    draw.line((cx + gap + 16, y, cx + half, y), fill=GOLD, width=3)
    draw.polygon([(cx, y - 11), (cx + 11, y), (cx, y + 11), (cx - 11, y)], fill=GOLD)


def seal(image, draw, cx, cy, r):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(240, 228, 196), outline=GOLD, width=8)
    draw.ellipse((cx - r + 16, cy - r + 16, cx + r - 16, cy + r - 16), outline=GOLD, width=3)
    mark = logo_height(int(r * 1.15))
    image.paste(mark, (int(cx - mark.width / 2), int(cy - mark.height / 2)), mark)


def format_date(date, lang):
    if lang == 'ky':
        return '%d-%s %d' % (date.day, MONTHS[lang][date.month - 1], date.year)
    if lang in MONTHS:
        return '%d %s %d' % (date.day, MONTHS[lang][date.month - 1], date.year)
    return date.strftime('%B %d, %Y').replace(' 0', ' ')


def render_certificate(enrollment, verify_url):
    """The certificate of a finished enrollment as PDF bytes."""
    import qrcode
    course = enrollment.course
    lang = course.language if course.language in TEXTS else 'ru'
    text = TEXTS[lang]
    image = Image.new('RGBA', (W, H), PAPER + (255,))

    watermark = logo_height(1100, 0.06)
    image.alpha_composite(watermark, ((W - watermark.width) // 2, (H - watermark.height) // 2))

    draw = ImageDraw.Draw(image)
    draw.rectangle((60, 60, W - 60, H - 60), outline=BURGUNDY, width=14)
    draw.rectangle((92, 92, W - 92, H - 92), outline=GOLD, width=3)
    draw.rectangle((106, 106, W - 106, H - 106), outline=GOLD, width=2)

    mark = logo_height(190)
    image.alpha_composite(mark, ((W - mark.width) // 2, 128))
    spaced(draw, 338, text['org'], font('bold', 50), BURGUNDY, 10)
    center(draw, 408, text['platform'], font('italic', 38), MUTED)
    rule(draw, 478, 360, 24)
    spaced(draw, 506, text['head'], font('bold', 150), DARK, 24)
    center(draw, 684, text['sub'], font('italic', 50), MUTED)
    center(draw, 792, text['certify'], font('regular', 48), INK)
    name = full_name(enrollment.profile.user)
    center(draw, 856, name, fit(draw, name, 'bold', 140, W - 500), BURGUNDY)
    draw.line((W / 2 - 520, 1020, W / 2 + 520, 1020), fill=GOLD, width=3)
    center(draw, 1048, text['completed'], font('regular', 48), INK)
    title = '«%s»' % course.title
    title_font = font('bold', 96)
    lines = wrap(draw, title, title_font, W - 500)
    if len(lines) > 2:
        title_font = font('bold', 80)
        lines = wrap(draw, title, title_font, W - 500)
    y = 1130 if len(lines) < 3 else 1118
    for line in lines:
        center(draw, y, line, title_font, DARK)
        y += 108 if len(lines) < 3 else 96

    date = timezone.localtime(enrollment.completed_at).date()
    label, value = font('italic', 34), font('bold', 46)
    for x, key, shown in ((190, 'date', format_date(date, lang)), (640, 'number', enrollment.certificate_code)):
        draw.text((x, 1478), text[key], font=label, fill=MUTED, anchor='lt')
        draw.text((x, 1526), shown, font=value, fill=INK, anchor='lt')
    seal(image, draw, 1250, 1540, 105)

    sx = 1720
    teacher = short_name(instructor_name(course))
    draw.line((sx - 250, 1545, sx + 250, 1545), fill=INK, width=3)
    draw.text((sx, 1558), teacher, font=fit(draw, teacher, 'bold', 46, 500), fill=INK, anchor='mt')
    draw.text((sx, 1612), text['teacher'], font=label, fill=MUTED, anchor='mt')

    qr = qrcode.make(verify_url, box_size=8, border=1).convert('RGB').resize((250, 250))
    image.paste(qr, (W - 190 - 250, 1352))
    draw.text((W - 190 - 125, 1608), text['verify'], font=font('italic', 30), fill=MUTED, anchor='mt')

    buf = BytesIO()
    image.convert('RGB').save(buf, 'PDF', resolution=300.0, title=course.title[:100])
    return buf.getvalue()
