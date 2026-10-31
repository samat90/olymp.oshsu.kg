from django.http import HttpResponse
from django.views.decorators.cache import cache_control

from judge.utils.default_avatar import ornament_svg


@cache_control(public=True, max_age=7 * 24 * 3600)
def default_avatar(request, seed):
    # The picture is made only of fixed strings and numbers; the seed is never echoed back.
    response = HttpResponse(ornament_svg(seed[:150]), content_type='image/svg+xml')
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "default-src 'none'"
    return response
