from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone
from judge.models import Contest, ContestProblem, ContestParticipation, Language, Problem, Profile
h = make_password('load-pass-2026')
lang = Language.objects.get(key='PY3')
existing = set(User.objects.filter(username__startswith='load').values_list('username', flat=True))
users = [User(username='load%04d' % i, password=h, first_name='Имя%d' % i, last_name='Фамилия') for i in range(1, 1001) if 'load%04d' % i not in existing]
User.objects.bulk_create(users, batch_size=500)
us = list(User.objects.filter(username__startswith='load'))
have = set(Profile.objects.filter(user__in=us).values_list('user_id', flat=True))
Profile.objects.bulk_create([Profile(user=u, language=lang, timezone='Asia/Bishkek') for u in us if u.id not in have], batch_size=500)
now = timezone.now()
c, _ = Contest.objects.get_or_create(key='load1000', defaults=dict(name='Нагрузочная олимпиада', start_time=now - timezone.timedelta(minutes=10), end_time=now + timezone.timedelta(hours=5), is_visible=True, format_name='ioi16'))
c.start_time = now - timezone.timedelta(minutes=10); c.end_time = now + timezone.timedelta(hours=5); c.anticheat_enabled = False; c.save()
for i, code in enumerate(['000001', '000002', '000003', '001057']):
    ContestProblem.objects.get_or_create(contest=c, problem=Problem.objects.get(code=code), defaults={'points': 100, 'partial': True, 'order': i})
profs = Profile.objects.filter(user__username__startswith='load')
have = set(ContestParticipation.objects.filter(contest=c).values_list('user_id', flat=True))
ContestParticipation.objects.bulk_create([ContestParticipation(contest=c, user=p, real_start=now) for p in profs if p.id not in have], batch_size=500)
parts = {p.user_id: p.id for p in ContestParticipation.objects.filter(contest=c)}
for p in profs:
    if p.current_contest_id != parts[p.id]:
        Profile.objects.filter(id=p.id).update(current_contest_id=parts[p.id])
c.user_count = len(parts); c.save(update_fields=['user_count'])
print('users', profs.count(), 'participations', len(parts))
