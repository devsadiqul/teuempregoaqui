import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.candidate.models import Nationality
from apps.locations.models import Location


class Command(BaseCommand):
    help = "Load demonyms (nationalities.csv) into candidate_nationality, matched to Location by country name."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to nationalities.csv")
        parser.add_argument(
            "--update", action="store_true",
            help="Update demonym fields if the Nationality row already exists.",
        )

    def handle(self, *args, **opts):
        path = Path(opts["file"])
        if not path.exists():
            raise CommandError(f"Missing file: {path}")

        countries = {
            loc.name.strip().lower(): loc
            for loc in Location.objects.filter(location_type="country")
        }

        created = updated = skipped = 0
        unmatched = []

        with open(path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                country_name = (row.get("country_name") or "").strip()
                location = countries.get(country_name.lower())
                if not location:
                    unmatched.append(country_name)
                    continue

                defaults = {
                    "demonym": (row.get("demonym") or "").strip(),
                    "demonym_es": (row.get("demonym_es") or "").strip(),
                    "demonym_pt": (row.get("demonym_pt") or "").strip(),
                }

                obj, was_created = Nationality.objects.get_or_create(
                    location=location, defaults=defaults
                )
                if was_created:
                    created += 1
                elif opts["update"]:
                    for field, value in defaults.items():
                        setattr(obj, field, value)
                    obj.save(update_fields=list(defaults.keys()) + ["updated_at"])
                    updated += 1
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Created: {created}, Updated: {updated}, Skipped (already existed): {skipped}"
        ))
        if unmatched:
            self.stdout.write(self.style.WARNING(
                f"{len(unmatched)} country name(s) had no matching Location: {unmatched}"
            ))