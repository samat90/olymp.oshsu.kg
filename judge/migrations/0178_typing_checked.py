from django.db import migrations, models


class Migration(migrations.Migration):
    """Results saved before the keystroke check stay in the history but leave the records."""

    dependencies = [
        ('judge', '0177_upcoming_ioi16_to_ioi'),
    ]

    operations = [
        migrations.AddField(
            model_name='typingresult',
            name='checked',
            field=models.BooleanField(default=False, help_text='Saved with a keystroke log that passed the checks. '
                                      'Only checked results count for records and levels.', verbose_name='checked'),
        ),
    ]
