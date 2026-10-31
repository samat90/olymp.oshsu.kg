from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from judge.models import Profile
from judge.utils.avatar import avatar_url
from . import registry


@registry.function
def gravatar(email, size=80, default=None):
    """Uploaded picture if there is one, otherwise the shyrdak ornament drawn from the username."""
    if isinstance(email, Profile):
        if default is None:
            default = email.mute
        if email.avatar and not default:
            return avatar_url(email.avatar)
        seed = email.user.username
    elif isinstance(email, AbstractUser):
        profile = getattr(email, 'profile', None)
        if profile is not None and profile.avatar:
            return avatar_url(profile.avatar)
        seed = email.username
    else:
        seed = (email or '').strip().lower()
    return reverse('default_avatar', args=[seed or '_'])
