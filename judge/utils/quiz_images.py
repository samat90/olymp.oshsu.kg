"""Pictures of quizzes: checked with Pillow, shrunk to 1280 px and about 100 KB, stored under MEDIA_ROOT/quiz/."""
import os
import secrets
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from PIL import Image, ImageOps, UnidentifiedImageError

from judge.models.quiz import Option, Question, Quiz

MAX_UPLOAD = 5 * 1024 * 1024
MAX_SIDE = 1280
TARGET_BYTES = 100 * 1024
MAX_PIXELS = 40 * 1000 * 1000
FORMATS = {'JPEG', 'PNG', 'GIF', 'WEBP', 'BMP', 'MPO'}
QUALITIES = (85, 78, 70, 62, 55, 48, 40)


class ImageError(Exception):
    pass


def has_alpha(image):
    if image.mode in ('RGBA', 'LA', 'PA'):
        alpha = image.getchannel('A')
        return alpha.getextrema()[0] < 255
    return image.mode == 'P' and 'transparency' in image.info


def encode(image, alpha):
    """Encode with lower and lower quality, then smaller size, until the file is small enough."""
    data = b''
    for _attempt in range(4):
        for quality in QUALITIES:
            buf = BytesIO()
            if alpha:
                image.save(buf, 'WEBP', quality=quality, method=4)
            else:
                image.save(buf, 'JPEG', quality=quality, optimize=True, progressive=True)
            data = buf.getvalue()
            if len(data) <= TARGET_BYTES:
                return data
        if max(image.size) <= 480:
            break
        image = image.resize((max(1, int(image.width * .8)), max(1, int(image.height * .8))), Image.LANCZOS)
    return data


def process(upload):
    """Return (bytes, extension) of a cleaned picture, or raise ImageError with a message for the user."""
    if upload is None:
        raise ImageError('Файл не получен')
    if upload.size > MAX_UPLOAD:
        raise ImageError('Картинка больше 5 МБ')
    raw = upload.read(MAX_UPLOAD + 1)
    if len(raw) > MAX_UPLOAD:
        raise ImageError('Картинка больше 5 МБ')
    try:
        probe = Image.open(BytesIO(raw))
        if probe.format not in FORMATS:
            raise ImageError('Нужна картинка JPEG, PNG, GIF или WebP')
        if probe.width * probe.height > MAX_PIXELS:
            raise ImageError('Слишком большая картинка')
        probe.verify()
        image = Image.open(BytesIO(raw))
        image.seek(0)
        image.load()
        image = ImageOps.exif_transpose(image)
    except ImageError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Image.DecompressionBombError):
        raise ImageError('Это не картинка или файл повреждён')
    alpha = has_alpha(image)
    image = image.convert('RGBA' if alpha else 'RGB')
    image.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    return encode(image, alpha), 'webp' if alpha else 'jpg'


def random_name(ext):
    return '%s.%s' % (secrets.token_hex(10), ext)


def delete_file(field):
    """Remove a stored file once the transaction is committed."""
    if not field:
        return
    storage, name = field.storage, field.name
    transaction.on_commit(lambda: storage.exists(name) and storage.delete(name))


def store(instance, field_name, upload):
    """Process the upload and put it into instance.<field_name>, deleting the old file. Saves the instance."""
    data, ext = process(upload)
    field = getattr(instance, field_name)
    old = field.name
    field.save(random_name(ext), ContentFile(data), save=False)
    instance.save(update_fields=[field_name])
    if old:
        storage = field.storage
        transaction.on_commit(lambda: storage.exists(old) and storage.delete(old))
    return field.url


def clear(instance, field_name):
    field = getattr(instance, field_name)
    if field:
        delete_file(field)
        setattr(instance, field_name, '')
        instance.save(update_fields=[field_name])


def copy_file(field):
    """A new stored copy of a file (for copied quizzes): returns the new name or ''."""
    if not field:
        return ''
    try:
        with field.storage.open(field.name, 'rb') as f:
            content = f.read()
    except OSError:
        return ''
    ext = os.path.splitext(field.name)[1].lstrip('.').lower() or 'jpg'
    return field.storage.save(field.field.upload_to + random_name(ext), ContentFile(content))


@receiver(post_delete, sender=Quiz, dispatch_uid='quiz_cover_delete')
def quiz_deleted(sender, instance, **kwargs):
    delete_file(instance.cover)


@receiver(post_delete, sender=Question, dispatch_uid='quiz_question_image_delete')
def question_deleted(sender, instance, **kwargs):
    delete_file(instance.image)


@receiver(post_delete, sender=Option, dispatch_uid='quiz_option_image_delete')
def option_deleted(sender, instance, **kwargs):
    delete_file(instance.image)
