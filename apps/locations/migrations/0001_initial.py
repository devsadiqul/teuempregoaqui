import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("local_name", models.CharField(blank=True, max_length=150)),
                (
                    "location_type",
                    models.CharField(
                        choices=[
                            ("country", "Country"),
                            ("region", "Region"),
                            ("district", "District"),
                            ("municipality", "Municipality"),
                            ("city", "City"),
                            ("subdivision", "Subdivision"),
                        ],
                        max_length=20,
                    ),
                ),
                ("country_code", models.CharField(blank=True, db_index=True, max_length=2)),
                ("depth", models.PositiveSmallIntegerField(default=0)),
                ("external_id", models.CharField(db_index=True, max_length=50, unique=True)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_leaf", models.BooleanField(default=True)),
                ("synced_at", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="locations.location",
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddIndex(
            model_name="location",
            index=models.Index(fields=["country_code", "location_type"], name="cl_locations_country_idx"),
        ),
        migrations.AddIndex(
            model_name="location",
            index=models.Index(fields=["parent", "is_active"], name="cl_locations_parent_idx"),
        ),
    ]
