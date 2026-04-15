from django.db import migrations


def fix_visibility(apps, schema_editor):
    Contest = apps.get_model('judge', 'Contest')
    Contest.objects.filter(is_private=True).update(is_private=False, is_organization_private=True)


def reverse_visibility(apps, schema_editor):
    Contest = apps.get_model('judge', 'Contest')
    for c in Contest.objects.all().iterator():
        Contest.objects.filter(pk=c.pk).update(is_private=c.is_organization_private)


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0089_submission_to_contest'),
    ]

    operations = [
        migrations.RunPython(fix_visibility, reverse_visibility, elidable=True),
    ]
