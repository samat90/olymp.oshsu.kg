"""«О платформе» page."""
from django.core.cache import cache
from django.shortcuts import render

from judge.models import Contest, Problem, Profile, Quiz


def _stats():
    stats = cache.get('about_stats')
    if stats is None:
        stats = {
            'problems': Problem.objects.filter(is_public=True).count(),
            'users': Profile.objects.filter(is_unlisted=False).count(),
            'contests': Contest.objects.filter(is_visible=True).count(),
        }
        stats['quizzes'] = Quiz.objects.filter(access=Quiz.PUBLIC, is_hidden=False, is_deleted=False).count()
        cache.set('about_stats', stats, 600)
    return stats


def about(request):
    return render(request, 'about.html', {'title': 'О платформе', 'stats': _stats()})
