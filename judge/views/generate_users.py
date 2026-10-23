"""Admin-only bulk user generation view."""
import csv
import io
import re
import secrets

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from judge.models import Contest, Language, Organization, Profile


SAFE_LETTERS = 'abcdefghjkmnpqrstuvwxyz'
SAFE_DIGITS = '23456789'
SAFE_ALPHANUM = SAFE_LETTERS + SAFE_DIGITS


def make_password(length: int = 8) -> str:
    return ''.join(secrets.choice(SAFE_ALPHANUM) for _ in range(length))


def parse_participants(text):
    """Lines like "Иванов Иван; ОшГУ" (a tab or a comma also works). Returns [(full name, organization)]."""
    people = []
    for line in (text or '').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p.strip() for p in re.split(r'[;\t]', line, maxsplit=1)]
        if len(parts) == 1 and ',' in line:
            parts = [p.strip() for p in line.split(',', 1)]
        name = parts[0]
        org = parts[1] if len(parts) > 1 else ''
        people.append((name[:150], org[:128]))
    return people


def split_name(full_name):
    """"Иванов Иван Иванович" -> last name "Иванов", first name "Иван Иванович"."""
    words = full_name.split()
    if not words:
        return '', ''
    return ' '.join(words[1:])[:150], words[0][:150]


TRANSLIT = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюяөүң',
                    ['a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r',
                     's', 't', 'u', 'f', 'kh', 'ts', 'ch', 'sh', 'sch', '', 'y', '', 'e', 'yu', 'ya', 'o', 'u', 'n']))


def make_slug(name):
    latin = ''.join(TRANSLIT.get(ch, ch) for ch in name.lower())
    return slugify(latin)[:100] or 'org'


def get_organization(name, cache):
    if not name:
        return None
    key = name.lower()
    if key in cache:
        return cache[key]
    org = Organization.objects.filter(name__iexact=name).first() or \
        Organization.objects.filter(short_name__iexact=name).first()
    if org is None:
        slug = make_slug(name)
        base, n = slug, 2
        while Organization.objects.filter(slug=slug).exists():
            slug = '%s-%d' % (base, n)
            n += 1
        org = Organization.objects.create(name=name, slug=slug, short_name=name[:20], about='', is_open=False)
    cache[key] = org
    return org


class GenerateUsersForm(forms.Form):
    participants = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'rows': 8, 'cols': 70,
                                                     'placeholder': 'Иванов Иван; ОшГУ\nПетрова Айгерим; ОшМПУ'}),
        label=_('Participants list'),
        help_text=_('One participant per line: full name, then a semicolon and the university or school. '
                    'If the list is filled in, the number below is ignored.'),
    )
    count = forms.IntegerField(
        min_value=1, max_value=1000, required=False,
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
    contest = forms.ModelChoiceField(
        queryset=Contest.objects.none(), required=False,
        label=_('Add to contest'),
        help_text=_('The new accounts become the only participants allowed into this contest.'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contest'].queryset = Contest.objects.filter(
            end_time__gte=timezone.now() - timezone.timedelta(days=1)).order_by('start_time')

    def clean(self):
        data = super().clean()
        people = parse_participants(data.get('participants'))
        data['people'] = people
        if not people and not data.get('count'):
            raise forms.ValidationError(_('Fill in the participants list or the number of participants.'))
        if len(people) > 1000:
            raise forms.ValidationError(_('At most 1000 participants at a time.'))
        return data


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
        people = form.cleaned_data['people']
        count = len(people) or form.cleaned_data['count']
        prefix = form.cleaned_data['prefix']
        password_length = form.cleaned_data['password_length']
        start = form.cleaned_data['start_number']
        contest = form.cleaned_data['contest']

        default_lang = Language.objects.filter(key='PY3').first() or Language.objects.first()
        orgs = {}
        created = []
        with transaction.atomic():
            serial = start
            while len(created) < count:
                login = f'{prefix}{serial:03d}'
                serial += 1
                if User.objects.filter(username=login).exists():
                    continue
                full_name, org_name = people[len(created)] if people else ('', '')
                first_name, last_name = split_name(full_name)
                password = make_password(password_length)
                user = User.objects.create_user(
                    username=login, password=password, is_active=True,
                    first_name=first_name, last_name=last_name,
                )
                profile = Profile.objects.create(
                    user=user, language=default_lang, timezone='Asia/Bishkek',
                )
                org = get_organization(org_name, orgs)
                if org is not None:
                    profile.organizations.add(org)
                created.append({'login': login, 'password': password, 'name': full_name, 'org': org_name})
                if contest is not None:
                    contest.private_contestants.add(profile)
            if contest is not None and created:
                contest.is_private = True
                contest.save(update_fields=['is_private'])

        if 'download' in self.request.POST:
            buf = io.StringIO()
            buf.write('﻿')  # so that Excel opens Cyrillic correctly
            writer = csv.writer(buf, delimiter=';')
            writer.writerow(['login', 'password', 'name', 'university'])
            for u in created:
                writer.writerow([u['login'], u['password'], u['name'], u['org']])
            resp = HttpResponse(buf.getvalue(), content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = f'attachment; filename="users_{prefix}.csv"'
            return resp

        self.request.session['generated_users'] = created
        msg = _('Создано пользователей: %(count)d') % {'count': len(created)}
        if contest is not None:
            msg += '. ' + str(_('They were added to the contest "%(contest)s".') % {'contest': contest.name})
        messages.success(self.request, msg)
        return self.render_to_response(self.get_context_data(form=self.get_form_class()()))
