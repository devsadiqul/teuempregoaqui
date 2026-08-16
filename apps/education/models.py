from django.db import models


TRUE_VALUES = {"1", "SIM", "S", "TRUE"}


def to_bool(val):
    if val is None:
        return False
    return str(val).strip().upper() in TRUE_VALUES


class Municipality(models.Model):
    """
    Shared city/state lookup used by every other table in this app, instead
    of repeating city/state/city_code on each one.
    """
    ibge_code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=2, db_index=True)
    region = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "education_municipality"
        verbose_name_plural = "Municipalities"
        indexes = [models.Index(fields=["state", "name"])]

    def __str__(self):
        return f"{self.name}/{self.state}"

    @classmethod
    def get_or_create_from_codes(cls, ibge_code, name, state, region=""):
        if not ibge_code:
            return None
        obj, _ = cls.objects.get_or_create(
            ibge_code=ibge_code,
            defaults={"name": name or "", "state": state or "", "region": region or ""},
        )
        return obj


class Institution(models.Model):
    """
    Higher education institutions (Universities/Colleges).
    Source: INEP Censo da Educação Superior (official government dataset).
    """
    inep_code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=500, db_index=True)
    acronym = models.CharField(max_length=50, blank=True)
    maintainer_name = models.CharField(max_length=500, blank=True)
    maintainer_code = models.CharField(max_length=20, blank=True)

    academic_org_type = models.CharField(max_length=100, blank=True)
    network_type = models.CharField(max_length=50, blank=True)
    admin_category = models.CharField(max_length=100, blank=True)
    is_community = models.BooleanField(default=False)
    is_confessional = models.BooleanField(default=False)

    address = models.CharField(max_length=500, blank=True)
    address_number = models.CharField(max_length=50, blank=True)
    neighborhood = models.CharField(max_length=200, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    municipality = models.ForeignKey(
        Municipality, on_delete=models.PROTECT, related_name="institutions"
    )

    # Enrichment fields — populated later by controlled crawling, NOT from
    # the government dataset itself.
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    career_center_url = models.URLField(blank=True)
    international_office_url = models.URLField(blank=True)
    enrichment_last_checked = models.DateTimeField(null=True, blank=True)

    census_year = models.IntegerField(default=2024)
    source = models.CharField(max_length=50, default="INEP_CENSO_SUPERIOR")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "education_institution"
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return f"{self.name} ({self.municipality.state})"


class Course(models.Model):
    """
    Higher-education courses tied to an Institution.
    Source: INEP Censo da Educação Superior — cadastro de cursos.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="courses")
    inep_course_code = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=500, db_index=True)

    cine_area_general = models.CharField(max_length=300, blank=True)
    cine_area_specific = models.CharField(max_length=300, blank=True)
    cine_area_detailed = models.CharField(max_length=300, blank=True)

    degree_type = models.CharField(max_length=100, blank=True)
    academic_level = models.CharField(max_length=100, blank=True)
    teaching_modality = models.CharField(max_length=100, blank=True)
    is_free = models.BooleanField(default=False)

    # Only set when the course's city differs from the institution's own
    # (satellite campus). Left null when it matches — avoids duplicating
    # the institution's own municipality on every course row.
    municipality = models.ForeignKey(
        Municipality, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses"
    )

    census_year = models.IntegerField(default=2024)
    source = models.CharField(max_length=50, default="INEP_CENSO_SUPERIOR")

    class Meta:
        db_table = "education_course"
        indexes = [models.Index(fields=["institution", "name"])]

    def __str__(self):
        return f"{self.name} @ {self.institution.name}"


class School(models.Model):
    """
    K-12 / Basic education schools.
    Source: INEP Censo Escolar (official government dataset).
    """
    inep_code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=500, db_index=True)

    dependency_type = models.CharField(max_length=100, blank=True)
    private_category = models.CharField(max_length=100, blank=True)
    location_type = models.CharField(max_length=100, blank=True)
    operating_status = models.CharField(max_length=100, blank=True)

    address = models.CharField(max_length=500, blank=True)
    neighborhood = models.CharField(max_length=200, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    latitude = models.CharField(max_length=50, blank=True)
    longitude = models.CharField(max_length=50, blank=True)

    municipality = models.ForeignKey(
        Municipality, on_delete=models.PROTECT, related_name="schools"
    )

    is_vocational = models.BooleanField(default=False)
    run_by_institution = models.ForeignKey(
        Institution, on_delete=models.SET_NULL, null=True, blank=True, related_name="run_schools"
    )

    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    enrichment_last_checked = models.DateTimeField(null=True, blank=True)

    census_year = models.IntegerField(default=2025)
    source = models.CharField(max_length=50, default="INEP_CENSO_ESCOLAR")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "education_school"
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return f"{self.name} ({self.municipality.state})"


class TechnicalCourseUnit(models.Model):
    """
    Institutions/units offering SISTEC-registered technical courses.
    Source: SISTEC open data (official government dataset).

    Many SISTEC units are the same physical institution already present in
    Institution or School — linked_institution / linked_school connect them
    instead of duplicating name/address/contact data.
    """
    unit_code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=500, db_index=True)

    teaching_system = models.CharField(max_length=100, blank=True)
    school_type = models.CharField(max_length=100, blank=True)
    admin_dependency = models.CharField(max_length=100, blank=True)
    manager_name = models.CharField(max_length=300, blank=True)

    street = models.CharField(max_length=500, blank=True)
    number = models.CharField(max_length=50, blank=True)
    complement = models.CharField(max_length=200, blank=True)
    neighborhood = models.CharField(max_length=200, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    municipality = models.ForeignKey(
        Municipality, on_delete=models.PROTECT, related_name="technical_units"
    )

    linked_institution = models.ForeignKey(
        Institution, on_delete=models.SET_NULL, null=True, blank=True, related_name="technical_units"
    )
    linked_school = models.ForeignKey(
        School, on_delete=models.SET_NULL, null=True, blank=True, related_name="technical_units"
    )

    # SISTEC already provides these — no enrichment crawl needed for this table.
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    source = models.CharField(max_length=50, default="SISTEC")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "education_technical_course_unit"
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return f"{self.name} ({self.municipality.state})"


class StandardCourseName(models.Model):
    """
    Official normalized technical course catalog.
    Source: CNCT — Catálogo Nacional de Cursos Técnicos, 4th edition.
    Used to normalize free-text SISTEC course names into a canonical list
    for the recommendation engine.
    """
    course_name = models.CharField(max_length=300, unique=True)
    technological_axis = models.CharField(max_length=300)
    technological_area = models.CharField(max_length=300, blank=True)
    min_workload_hours = models.IntegerField(null=True, blank=True)
    toc_page = models.IntegerField(null=True, blank=True)

    edition = models.CharField(max_length=50, default="4ª edição (2020, atualizado 2025)")
    source = models.CharField(max_length=50, default="CNCT")

    class Meta:
        db_table = "education_standard_course_name"

    def __str__(self):
        return self.course_name


class TechnicalCourse(models.Model):
    """
    Technical/vocational courses offered — SISTEC.
    Source: SISTEC open data (official government dataset).
    """
    unit = models.ForeignKey(TechnicalCourseUnit, on_delete=models.CASCADE, related_name="courses")

    course_code = models.CharField(max_length=20, blank=True)
    course_name = models.CharField(max_length=500, db_index=True)
    subtype = models.CharField(max_length=100, blank=True)
    technological_axis = models.CharField(max_length=300, blank=True)
    modality = models.CharField(max_length=100, blank=True)
    workload_hours = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    standard_course = models.ForeignKey(
        StandardCourseName, on_delete=models.SET_NULL, null=True, blank=True, related_name="offerings"
    )

    source = models.CharField(max_length=50, default="SISTEC")

    class Meta:
        db_table = "education_technical_course"
        indexes = [models.Index(fields=["course_name"])]

    def __str__(self):
        return f"{self.course_name} @ {self.unit.name}"