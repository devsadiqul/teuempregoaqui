import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.crosswalk.models import EscoOccupation, OccupationSkill, SkillLabel

BATCH = 5000


def norm(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].strip().replace("-", "").lower()


class Command(BaseCommand):
    help = "Layer ES/PT occupation and skill labels onto already-loaded ESCO data."

    def add_arguments(self, parser):
        parser.add_argument("--dir", required=True,
                            help="Folder with occupations_<lang>.csv and skills_<lang>.csv")
        parser.add_argument("--langs", default="es,pt")

    @transaction.atomic
    def handle(self, *args, **opts):
        base = Path(opts["dir"])
        langs = [l.strip() for l in opts["langs"].split(",") if l.strip()]
        self._occupations(base, langs)
        self._skills(base, langs)
        self.stdout.write(self.style.SUCCESS("Done."))

    def _occupations(self, base, langs):
        existing = {str(pk).replace("-", "").lower(): pk
                    for pk in EscoOccupation.objects.values_list("pk", flat=True)}
        for lang in langs:
            path = base / f"occupations_{lang}.csv"
            if not path.exists():
                self.stdout.write(f"  (skip) {path.name} not found")
                continue
            field, updates = f"label_{lang}", []
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    pk = existing.get(norm(row["conceptUri"]))
                    if pk is None:
                        continue
                    obj = EscoOccupation(pk=pk)
                    setattr(obj, field, (row.get("preferredLabel") or "")[:255])
                    updates.append(obj)
            EscoOccupation.objects.bulk_update(updates, [field], batch_size=BATCH)
            self.stdout.write(f"  occupation {field}: {len(updates):,} updated")

    def _skills(self, base, langs):
        canon = {str(u).replace("-", "").lower(): u
                for u in OccupationSkill.objects.values_list("skill_uuid", flat=True).distinct()}
        for lang in langs:
            path = base / f"skills_{lang}.csv"
            if not path.exists():
                self.stdout.write(f"  (skip) {path.name} not found")
                continue
            SkillLabel.objects.filter(lang=lang).delete()
            objs = []
            seen = set()
            dupes = 0
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    u = canon.get(norm(row["conceptUri"]))
                    if u is None:
                        continue
                    if u in seen:
                        dupes += 1
                        continue
                    seen.add(u)
                    objs.append(SkillLabel(skill_uuid=u, lang=lang,
                                        label=(row.get("preferredLabel") or "")[:255]))
                    if len(objs) >= BATCH:
                        SkillLabel.objects.bulk_create(objs, batch_size=BATCH)
                        objs = []
            if objs:
                SkillLabel.objects.bulk_create(objs, batch_size=BATCH)
            if dupes:
                self.stdout.write(f"  (note) {dupes:,} duplicate conceptUri rows skipped in {path.name}")
            self.stdout.write(f"  skill labels [{lang}]: "
                            f"{SkillLabel.objects.filter(lang=lang).count():,}")