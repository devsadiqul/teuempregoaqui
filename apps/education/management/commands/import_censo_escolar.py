# management/commands/import_censo_escolar.py
#
# Usage:
#   python manage.py import_censo_escolar --path datasets/Tabela_Escola_2025.csv
#
# Updated for models_v2.py: resolves Municipality FK and links
# run_by_institution (was CO_IES_OFERTANTE raw string) to an actual
# Institution row when one exists.
#
# IMPORTANT: run this AFTER import_censo_superior, so the Institution
# lookup table used for run_by_institution is populated.

import pandas as pd
from django.core.management.base import BaseCommand
from apps.education.models import School, Institution, Municipality, to_bool


class Command(BaseCommand):
    help = "Import School data from INEP Censo Escolar 2025"

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True)
        parser.add_argument("--chunksize", type=int, default=20000)

    def handle(self, *args, **options):
        path = options["path"]
        chunksize = options["chunksize"]

        institution_pk_by_code = {
            inep_code: pk for inep_code, pk in Institution.objects.values_list("inep_code", "pk")
        }
        if not institution_pk_by_code:
            self.stdout.write(self.style.WARNING(
                "No Institution rows found — run import_censo_superior first if you want "
                "run_by_institution links resolved. Continuing without them."
            ))

        cols = [
            "NU_ANO_CENSO", "CO_ENTIDADE", "NO_ENTIDADE",
            "TP_DEPENDENCIA", "TP_CATEGORIA_ESCOLA_PRIVADA", "TP_LOCALIZACAO",
            "TP_SITUACAO_FUNCIONAMENTO",
            "DS_ENDERECO", "NO_BAIRRO", "CO_CEP",
            "NO_MUNICIPIO", "CO_MUNICIPIO", "SG_UF", "LATITUDE", "LONGITUDE",
            "IN_PROFISSIONALIZANTE", "CO_IES_OFERTANTE",
        ]

        reader = pd.read_csv(path, sep=";", encoding="latin-1", dtype=str, chunksize=chunksize, usecols=cols)

        total_created, total_updated, total_skipped = 0, 0, 0
        for chunk in reader:
            for _, row in chunk.iterrows():
                municipality = Municipality.get_or_create_from_codes(
                    ibge_code=row.get("CO_MUNICIPIO"),
                    name=row.get("NO_MUNICIPIO"),
                    state=row.get("SG_UF"),
                )
                if municipality is None:
                    total_skipped += 1
                    continue

                run_by_institution_id = institution_pk_by_code.get(row.get("CO_IES_OFERTANTE"))

                obj, created = School.objects.update_or_create(
                    inep_code=row.get("CO_ENTIDADE"),
                    defaults={
                        "name": row.get("NO_ENTIDADE", "")[:500],
                        "dependency_type": row.get("TP_DEPENDENCIA"),
                        "private_category": row.get("TP_CATEGORIA_ESCOLA_PRIVADA"),
                        "location_type": row.get("TP_LOCALIZACAO"),
                        "operating_status": row.get("TP_SITUACAO_FUNCIONAMENTO"),
                        "address": row.get("DS_ENDERECO"),
                        "neighborhood": row.get("NO_BAIRRO"),
                        "zip_code": row.get("CO_CEP"),
                        "municipality": municipality,
                        "latitude": row.get("LATITUDE"),
                        "longitude": row.get("LONGITUDE"),
                        "is_vocational": to_bool(row.get("IN_PROFISSIONALIZANTE")),
                        "run_by_institution_id": run_by_institution_id,
                        "census_year": int(row.get("NU_ANO_CENSO", 2025) or 2025),
                    },
                )
                total_created += created
                total_updated += not created

            self.stdout.write(
                f"  ...running total: created={total_created} updated={total_updated} skipped={total_skipped}"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Schools: {total_created} created, {total_updated} updated, {total_skipped} skipped"
        ))