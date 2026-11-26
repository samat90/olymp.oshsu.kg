"""Quiz statistics and the YouTube video of a question.

The counters are filled from the games already played. Only the new columns and `plays` are written,
nothing is removed: `plays` used to count every finished game, now it skips games without answers.
"""
from django.db import migrations, models

from judge.utils import quiz_stats


def backfill(apps, schema_editor):
    used = {name: apps.get_model('judge', name) for name in ('Player', 'Answer', 'Question')}
    Quiz = apps.get_model('judge', 'Quiz')
    for quiz_id in list(Quiz.objects.values_list('id', flat=True)):
        Quiz.objects.filter(id=quiz_id).update(**quiz_stats.totals(quiz_id, used))


def counter(verbose_name):
    return models.PositiveIntegerField(default=0, verbose_name=verbose_name)


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0191_blog_new_features_post'),
    ]

    operations = [
        migrations.AddField('quiz', 'hosted_plays', counter('games with a host')),
        migrations.AddField('quiz', 'solo_plays', counter('solo games')),
        migrations.AddField('quiz', 'participations', counter('participations')),
        migrations.AddField('quiz', 'hosted_participations', counter('participations in games with a host')),
        migrations.AddField('quiz', 'unique_players', counter('different players')),
        migrations.AddField('quiz', 'answers_counted', counter('answers to questions with a right answer')),
        migrations.AddField('quiz', 'answers_correct', counter('correct answers')),
        migrations.AddField('quiz', 'last_played',
                            models.DateTimeField(blank=True, null=True, verbose_name='last played')),
        migrations.AddField('question', 'youtube_id',
                            models.CharField(blank=True, max_length=11, verbose_name='YouTube video')),
        migrations.AddField('question', 'youtube_start',
                            models.PositiveIntegerField(default=0, verbose_name='video start, s')),
        migrations.RunPython(backfill, migrations.RunPython.noop, elidable=True),
    ]
