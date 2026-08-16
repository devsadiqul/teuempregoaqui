import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.crosswalk.models import EscoOccupation, OccupationSkill, RomeEscoMapping

BATCH = 5000
EURES_SKIP = 16
EURES_ENCODING = "latin-1"


def uuid_from_uri(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].strip()


class Command(BaseCommand):
    help = "Load ESCO occupations/skills and the France ROME->ESCO mapping."

    def add_arguments(self, parser):
        parser.add_argument("--dir", required=True, help="Folder with the raw CSVs")
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete existing crosswalk rows before loading",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        base = Path(opts["dir"])
        for fname in ("occupations_en.csv", "occupationSkillRelations_en.csv",
                      "EURESmapping_occs_FR.csv"):
            if not (base / fname).exists():
                raise CommandError(f"Missing file: {base / fname}")

        if opts["flush"]:
            self.stdout.write("Flushing existing rows...")
            RomeEscoMapping.objects.all().delete()
            OccupationSkill.objects.all().delete()
            EscoOccupation.objects.all().delete()

        valid_uuids = self._load_occupations(base / "occupations_en.csv")
        self._load_skills(base / "occupationSkillRelations_en.csv", valid_uuids)
        self._load_mapping(base / "EURESmapping_occs_FR.csv", valid_uuids)
        self.stdout.write(self.style.SUCCESS("Done."))

    def _load_occupations(self, path: Path) -> set:
        occ_map = {}
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                u = uuid_from_uri(row["conceptUri"])
                regulated = row.get("regulatedProfessionNote", "").strip().endswith("/regulated")
                occ_map[u] = EscoOccupation(
                    esco_uuid=u,
                    code=(row.get("code") or "")[:20],
                    isco_group=(row.get("iscoGroup") or "")[:10],
                    label=(row.get("preferredLabel") or "")[:255],
                    regulated=regulated,
                )
        objs = list(occ_map.values())
        EscoOccupation.objects.bulk_create(objs, batch_size=BATCH)
        reg = sum(o.regulated for o in objs)
        self.stdout.write(f"  esco_occupation       : {len(objs):>7,} ({reg} regulated)")
        return set(occ_map.keys())

    def _load_skills(self, path: Path, valid: set):
        objs, skipped = [], 0
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                occ = uuid_from_uri(row["occupationUri"])
                if occ not in valid:
                    skipped += 1
                    continue
                objs.append(OccupationSkill(
                    occupation_id=occ,
                    skill_uuid=uuid_from_uri(row["skillUri"]),
                    skill_label=(row.get("skillLabel") or "")[:255],
                    relation=(row.get("relationType") or "")[:20],
                    skill_type=(row.get("skillType") or "")[:30],
                ))
                if len(objs) >= BATCH:
                    OccupationSkill.objects.bulk_create(objs, batch_size=BATCH)
                    objs = []
        if objs:
            OccupationSkill.objects.bulk_create(objs, batch_size=BATCH)
        msg = f"  esco_occupation_skill : {OccupationSkill.objects.count():>7,}"
        if skipped:
            msg += f" ({skipped} orphan rows skipped)"
        self.stdout.write(msg)

    def _load_mapping(self, path: Path, valid: set):
        objs, skipped = [], 0
        with open(path, newline="", encoding=EURES_ENCODING) as f:
            reader = csv.reader(f, delimiter=";")
            for _ in range(EURES_SKIP):
                next(reader, None)
            next(reader, None)
            for r in reader:
                if len(r) < 9 or not r[0]:
                    continue
                occ = uuid_from_uri(r[0])
                if occ not in valid:
                    skipped += 1
                    continue
                objs.append(RomeEscoMapping(
                    rome_appellation_id=(r[5] or "")[:20],
                    occupation_id=occ,
                    rome_label=(r[6] or "")[:255],
                    skos_match=(r[8] or "").replace("skos:", "")[:20],
                ))
        RomeEscoMapping.objects.bulk_create(objs, batch_size=BATCH)
        msg = f"  rome_esco_mapping     : {len(objs):>7,}"
        if skipped:
            msg += f" ({skipped} orphan rows skipped)"
        self.stdout.write(msg)