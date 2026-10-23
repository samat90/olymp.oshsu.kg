from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('judge', '0156_problem_difficulty')]
    operations = [
        migrations.AddField(
            model_name='contest', name='publish_problems_after_end',
            field=models.BooleanField(default=True, verbose_name='Publish problems after contest',
                help_text='Automatically make contest problems available to everyone after the contest ends.')),
        migrations.AddField(
            model_name='contest', name='problems_published_at',
            field=models.DateTimeField(null=True, blank=True, editable=False)),
    ]
