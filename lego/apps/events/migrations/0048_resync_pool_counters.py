from django.db import migrations
from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce


def resync_pool_counters(apps, _):
    """
    Repair counters left drifted by the bump paths, which used to move registrations
    into a pool without adjusting `Pool.counter`. Soft-deleted registrations are
    excluded to match `pool.registrations`.
    """
    pool = apps.get_model("events", "Pool")
    registration = apps.get_model("events", "Registration")

    actual_count = (
        registration.objects.filter(pool=OuterRef("pk"), deleted=False)
        .order_by()
        .values("pool")
        .annotate(count=Count("pk"))
        .values("count")
    )

    pool.objects.update(
        counter=Coalesce(
            Subquery(actual_count, output_field=IntegerField()),
            0,
            output_field=IntegerField(),
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0047_alter_event_event_type"),
    ]

    operations = [
        migrations.RunPython(resync_pool_counters, migrations.RunPython.noop),
    ]
