# management/commands/import_sistec.py
#
# Usage:
#   python manage.py import_sistec --unidades-path datasets/Sistec_Unidades_Ensino_Brasil_120922.csv --cursos-path datasets/Sistec_Cursos_Tecnicos_ativos_120922.csv
#
# Updated for models_v2.py:
#   - TechnicalCourseUnit now uses a Municipality FK instead of raw city/state.
#   - linked_emec_code / linked_inep_code (raw strings) are now resolved into
#     real FKs: linked_institution -> Institution, linked_school -> School.
#   - TechnicalCourse.unit is a required FK (not nullable) — course rows whose
#     unit_code doesn't match an imported unit are skipped and counted.
#
# Run AFTER import_censo_superior and import_censo_escolar so the
# Institution/School lookup tables used for linking are populated.

import pandas as pd
from django.core.management.base import BaseCommand
from apps.education.models import (
    TechnicalCourseUnit, TechnicalCourse, Institution, School, Municipality,
)


class Command(BaseCommand):
    help = "Import SISTEC technical course units + courses"

    def add_arguments(self, parser):
        parser.add_argument("--unidades-path", required=True)
        parser.add_argument("--cursos-path", required=True)

    def handle(self, *args, **options):
        self.import_units(options["unidades_path"])
        self.import_courses(options["cursos_path"])

    def import_units(self, path):
        self.stdout.write("Reading SISTEC Unidades de Ensino...")
        df = pd.read_csv(path, sep=";", encoding="latin1", dtype=str)
        self.stdout.write(f"Total unit rows: {len(df)}")

        institution_pk_by_code = {
            code: pk for code, pk in Institution.objects.values_list("inep_code", "pk")
        }
        school_pk_by_code = {
            code: pk for code, pk in School.objects.values_list("inep_code", "pk")
        }
        if not institution_pk_by_code and not school_pk_by_code:
            self.stdout.write(self.style.WARNING(
                "No Institution/School rows found — run import_censo_superior and "
                "import_censo_escolar first if you want linked_institution/linked_school "
                "resolved. Continuing without them."
            ))

        created, updated, skipped = 0, 0, 0
        for _, row in df.iterrows():
            municipality = Municipality.get_or_create_from_codes(
                ibge_code=row.get("CO_MUNICIPIO"),
                name=row.get("DS_MUNICIPIO"),
                state=row.get("SG_UF"),
            )
            if municipality is None:
                skipped += 1
                continue

            emec_code = row.get("CODIGO_EMEC_ENDERECO_CAMPUS")
            inep_code = row.get("CODIGO_INEP")
            linked_institution_id = institution_pk_by_code.get(emec_code) if emec_code and emec_code != "0" else None
            linked_school_id = school_pk_by_code.get(inep_code) if inep_code and inep_code != "0" else None

            obj, is_created = TechnicalCourseUnit.objects.update_or_create(
                unit_code=row.get("CO_UNIDADE_ENSINO"),
                defaults={
                    "name": row.get("NO_UNIDADE_ENSINO", "")[:500],
                    "teaching_system": row.get("NO_SISTEMA_ENSINO"),
                    "school_type": row.get("NO_TIPO_ESCOLA"),
                    "admin_dependency": row.get("NO_DEPENDENCIA_ADMIN"),
                    "manager_name": row.get("NOME_GESTOR_UNIDADE_ENSINO"),
                    "zip_code": row.get("CEP"),
                    "street": row.get("LOGRADOURO"),
                    "number": row.get("NUMERO"),
                    "complement": row.get("COMPLEMENTO"),
                    "neighborhood": row.get("BAIRRO"),
                    "email": row.get("EMAIL") or None,
                    "phone": row.get("TELEFONE_01_DA_UNIDADE_DE_ENSINO"),
                    "municipality": municipality,
                    "linked_institution_id": linked_institution_id,
                    "linked_school_id": linked_school_id,
                },
            )
            created += is_created
            updated += not is_created

        self.stdout.write(self.style.SUCCESS(
            f"TechnicalCourseUnit: {created} created, {updated} updated, {skipped} skipped (no municipality code)"
        ))

    def import_courses(self, path):
        self.stdout.write("Reading SISTEC Cursos Técnicos...")
        df = pd.read_csv(path, sep=";", encoding="latin1", dtype=str)
        self.stdout.write(f"Total course rows: {len(df)}")

        unit_pk_by_code = {
            code: pk for code, pk in TechnicalCourseUnit.objects.values_list("unit_code", "pk")
        }

        objs = []
        skipped = 0
        for _, row in df.iterrows():
            unit_code = row.get("CÓDIGO UNIDADE DE ENSINO")
            unit_pk = unit_pk_by_code.get(unit_code)
            if not unit_pk:
                skipped += 1
                continue

            workload_raw = row.get("CARGA HORÁRIA CURSO")
            try:
                workload = int(float(workload_raw)) if workload_raw else None
            except (ValueError, TypeError):
                workload = None

            objs.append(TechnicalCourse(
                unit_id=unit_pk,
                course_code=row.get("CÓDIGO CURSO"),
                course_name=row.get("CURSO", "")[:500],
                subtype=row.get("NOME SUBTIPO DE CURSOS"),
                technological_axis=row.get("EIXO TECNOLÓGICO"),
                modality=row.get("MODALIDADE"),
                workload_hours=workload,
                is_active=(str(row.get("SITUACAO ATIVO", "")).strip().upper() == "ATIVO"),
            ))

        TechnicalCourse.objects.bulk_create(objs, batch_size=5000)
        self.stdout.write(self.style.SUCCESS(
            f"TechnicalCourse: {len(objs)} created, {skipped} skipped (no matching unit)"
        ))