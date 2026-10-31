from django.db import migrations, models
import django.db.models.deletion


def fill_keys(apps, schema_editor):
    Answer = apps.get_model('judge', 'Answer')
    Answer.objects.using(schema_editor.connection.alias).filter(question_key=0).update(
        question_key=models.F('question_id'))


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0173_quiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='question_key',
            field=models.PositiveIntegerField(db_index=True, default=0, verbose_name='question id'),
        ),
        migrations.RunPython(fill_keys, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='answers', to='judge.question', verbose_name='question'),
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together={('player', 'question_key')},
        ),
        migrations.AddField(
            model_name='quiz',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='deleted by the author'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='access',
            field=models.CharField(choices=[('public', 'Открытая'), ('link', 'По ссылке')], default='public', max_length=8, verbose_name='access'),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='snapshot',
            field=models.JSONField(blank=True, default=dict, verbose_name='questions at the start'),
        ),
    ]
