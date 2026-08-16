from django.core.management.base import BaseCommand, CommandError
from apps.francetravail import services


class Command(BaseCommand):
    help = "Sync active France Travail offers into the JobOffer mirror."

    def add_arguments(self, parser):
        parser.add_argument("--rome", help="ROME metier code, e.g. M1805")
        parser.add_argument("--mots-cles", help="Free-text keywords")
        parser.add_argument("--departement", help="French department code, e.g. 75")
        parser.add_argument("--max", type=int, default=150, dest="max_offers")
        parser.add_argument("--no-purge", action="store_true",
                            help="Skip purging stale offers after sync")

    def handle(self, *args, **opts):
        if not opts["rome"] and not opts["mots_cles"]:
            raise CommandError("Provide --rome or --mots-cles.")

        try:
            stats = services.sync_offers(
                code_rome=opts["rome"],
                mots_cles=opts["mots_cles"],
                departement=opts["departement"],
                max_offers=opts["max_offers"],
            )
        except Exception as exc:
            raise CommandError(f"Sync failed: {exc}")

        self.stdout.write(self.style.SUCCESS(
            f"synced: {stats['seen']} (created {stats['created']}, "
            f"updated {stats['updated']})"))

        if not opts["no_purge"]:
            removed = services.purge_stale(stats["seen_ids"])
            self.stdout.write(f"purged stale offers: {removed}")