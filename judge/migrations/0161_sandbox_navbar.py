from django.db import migrations
from django.db.models import Max


def add_link(apps, schema_editor):
    alias = schema_editor.connection.alias
    NavigationBar = apps.get_model('judge', 'NavigationBar')
    if NavigationBar.objects.using(alias).filter(key='sandbox').exists():
        return
    tree_id = (NavigationBar.objects.using(alias).aggregate(m=Max('tree_id'))['m'] or 0) + 1
    NavigationBar.objects.using(alias).create(order=4, key='sandbox', label='Sandbox', path='/sandbox/',
                                              regex='^/sandbox', lft=1, rght=2, tree_id=tree_id, level=0)


def remove_link(apps, schema_editor):
    apps.get_model('judge', 'NavigationBar').objects.using(schema_editor.connection.alias).filter(key='sandbox').delete()


class Migration(migrations.Migration):
    dependencies = [('judge', '0160_workspace')]
    operations = [migrations.RunPython(add_link, remove_link)]
