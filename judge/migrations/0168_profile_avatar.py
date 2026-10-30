from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0167_typing_trainer'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='avatar',
                                   help_text='Uploaded picture, relative to MEDIA_ROOT.'),
        ),
    ]
