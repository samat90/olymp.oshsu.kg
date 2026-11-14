from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('judge', '0181_hide_duplicate_problems'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='avatar',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='avatar'),
        ),
    ]
