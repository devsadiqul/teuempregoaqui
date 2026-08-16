# management/commands/import_cnct.py
#
# Usage:
#   python manage.py import_cnct --path datasets/cnct_courses.csv
#
# Imports the CNCT (Catálogo Nacional de Cursos Técnicos) standard course
# catalog, parsed from the official PDF. Used to normalize/fuzzy-match
# free-text SISTEC course names against a canonical list.

import pandas as pd
from django.core.management.base import BaseCommand
from apps.education.models import StandardCourseName


class Command(BaseCommand):
    help = "Import CNCT standard course catalog"

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="Path to cnct_courses.csv")

    def handle(self, *args, **options):
        df = pd.read_csv(options["path"])
        self.stdout.write(f"Total CNCT course rows: {len(df)}")

        created, updated = 0, 0
        for _, row in df.iterrows():
            workload = row.get("min_workload_hours")
            workload = int(workload) if pd.notna(workload) else None

            obj, is_created = StandardCourseName.objects.update_or_create(
                course_name=row["course_name"],
                defaults={
                    "technological_axis": row.get("eixo_tecnologico"),
                    "technological_area": row.get("area_tecnologica"),
                    "min_workload_hours": workload,
                    "toc_page": int(row["toc_page"]) if pd.notna(row.get("toc_page")) else None,
                },
            )
            created += is_created
            updated += not is_created

        self.stdout.write(self.style.SUCCESS(
            f"StandardCourseName: {created} created, {updated} updated"
        ))


# --- Optional: fuzzy-match step to link TechnicalCourse -> StandardCourseName ---
# Run this AFTER both import_sistec and import_cnct have completed.
#
# from rapidfuzz import process, fuzz
# from myapp.models import TechnicalCourse, StandardCourseName
#
# standards = list(StandardCourseName.objects.values_list("id", "course_name"))
# standard_names = [s[1] for s in standards]
# standard_ids = {s[1]: s[0] for s in standards}
#
# for course in TechnicalCourse.objects.filter(standard_course__isnull=True).iterator():
#     match, score, _ = process.extractOne(course.course_name, standard_names, scorer=fuzz.token_sort_ratio)
#     if score >= 85:  # tune threshold
#         course.standard_course_id = standard_ids[match]
#         course.save(update_fields=["standard_course"])