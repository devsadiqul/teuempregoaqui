# management/commands/import_censo_superior.py
#
# Usage:
#   python manage.py import_censo_superior --ies-path datasets/MICRODADOS_ED_SUP_IES_2024.CSV --cursos-path datasets/MICRODADOS_CADASTRO_CURSOS_2024.CSV
#
# Updated for models_v2.py: resolves Municipality FK instead of storing raw
# city/state strings on Institution/Course.

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.education.models import Institution, Course, Municipality, to_bool


class Command(BaseCommand):
    help = "Import Institution + Course data from INEP Censo da Educação Superior 2024"

    def add_arguments(self, parser):
        parser.add_argument("--ies-path", required=True)
        parser.add_argument("--cursos-path", required=True)
        parser.add_argument("--chunksize", type=int, default=20000)

    def handle(self, *args, **options):
        self.import_institutions(options["ies_path"])
        self.import_courses(options["cursos_path"], options["chunksize"])

    def import_institutions(self, path):
        self.stdout.write("Reading Institution (IES) file...")
        df = pd.read_csv(path, sep=";", encoding="latin-1", dtype=str)
        self.stdout.write(f"Total institution rows: {len(df)}")

        created, updated, skipped = 0, 0, 0
        with transaction.atomic():
            for _, row in df.iterrows():
                municipality = Municipality.get_or_create_from_codes(
                    ibge_code=row.get("CO_MUNICIPIO_IES"),
                    name=row.get("NO_MUNICIPIO_IES"),
                    state=row.get("SG_UF_IES"),
                    region=row.get("NO_REGIAO_IES"),
                )
                if municipality is None:
                    skipped += 1
                    continue

                obj, is_created = Institution.objects.update_or_create(
                    inep_code=row.get("CO_IES"),
                    defaults={
                        "name": row.get("NO_IES", "")[:500],
                        "acronym": row.get("SG_IES"),
                        "maintainer_name": row.get("NO_MANTENEDORA"),
                        "maintainer_code": row.get("CO_MANTENEDORA"),
                        "academic_org_type": row.get("TP_ORGANIZACAO_ACADEMICA"),
                        "network_type": row.get("TP_REDE"),
                        "admin_category": row.get("TP_CATEGORIA_ADMINISTRATIVA"),
                        "is_community": to_bool(row.get("IN_COMUNITARIA")),
                        "is_confessional": to_bool(row.get("IN_CONFESSIONAL")),
                        "address": row.get("DS_ENDERECO_IES"),
                        "address_number": row.get("DS_NUMERO_ENDERECO_IES"),
                        "neighborhood": row.get("NO_BAIRRO_IES"),
                        "zip_code": row.get("NU_CEP_IES"),
                        "municipality": municipality,
                        "census_year": int(row.get("NU_ANO_CENSO", 2024) or 2024),
                    },
                )
                created += is_created
                updated += not is_created

        self.stdout.write(self.style.SUCCESS(
            f"Institutions: {created} created, {updated} updated, {skipped} skipped (no municipality code)"
        ))

    def import_courses(self, path, chunksize):
        self.stdout.write("Reading Course file (large — streaming in chunks)...")

        institutions = Institution.objects.select_related("municipality").values(
            "inep_code", "pk", "municipality__ibge_code"
        )
        institution_pk_by_code = {}
        institution_home_ibge = {}
        for row in institutions:
            institution_pk_by_code[row["inep_code"]] = row["pk"]
            institution_home_ibge[row["inep_code"]] = row["municipality__ibge_code"]

        total_created, total_skipped = 0, 0
        reader = pd.read_csv(
            path, sep=";", encoding="latin-1", dtype=str, chunksize=chunksize,
            usecols=[
                "NU_ANO_CENSO", "CO_IES", "NO_CURSO", "CO_CURSO",
                "NO_CINE_AREA_GERAL", "NO_CINE_AREA_ESPECIFICA", "NO_CINE_AREA_DETALHADA",
                "TP_GRAU_ACADEMICO", "TP_NIVEL_ACADEMICO", "TP_MODALIDADE_ENSINO",
                "IN_GRATUITO", "NO_MUNICIPIO", "CO_MUNICIPIO", "SG_UF",
            ],
        )

        course_objs = []
        for chunk in reader:
            for _, row in chunk.iterrows():
                co_ies = row.get("CO_IES")
                institution_pk = institution_pk_by_code.get(co_ies)
                if not institution_pk:
                    total_skipped += 1
                    continue

                course_city_code = row.get("CO_MUNICIPIO")
                municipality_id = None
                if course_city_code and course_city_code != institution_home_ibge.get(co_ies):
                    m = Municipality.get_or_create_from_codes(
                        ibge_code=course_city_code,
                        name=row.get("NO_MUNICIPIO"),
                        state=row.get("SG_UF"),
                    )
                    municipality_id = m.pk if m else None

                course_objs.append(Course(
                    institution_id=institution_pk,
                    inep_course_code=row.get("CO_CURSO"),
                    name=row.get("NO_CURSO", "")[:500],
                    cine_area_general=row.get("NO_CINE_AREA_GERAL"),
                    cine_area_specific=row.get("NO_CINE_AREA_ESPECIFICA"),
                    cine_area_detailed=row.get("NO_CINE_AREA_DETALHADA"),
                    degree_type=row.get("TP_GRAU_ACADEMICO"),
                    academic_level=row.get("TP_NIVEL_ACADEMICO"),
                    teaching_modality=row.get("TP_MODALIDADE_ENSINO"),
                    is_free=to_bool(row.get("IN_GRATUITO")),
                    municipality_id=municipality_id,
                    census_year=int(row.get("NU_ANO_CENSO", 2024) or 2024),
                ))

            if len(course_objs) >= chunksize:
                Course.objects.bulk_create(course_objs, batch_size=5000)
                total_created += len(course_objs)
                self.stdout.write(f"  ...{total_created} courses imported so far")
                course_objs = []

        if course_objs:
            Course.objects.bulk_create(course_objs, batch_size=5000)
            total_created += len(course_objs)

        self.stdout.write(self.style.SUCCESS(
            f"Courses: {total_created} created, {total_skipped} skipped (no matching institution)"
        ))