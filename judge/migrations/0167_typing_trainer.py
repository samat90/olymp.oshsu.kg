from django.db import migrations, models
from django.db.models import F, Max
import django.db.models.deletion


def add_link(apps, schema_editor):
    """Menu item "Typing" right after "Compiler" (the menu is ordered by tree)."""
    alias = schema_editor.connection.alias
    NavigationBar = apps.get_model('judge', 'NavigationBar')
    items = NavigationBar.objects.using(alias)
    if items.filter(key='typing').exists():
        return
    compiler = items.filter(key='sandbox', parent=None).first()
    if compiler is None:
        tree_id = (items.aggregate(m=Max('tree_id'))['m'] or 0) + 1
    else:
        tree_id = compiler.tree_id + 1
        items.filter(tree_id__gte=tree_id).update(tree_id=F('tree_id') + 1)
    items.create(order=5, key='typing', label='Typing', path='/typing/', regex='^/typing',
                 lft=1, rght=2, tree_id=tree_id, level=0)


def remove_link(apps, schema_editor):
    apps.get_model('judge', 'NavigationBar').objects.using(schema_editor.connection.alias).filter(key='typing').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0166_krsu_languages'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypingResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('lesson', 'lesson'), ('test', 'speed test'), ('code', 'code')], max_length=8, verbose_name='mode')),
                ('layout', models.CharField(choices=[('ru', 'Русская'), ('en', 'English'), ('ky', 'Кыргызча')], max_length=2, verbose_name='layout')),
                ('lesson', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='lesson')),
                ('seconds', models.FloatField(verbose_name='time, s')),
                ('chars', models.PositiveIntegerField(verbose_name='characters')),
                ('errors', models.PositiveIntegerField(verbose_name='errors')),
                ('cpm', models.PositiveIntegerField(db_index=True, verbose_name='characters per minute')),
                ('accuracy', models.FloatField(verbose_name='accuracy, %')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='typing_results', to='judge.profile', verbose_name='user')),
            ],
            options={
                'verbose_name': 'typing result',
                'verbose_name_plural': 'typing results',
                'ordering': ['-created'],
                'indexes': [models.Index(fields=['mode', 'layout', '-cpm'], name='judge_typin_mode_af0230_idx')],
            },
        ),
        migrations.RunPython(add_link, remove_link),
    ]
