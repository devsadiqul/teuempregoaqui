from django.core.management.base import BaseCommand

from apps.education.models import Municipality
from apps.locations.models import Location


class Command(BaseCommand):
    help = "Cross-reference education.Municipality rows to locations.Location (Brazil city nodes)"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        regions = {
            loc.local_name.upper(): loc
            for loc in Location.objects.filter(country_code="BR", location_type="region")
            if loc.local_name
        }

        qs = Municipality.objects.filter(location__isnull=True)
        matched = 0
        unmatched = []

        for muni in qs.iterator():
            region = regions.get(muni.state.upper())
            if not region:
                unmatched.append((muni.ibge_code, muni.name, muni.state, "unknown state"))
                continue

            location = Location.objects.filter(
                country_code="BR", location_type="city",
                parent=region, name__iexact=muni.name.strip(),
            ).first()

            if location:
                matched += 1
                if not dry_run:
                    muni.location = location
                    muni.save(update_fields=["location"])
            else:
                unmatched.append((muni.ibge_code, muni.name, muni.state, "no match"))

        total = matched + len(unmatched)
        suffix = " (dry-run, nothing saved)" if dry_run else ""
        self.stdout.write(self.style.SUCCESS(f"Municipality -> Location: {matched}/{total} matched{suffix}"))
        if unmatched:
            self.stdout.write(self.style.WARNING(f"{len(unmatched)} unmatched:"))
            for code, name, state, reason in unmatched[:30]:
                self.stdout.write(f"  {code}  {name} ({state})  {reason}")
            if len(unmatched) > 30:
                self.stdout.write(f"  ... and {len(unmatched) - 30} more")