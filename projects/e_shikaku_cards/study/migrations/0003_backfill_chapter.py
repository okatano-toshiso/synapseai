from django.db import migrations

CH_FORWARD = "順伝播型ネットワーク"


def backfill(apps, schema_editor):
    Card = apps.get_model('study', 'Card')
    Card.objects.filter(chapter='').update(chapter=CH_FORWARD)


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0002_card_chapter'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
