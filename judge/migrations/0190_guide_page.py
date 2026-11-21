from django.db import migrations
from django.db.models import F


def forward(apps, schema_editor):
    """The "About" drop-down gets one more item: the user guide (/guide/)."""
    items = apps.get_model('judge', 'NavigationBar').objects.using(schema_editor.connection.alias)
    about = items.filter(key='about', parent=None).first()
    if about is None or items.filter(key='guide').exists():
        return
    children = items.filter(parent=about).order_by('order')
    if not children.exists():
        return
    last = children.last()
    # Menu items are ordered by tree; the children share the tree of their parent.
    items.filter(tree_id=about.tree_id, lft__gt=last.rght).update(lft=F('lft') + 2)
    items.filter(tree_id=about.tree_id, rght__gte=last.rght + 1).update(rght=F('rght') + 2)
    items.create(order=last.order + 1, key='guide', label='User guide', path='/guide/', regex='^/guide',
                 parent=about, tree_id=about.tree_id, level=last.level, lft=last.rght + 1, rght=last.rght + 2)


def backward(apps, schema_editor):
    items = apps.get_model('judge', 'NavigationBar').objects.using(schema_editor.connection.alias)
    items.filter(key='guide').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('judge', '0189_about_submenu'),
    ]
    operations = [migrations.RunPython(forward, backward)]
