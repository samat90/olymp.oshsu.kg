"""Local WSL stand only: the site's URLs plus uploaded media (nginx serves /media/ on the server)."""
from django.conf import settings
from django.conf.urls.static import static

from dmoj.urls import handler403, handler404, handler500, urlpatterns  # noqa: F401

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
