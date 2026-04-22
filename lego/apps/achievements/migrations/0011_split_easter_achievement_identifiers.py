from django.db import migrations, models


FORWARD_EASTER_MAPPING = {
    ("easter_winner", 0): ("easter_2024", 0),
    ("easter_winner", 1): ("easter_2025", 0),
    ("easter_winner", 2): ("easter_2025", 1),
    ("easter_winner", 3): ("easter_2026", 0),
    ("easter_winner", 4): ("easter_2026", 1),
    ("easter_winner", 5): ("easter_2026", 2),
}

REVERSE_EASTER_MAPPING = {
    ("easter_2024", 0): ("easter_winner", 0),
    ("easter_2025", 0): ("easter_winner", 1),
    ("easter_2025", 1): ("easter_winner", 2),
    ("easter_2026", 0): ("easter_winner", 3),
    ("easter_2026", 1): ("easter_winner", 4),
    ("easter_2026", 2): ("easter_winner", 5),
}


def _remap_easter_achievements(apps, schema_editor, mapping):
    Achievement = apps.get_model("achievements", "Achievement")
    queryset = Achievement._base_manager.filter(
        identifier__in=["easter_winner", "easter_2024", "easter_2025", "easter_2026"]
    )

    for achievement in queryset.iterator():
        target = mapping.get((achievement.identifier, achievement.level))
        if not target:
            continue

        identifier, level = target
        achievement.identifier = identifier
        achievement.level = level
        achievement.save(update_fields=["identifier", "level"])


def forwards(apps, schema_editor):
    _remap_easter_achievements(apps, schema_editor, FORWARD_EASTER_MAPPING)


def backwards(apps, schema_editor):
    _remap_easter_achievements(apps, schema_editor, REVERSE_EASTER_MAPPING)


class Migration(migrations.Migration):

    dependencies = [
        ("achievements", "0010_alter_achievement_identifier"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.AlterField(
            model_name="achievement",
            name="identifier",
            field=models.CharField(
                choices=[
                    ("christmas_calendar", "christmas_calendar"),
                    ("complete_profile", "complete_profile"),
                    ("easter_2024", "easter_2024"),
                    ("easter_2025", "easter_2025"),
                    ("easter_2026", "easter_2026"),
                    ("event_count", "event_count"),
                    ("event_price", "event_price"),
                    ("event_rank", "event_rank"),
                    ("event_rules", "event_rules"),
                    ("gala_count", "gala_count"),
                    ("genfors_count", "genfors_count"),
                    ("keypress_order", "keypress_order"),
                    ("meeting_hidden", "meeting_hidden"),
                    ("penalty_period", "penalty_period"),
                    ("poll_count", "poll_count"),
                    ("quote_count", "quote_count"),
                ],
                max_length=128,
            ),
        ),
    ]
