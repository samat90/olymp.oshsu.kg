from django.db import migrations


def restore(apps, schema_editor):
    """Results saved before the keystroke check count for records and levels again."""
    apps.get_model('judge', 'TypingResult').objects.using(schema_editor.connection.alias) \
        .filter(checked=False).update(checked=True)


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0178_typing_checked'),
    ]

    operations = [
        migrations.RunPython(restore, migrations.RunPython.noop),
    ]
