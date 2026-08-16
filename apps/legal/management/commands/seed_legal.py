from django.core.management.base import BaseCommand
from django.db import transaction
from apps.legal.models import Legal
from apps.legal.privacy_content import PRIVACY_POLICY
from apps.legal.terms_content import TERMS_CONDITIONS
from apps.legal.disclaimer_content import DISCLAIMER
from apps.legal.about_content import ABOUT_US

DOCUMENTS = {
    "privacy_policy": PRIVACY_POLICY,
    "terms_conditions": TERMS_CONDITIONS,
    "disclaimer": DISCLAIMER,
    "about_us": ABOUT_US,
}


class Command(BaseCommand):
    help = "Seed the legal app with multilingual (en/es/pt) documents, each active."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete existing legal rows before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["flush"]:
            self.stdout.write("Flushing existing legal rows...")
            Legal.objects.all().delete()

        created, skipped = 0, 0
        for doc_type, by_lang in DOCUMENTS.items():
            for lang, payload in by_lang.items():
                exists = Legal.objects.filter(
                    document_type=doc_type, language=lang).exists()
                if exists:
                    skipped += 1
                    continue
                Legal.objects.create(
                    document_type=doc_type,
                    language=lang,
                    title=payload["title"],
                    content=payload["content"],
                    is_active=True,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Legal seed done: {created} created, {skipped} skipped (already existed)."))
