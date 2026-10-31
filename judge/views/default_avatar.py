from django.http import HttpResponse
from django.views.decorators.cache import cache_control

from judge.utils.default_avatar import default_avatar_svg


@cache_control(public=True, max_age=24 * 3600)
def default_avatar(request, seed):
    # The picture is a constant; the seed only keeps one URL per user.
    response = HttpResponse(default_avatar_svg(seed), content_type='image/svg+xml')
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "default-src 'none'"
    return response
