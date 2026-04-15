"""Admin-only bulk user generation view."""
import csv
import io
import secrets

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.contrib.auth.models import User

from judge.models import Profile, Language


SAFE_LETTERS = 'abcdefghjkmnpqrstuvwxyz'
SAFE_DIGITS = '23456789'
SAFE_ALPHANUM = SAFE_LETTERS + SAFE_DIGITS


def make_password(length: int = 8) -> str:
    return ''.join(secrets.choice(SAFE_ALPHANUM) for _ in range(length))


class GenerateUsersForm(forms.Form):
    count = forms.IntegerField(
        min_value=1, max_value=1000,
        label=_('Количество участников'),
        help_text=_('Сколько новых пользователей создать (от 1 до 1000).'),
    )
    prefix = forms.CharField(
        max_length=20, initial='user', required=True,
        label=_('Префикс логина'),
        help_text=_('Логины будут prefix001, prefix002, ...'),
    )
    password_length = forms.IntegerField(
        min_value=6, max_value=24, initial=8,
        label=_('Длина пароля'),
    )
    start_number = forms.IntegerField(
        min_value=1, initial=1,
        label=_('Начальный номер'),
        help_text=_('С какого номера начинать (1 = начать с 001).'),
    )


@method_decorator(staff_member_required, name='dispatch')
class GenerateUsersView(FormView):
    form_class = GenerateUsersForm
    template_name = 'admin/generate_users.html'
    success_url = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = _('Генерация участников')
        ctx['generated'] = self.request.session.pop('generated_users', None)
        return ctx

    def form_valid(self, form):
        count = form.cleaned_data['count']
        prefix = form.cleaned_data['prefix']
        password_length = form.cleaned_data['password_length']
        start = form.cleaned_data['start_number']

        default_lang = Language.objects.filter(key='PY3').first() or Language.objects.first()
        created = []
        with transaction.atomic():
            serial = start
            while len(created) < count:
                login = f'{prefix}{serial:03d}'
                serial += 1
                if User.objects.filter(username=login).exists():
                    continue
                password = make_password(password_length)
                user = User.objects.create_user(
                    username=login, password=password, is_active=True,
                )
                Profile.objects.create(
                    user=user, language=default_lang, timezone='Asia/Bishkek',
                )
                created.append({'login': login, 'password': password})

        if 'download' in self.request.POST:
            # CSV download
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(['login', 'password'])
            for u in created:
                writer.writerow([u['login'], u['password']])
            resp = HttpResponse(buf.getvalue(), content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = f'attachment; filename="users_{prefix}.csv"'
            return resp

        self.request.session['generated_users'] = created
        messages.success(self.request, _('Создано пользователей: %(count)d') % {'count': len(created)})
        return self.render_to_response(self.get_context_data(form=self.get_form_class()()))
