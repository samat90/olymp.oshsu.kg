from django.db import migrations, models


def merge_modes(apps, schema_editor):
    """"Host with a screen" and "host with a phone remote" became one mode."""
    GameSession = apps.get_model('judge', 'GameSession')
    GameSession.objects.using(schema_editor.connection.alias).filter(mode='remote').update(mode='screen')


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0174_quiz_answers_keep'),
    ]

    operations = [
        migrations.RunPython(merge_modes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='gamesession',
            name='mode',
            field=models.CharField(choices=[('screen', 'С ведущим'), ('auto', 'Автоматически'), ('solo', 'В одиночку')], default='screen', max_length=6, verbose_name='mode'),
        ),
    ]
