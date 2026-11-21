from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0185_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='auto_mode',
            field=models.BooleanField(default=False, verbose_name='automatic mode'),
        ),
    ]
