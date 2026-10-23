from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('judge', '0155_python314')]
    operations = [
        migrations.AddField(
            model_name='problem', name='difficulty',
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, db_index=True, verbose_name='Difficulty',
                help_text='Difficulty from 1% to 100%. Independent of awarded points.',
                validators=[MinValueValidator(1), MaxValueValidator(100)])),
        migrations.AddField(
            model_name='problem', name='is_listed',
            field=models.BooleanField(default=True, db_index=True, verbose_name='Show in problem archive')),
        migrations.AddConstraint(
            model_name='problem',
            constraint=models.CheckConstraint(
                check=models.Q(difficulty__isnull=True) | models.Q(difficulty__gte=1, difficulty__lte=100),
                name='problem_difficulty_percent_range')),
    ]
