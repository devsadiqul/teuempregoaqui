import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.locations.models import Location


class Command(BaseCommand):
    help = "Sync location data from the oit backbone"

    def add_arguments(self, parser):
        parser.add_argument("--country", type=str, default=None)

    def handle(self, *args, **options):
        base_url = getattr(settings, "OIT_BACKBONE_URL", None)
        if not base_url:
            raise CommandError("OIT_BACKBONE_URL is not configured in settings")

        url = f"{base_url}/api/v1/locations/export/"
        params = {"country": options["country"]} if options["country"] else {}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        pending = {item["id"]: item for item in data}
        id_map = {}
        synced_count = 0

        with transaction.atomic():
            while pending:
                ready = [
                    item for item in pending.values()
                    if not item["parent"] or item["parent"] in id_map
                ]
                if not ready:
                    missing_parents = {item["parent"] for item in pending.values()} - id_map.keys()
                    raise CommandError(
                        f"{len(pending)} locations stuck, missing parents: {missing_parents}"
                    )

                for item in ready:
                    parent = id_map.get(item["parent"]) if item["parent"] else None
                    obj, _ = Location.objects.update_or_create(
                        external_id=item["external_id"] or str(item["id"]),
                        defaults={
                            "parent": parent,
                            "name": item["name"],
                            "local_name": item["local_name"],
                            "location_type": item["location_type"],
                            "country_code": item["country_code"],
                            "depth": item["depth"],
                            "path": item["path"],
                            "status": item["status"],
                            "is_active": item["status"] == Location.StatusChoices.ACTIVE,
                            "is_leaf": item["is_leaf"],
                            "latitude": item["latitude"],
                            "longitude": item["longitude"],
                        },
                    )
                    id_map[item["id"]] = obj
                    del pending[item["id"]]
                    synced_count += 1

        self.stdout.write(self.style.SUCCESS(f"Synced {synced_count} locations"))