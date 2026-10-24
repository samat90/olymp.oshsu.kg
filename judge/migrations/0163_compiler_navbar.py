from django.db import migrations


def rename(apps, schema_editor):
    apps.get_model('judge', 'NavigationBar').objects.using(schema_editor.connection.alias).filter(key='sandbox') \
        .update(label='Compiler', path='/compiler/', regex='^/compiler')


def rename_back(apps, schema_editor):
    apps.get_model('judge', 'NavigationBar').objects.using(schema_editor.connection.alias).filter(key='sandbox') \
        .update(label='Sandbox', path='/sandbox/', regex='^/sandbox')


class Migration(migrations.Migration):
    dependencies = [('judge', '0162_contest_anticheat')]
    operations = [migrations.RunPython(rename, rename_back)]
