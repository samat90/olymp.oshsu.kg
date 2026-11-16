from django.http import Http404, JsonResponse
from django.views.decorators.cache import never_cache

from judge.utils import online


@never_cache
def online_now(request):
    """Live statistics for the admins' home page; everybody else gets a plain 404."""
    user = request.user
    if not (user.is_authenticated and (user.is_superuser or user.is_staff)):
        raise Http404()
    return JsonResponse(online.get_payload(), json_dumps_params={'ensure_ascii': False})
