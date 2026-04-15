from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations, models


def populate_revisions(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ContentType = apps.get_model('contenttypes', 'ContentType')
    try:
        content_type = ContentType.objects.get(app_label='judge', model='Comment')
    except ObjectDoesNotExist:
        # If you don't have content types, then you obviously haven't had any edited comments.
        # Therefore, it's safe to all revision counts as zero.
        pass
    else:
        if schema_editor.connection.vendor == 'mysql':
            schema_editor.execute("""\
UPDATE `judge_comment` INNER JOIN (
    SELECT CAST(`reversion_version`.`object_id` AS INT) AS `id`, COUNT(*) AS `count`
    FROM `reversion_version`
    WHERE `reversion_version`.`content_type_id` = %s AND
          `reversion_version`.`db` = %s
    GROUP BY 1
) `versions` ON (`judge_comment`.`id` = `versions`.`id`)
SET `judge_comment`.`revisions` = `versions`.`count`;
""", (content_type.id, db_alias))
        else:
            Comment = apps.get_model('judge', 'Comment')
            Version = apps.get_model('reversion', 'Version')
            from django.db.models import Count
            counts = (Version.objects
                      .filter(content_type_id=content_type.id, db=db_alias)
                      .values('object_id')
                      .annotate(count=Count('id')))
            for row in counts:
                try:
                    pk = int(row['object_id'])
                except (TypeError, ValueError):
                    continue
                Comment.objects.filter(pk=pk).update(revisions=row['count'])


class Migration(migrations.Migration):
    dependencies = [
        ('judge', '0145_site_data_batch_prerequisites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='revisions',
            field=models.IntegerField(default=1, verbose_name='revisions'),
        ),
        migrations.RunPython(populate_revisions, migrations.RunPython.noop, atomic=False, elidable=True),
    ]
