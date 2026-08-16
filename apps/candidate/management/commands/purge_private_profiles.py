from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.candidate.models import CandidateProfile


class Command(BaseCommand):
    help = "Delete expired PRIVATE-mode candidate profiles (GDPR/LGPD)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Report what would be deleted, delete nothing.")

    def handle(self, *args, **opts):
        expired = CandidateProfile.objects.filter(
            mode=CandidateProfile.Mode.PRIVATE,
            expires_at__lt=timezone.now(),
        )
        count = expired.count()
        if opts["dry_run"]:
            self.stdout.write(f"[dry-run] would delete {count} expired private profile(s).")
            return
        expired.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} expired private profile(s)."))
