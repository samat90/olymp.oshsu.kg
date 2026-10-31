"""«О платформе» page."""
from django.shortcuts import render


def about(request):
    return render(request, 'about.html', {'title': 'О платформе'})
