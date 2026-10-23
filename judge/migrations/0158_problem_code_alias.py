from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import judge.models.problem


class Migration(migrations.Migration):
    dependencies = [('judge', '0157_contest_problem_publication')]

    operations = [
        migrations.AlterField(
            model_name='problem', name='code',
            field=models.CharField(blank=True, max_length=20, unique=True,
                                   verbose_name='problem code',
                                   validators=[django.core.validators.RegexValidator(
                                       '^[a-z0-9]+$', 'Problem code must be ^[a-z0-9]+$'),
                                       judge.models.problem.numeric_problem_code_validator],
                                   help_text='A short, unique code for the problem, used in the URL after /problem/'),
        ),
        migrations.CreateModel(
            name='ProblemCodeAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                             related_name='code_aliases', to='judge.problem')),
            ],
        ),
    ]
