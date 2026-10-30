import io
import os
import secrets

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _

AVATAR_DIR = 'avatars'
AVATAR_SIZE = 256
AVATAR_MAX_BYTES = 5 * 1024 * 1024
AVATAR_MAX_PIXELS = 40_000_000
AVATAR_FORMATS = ('JPEG', 'PNG', 'GIF', 'WEBP', 'BMP')


class AvatarError(Exception):
    pass


def avatar_url(name):
    return settings.MEDIA_URL + name


def _render(upload):
    """Re-encode the upload as a square JPEG, so nothing but pixels reaches /media/."""
    from PIL import Image, ImageOps

    if upload.size > AVATAR_MAX_BYTES:
        raise AvatarError(_('The picture is larger than 5 MB.'))
    try:
        with Image.open(upload) as img:
            if img.format not in AVATAR_FORMATS or img.width * img.height > AVATAR_MAX_PIXELS:
                raise AvatarError(_('Upload a JPG, PNG, GIF or WebP picture.'))
            img.draft('RGB', (AVATAR_SIZE * 2, AVATAR_SIZE * 2))
            img = ImageOps.exif_transpose(img).convert('RGBA')
            img = ImageOps.fit(img, (AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        raise AvatarError(_('Upload a JPG, PNG, GIF or WebP picture.'))

    out = Image.new('RGB', img.size, 'white')
    out.paste(img, mask=img.getchannel('A'))
    buf = io.BytesIO()
    out.save(buf, 'JPEG', quality=88, optimize=True)
    return buf.getvalue()


def _delete(name):
    if name and name.startswith(AVATAR_DIR + '/'):
        try:
            default_storage.delete(name)
        except OSError:
            pass


def set_avatar(profile, upload):
    data = _render(upload)
    name = default_storage.save(os.path.join(AVATAR_DIR, '%d-%s.jpg' % (profile.id, secrets.token_hex(4))),
                                ContentFile(data)).replace(os.sep, '/')
    old, profile.avatar = profile.avatar, name
    profile.save(update_fields=['avatar'])
    _delete(old)


def remove_avatar(profile):
    old, profile.avatar = profile.avatar, ''
    profile.save(update_fields=['avatar'])
    _delete(old)
