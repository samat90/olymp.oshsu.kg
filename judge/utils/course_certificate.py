"""Course certificate: an A4 landscape page drawn with Pillow (fonts in resources/courses/fonts), saved as PDF."""
import os
from io import BytesIO

from django.conf import settings
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from judge.utils.course_logic import full_name

W, H = 2480, 1754  # A4 landscape at 300 dpi
INK, MUTED, ACCENT, PAPER = (27, 36, 48), (102, 112, 133), (30, 58, 95), (253, 252, 248)
GOLD = (176, 138, 54)

TEXTS = {
    'ru': ('СЕРТИФИКАТ', 'Подтверждается, что', 'успешно прошёл(а) курс', 'Преподаватель', 'Дата', 'Номер',
           'Проверка: отсканируйте код'),
    'ky': ('СЕРТИФИКАТ', 'Бул документ төмөнкүнү тастыктайт:', 'курсун ийгиликтүү аяктады', 'Окутуучу', 'Дата',
           'Номери', 'Текшерүү: кодду сканерлеңиз'),
    'en': ('CERTIFICATE', 'This certifies that', 'has successfully completed the course', 'Teacher', 'Date', 'Number',
           'Verify: scan the code'),
}
MONTHS = {
    'ru': ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
           'декабря'],
    'ky': ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь',
           'декабрь'],
}


def font(bold, size):
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    for folder in (os.path.join(settings.BASE_DIR, 'resources', 'courses', 'fonts'),
                   '/usr/share/fonts/truetype/dejavu'):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit(draw, text, bold, size, width, minimum=40):
    """The largest font (down to `minimum`) in which the text fits the width."""
    while size > minimum:
        f = font(bold, size)
        if draw.textlength(text, font=f) <= width:
            return f
        size -= 4
    return font(bold, minimum)


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


def center(draw, y, text, f, fill):
    draw.text((W / 2, y), text, font=f, fill=fill, anchor='mt')


def format_date(date, lang):
    if lang in MONTHS:
        return '%d %s %d' % (date.day, MONTHS[lang][date.month - 1], date.year)
    return date.strftime('%B %d, %Y').replace(' 0', ' ')


def render_certificate(enrollment, verify_url):
    """The certificate of a finished enrollment as PDF bytes."""
    import qrcode
    course = enrollment.course
    lang = course.language if course.language in TEXTS else 'ru'
    head, certify, completed, teacher, date_label, number_label, scan = TEXTS[lang]
    image = Image.new('RGB', (W, H), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((60, 60, W - 60, H - 60), outline=ACCENT, width=10)
    draw.rectangle((92, 92, W - 92, H - 92), outline=GOLD, width=3)
    center(draw, 190, 'OshSU Olymp', font(True, 46), MUTED)
    center(draw, 270, head, font(True, 130), ACCENT)
    center(draw, 460, certify, font(False, 56), MUTED)
    name = full_name(enrollment.profile.user)
    center(draw, 560, name, fit(draw, name, True, 120, W - 400), INK)
    draw.line((W / 2 - 520, 720, W / 2 + 520, 720), fill=GOLD, width=3)
    center(draw, 770, completed, font(False, 56), MUTED)
    title_font = font(True, 88)
    y = 880
    for line in wrap(draw, '«%s»' % course.title, title_font, W - 460):
        center(draw, y, line, title_font, ACCENT)
        y += 112
    date = timezone.localtime(enrollment.completed_at).date()
    small = font(False, 44)
    draw.text((300, H - 400), '%s: %s' % (date_label, format_date(date, lang)), font=small, fill=INK)
    draw.text((300, H - 330), '%s: %s' % (number_label, enrollment.certificate_code), font=small, fill=INK)
    author = course.author.user.get_full_name().strip() or course.author.username
    draw.text((300, H - 260), '%s: %s' % (teacher, author), font=small, fill=INK)
    qr = qrcode.make(verify_url, box_size=8, border=2).convert('RGB').resize((340, 340))
    image.paste(qr, (W - 300 - 340, H - 520))
    draw.text((W - 300 - 170, H - 160), scan, font=font(False, 30), fill=MUTED, anchor='mt')
    buf = BytesIO()
    image.save(buf, 'PDF', resolution=300.0, title=course.title[:100])
    return buf.getvalue()
