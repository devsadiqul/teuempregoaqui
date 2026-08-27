import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.locations.models import Location


class Command(BaseCommand):
    help = "Sync location data from the oit backbone"

    def add_arguments(self, parser):
        parser.add_argument("--country", type=str, default=None)

    def handle(self, *args, **options):
        base_url = getattr(settings, "OIT_BACKBONE_URL", None)
        if not base_url:
            raise CommandError("OIT_BACKBONE_URL is not configured in settings")

        url = f"{base_url}/locations/export/"
        params = {"country": options["country"]} if options["country"] else {}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        id_map = {}
        for item in sorted(data, key=lambda x: x["depth"]):
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
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "is_active": item["is_active"],
                    "is_leaf": item["is_leaf"],
                },
            )
            id_map[item["id"]] = obj

        self.stdout.write(self.style.SUCCESS(f"Synced {len(data)} locations"))
