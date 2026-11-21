from django.db import migrations

CHILDREN = (
    ('about_us', 'About', '/about/', '^/about'),
    ('terms', 'Terms of use', '/tos/', '^/tos'),
    ('privacy', 'Privacy', '/privacy/', '^/privacy'),
)


def forward(apps, schema_editor):
    """The "About" menu item becomes a drop-down: About, Terms of use, Privacy."""
    items = apps.get_model('judge', 'NavigationBar').objects.using(schema_editor.connection.alias)
    about = items.filter(key='about', parent=None).first()
    if about is None or items.filter(parent=about).exists():
        return
    # Menu items are ordered by tree; the children share the tree of their parent.
    about.lft, about.rght, about.level = 1, 2 + 2 * len(CHILDREN), 0
    about.save()
    for number, (key, label, path, regex) in enumerate(CHILDREN):
        items.filter(key=key).delete()
        items.create(order=number + 1, key=key, label=label, path=path, regex=regex, parent=about,
                     tree_id=about.tree_id, level=1, lft=2 + 2 * number, rght=3 + 2 * number)


def backward(apps, schema_editor):
    items = apps.get_model('judge', 'NavigationBar').objects.using(schema_editor.connection.alias)
    about = items.filter(key='about', parent=None).first()
    items.filter(key__in=[c[0] for c in CHILDREN]).delete()
    if about is not None:
        about.lft, about.rght = 1, 2
        about.save()


class Migration(migrations.Migration):
    dependencies = [
        ('judge', '0188_course_instructor_name'),
    ]
    operations = [migrations.RunPython(forward, backward)]
