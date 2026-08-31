from datetime import timedelta
from django.db import models
from django.utils import timezone

from apps.locations.models import Location
from apps.education.models import Institution

PRIVATE_TTL = timedelta(hours=24)


class TriState(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    IN_PROGRESS = "in_progress", "In Progress"


class WorkAuthorizationStatus(models.TextChoices):
    """Simple, self-declared answer to: 'Do you currently have authorization
    to work in the selected country?' Replaces asking users to classify
    themselves under detailed immigration categories they may not fully
    understand (client feedback, Breafing_ago_26)."""
    YES = "yes", "Yes"
    NO = "no", "No"
    PENDING = "pending", "Pending"
    DONT_KNOW = "dont_know", "I don't know"


class EvidenceStatus(models.TextChoices):
    """Provenance/verification status shared across the assessment.
    'No Evidence, No Points, No Inference': a value with status MISSING
    never means the underlying trait is absent, only that the system has
    no sufficient evidence to award points for it."""
    VERIFIED = "verified", "Verified"
    DECLARED_UNVERIFIED = "declared_unverified", "Declared / Unverified"
    MISSING = "missing", "Missing"
    NOT_COMPLIANT = "not_compliant", "Not Compliant"


class SkillLevel(models.TextChoices):
    """Everyday proficiency wording, more intuitive for our initial target
    users than a 1-5 numeric score (client feedback: remove default
    'Proficiency Score 1-5')."""
    BASIC = "basic", "Basic"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
    FLUENT_NATIVE = "fluent_native", "Fluent / Native"


class WillingnessLevel(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    MAYBE = "maybe", "Maybe"


class Nationality(models.Model):
    location = models.OneToOneField(
        Location, on_delete=models.CASCADE, related_name="nationality",
        limit_choices_to={"location_type": "country"},
    )
    demonym = models.CharField(max_length=100)
    demonym_es = models.CharField(max_length=100, blank=True)
    demonym_pt = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "candidate_nationality"
        verbose_name_plural = "Nationalities"

    def __str__(self):
        return f"{self.location.name} -> {self.demonym}"


class CandidateProfile(models.Model):
    class Mode(models.TextChoices):
        PRIVATE = "private", "Private Mode"
        ACCOUNT = "account", "Personal Account Mode"

    class ImmigrationStatus(models.TextChoices):
        EU_CITIZEN = "eu_citizen", "EU Citizen"
        DUAL_CITIZENSHIP = "dual_citizenship", "Dual Citizenship"
        PERMANENT_RESIDENT = "permanent_resident", "Permanent Resident"
        WORK_VISA = "work_visa", "Work Visa Holder"
        STUDENT_VISA = "student_visa", "Student Visa Holder"
        JOB_SEEKER_VISA = "job_seeker_visa", "Job Seeker Visa"
        FAMILY_REUNIFICATION = "family_reunification", "Family Reunification"
        NO_LEGAL_STATUS = "no_legal_status", "No Legal Status"
        OTHER = "other", "Other"

    class WorkModel(models.TextChoices):
        ON_SITE = "on_site", "On-site"
        HYBRID = "hybrid", "Hybrid"
        REMOTE = "remote", "Remote"
        NO_PREFERENCE = "no_preference", "No Preference"

    mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.PRIVATE)
    user_id = models.CharField(max_length=255, blank=True, db_index=True)
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    consent_given = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(
        default=False,
        help_text="Optional marketing-communications consent, kept separate from the "
                   "Privacy Notice / Terms acceptance (client feedback: do not combine "
                   "everything into one generic acceptance).")
    expires_at = models.DateTimeField(null=True, blank=True)
    full_name = models.CharField(
        max_length=255, blank=True,
        help_text="Optional here - primarily belongs to the OIT user account.")
    country_of_birth = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", limit_choices_to={"location_type": "country"},
    )
    current_nationality = models.ForeignKey(
        Nationality, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="profiles",
    )
    country_of_residence = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", limit_choices_to={"location_type": "country"},
    )
    city_of_residence = models.CharField(max_length=100, blank=True)
    age = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Optional - collect only if a specific feature requires it. "
                   "Must never be used as an employment-ranking variable.")
    email = models.EmailField(blank=True, help_text="Can be linked to the OIT account.")
    phone_number = models.CharField(
        max_length=40, blank=True,
        help_text="Not mandatory unless a specific feature requires it.")
    linkedin_profile = models.URLField(blank=True)
    immigration_status = models.CharField(
        max_length=30, choices=ImmigrationStatus.choices, blank=True,
        help_text="Optional, more detailed classification. The primary self-declared "
                   "signal is `work_authorization` below - we avoid forcing users into "
                   "immigration categories they may not fully understand.")
    target_country = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", limit_choices_to={"location_type": "country"},
    )
    work_authorization = models.CharField(
        max_length=12, choices=WorkAuthorizationStatus.choices, blank=True,
        help_text="Self-declared answer to: 'Do you currently have authorization to "
                   "work in the selected country?' TeuEmpregoAqui does not provide an "
                   "individualized legal opinion or determine immigration status.")
    residency_authorization = models.CharField(max_length=12, choices=TriState.choices, blank=True)
    current_occupation = models.CharField(max_length=255, blank=True)
    years_experience = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Optional. If blank, derived from previous positions' dates.")
    international_experience = models.BooleanField(default=False)
    willing_to_relocate = models.BooleanField(default=False)
    willing_to_change_country = models.BooleanField(default=False)
    willing_to_change_occupation = models.CharField(
        max_length=5, choices=WillingnessLevel.choices, blank=True,
        help_text="'Are you willing to work outside your current professional field?'")
    preferred_work_model = models.CharField(
        max_length=15, choices=WorkModel.choices, default=WorkModel.NO_PREFERENCE
    )
    preferred_location = models.CharField(max_length=255, blank=True)
    max_commute_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    expected_salary_min = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Optional. May later interact with Tuacasaaqui housing/cost-of-living data.")
    expected_salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=3, blank=True, default="EUR")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "candidate_profile"

    def save(self, *args, **kwargs):
        if self.mode == self.Mode.PRIVATE and not self.expires_at:
            self.expires_at = timezone.now() + PRIVATE_TTL
        if self.mode == self.Mode.ACCOUNT:
            self.expires_at = None
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at < timezone.now())

    def __str__(self):
        return f"{self.full_name} ({self.get_mode_display()})"


class Education(models.Model):
    class EQFLevel(models.IntegerChoices):
        L3 = 3, "EQF Level 3 - Secondary Education"
        L4 = 4, "EQF Level 4 - Vocational Qualification"
        L5 = 5, "EQF Level 5 - Higher Technical Diploma"
        L6 = 6, "EQF Level 6 - Bachelor's Degree"
        L7 = 7, "EQF Level 7 - Master's Degree"
        L8 = 8, "EQF Level 8 - Doctorate"

    class FieldOfStudy(models.TextChoices):
        JOURNALISM = "journalism_communication", "Journalism & Communication"
        BUSINESS = "business_administration", "Business Administration"
        MARKETING = "marketing", "Marketing"
        ECONOMICS = "economics", "Economics"
        ENGINEERING = "engineering", "Engineering"
        IT = "information_technology", "Information Technology"
        TOURISM = "tourism_hospitality", "Tourism & Hospitality"
        HEALTHCARE = "healthcare", "Healthcare"
        EDUCATION = "education", "Education"
        LAW = "law", "Law"
        OTHER = "other", "Other"

    class Regulated(models.TextChoices):
        YES = "yes", "Yes"
        NO = "no", "No"
        DONT_KNOW = "dont_know", "I Don't Know"

    class Recognition(models.TextChoices):
        YES = "yes", "Yes"
        NO = "no", "No"
        IN_PROGRESS = "in_progress", "In Progress"
        DONT_KNOW = "dont_know", "I Don't Know"

    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="education"
    )
    eqf_level = models.IntegerField(choices=EQFLevel.choices)
    country_of_qualification = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", limit_choices_to={"location_type": "country"},
    )
    institution = models.ForeignKey(
        Institution, on_delete=models.PROTECT,
        null=True, blank=True, related_name="candidate_educations",
        help_text="Selected via the institution autocomplete (apps.education.Institution)."
    )
    degree_name = models.CharField(max_length=255, blank=True)
    field_of_study = models.CharField(max_length=40, choices=FieldOfStudy.choices)
    year_of_completion = models.PositiveSmallIntegerField(null=True, blank=True)
    instruction_language = models.CharField(max_length=60, blank=True)
    regulated_profession = models.CharField(
        max_length=10, choices=Regulated.choices, default=Regulated.DONT_KNOW
    )
    degree_recognized = models.CharField(
        max_length=12, choices=Recognition.choices, default=Recognition.DONT_KNOW,
        help_text="Self-declared and optional - a migrant cannot be expected to know "
                   "whether their qualification is officially recognized abroad. Whether "
                   "recognition is actually required is determined separately by the "
                   "system from official sources (see PracticeCredential.recognition_requirement_status)."
    )
    physical_diploma = models.BooleanField(default=False)
    academic_transcript = models.BooleanField(default=False)
    course_syllabi = models.BooleanField(default=False)
    grades_converted_eu_scale = models.BooleanField(default=False)
    apostille_completed = models.BooleanField(default=False)
    certified_translation = models.BooleanField(default=False)
    recognition_process_started = models.BooleanField(default=False)
    academic_supervisor_confirmed = models.BooleanField(default=False)

    class Meta:
        db_table = "candidate_education"


class WorkExperience(models.Model):
    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="experiences"
    )
    position = models.CharField(max_length=255)
    employer = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", limit_choices_to={"location_type": "country"},
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    key_responsibilities = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    international = models.BooleanField(default=False)

    class Meta:
        db_table = "candidate_work_experience"


class CandidateLanguage(models.Model):
    """Language Skills Assessment (client feedback: no default numeric
    proficiency score; ask Listening/Speaking/Reading/Writing separately
    using Basic/Intermediate/Advanced/Fluent-Native wording). All four
    dimensions are self-declared unless a certificate is attached below."""

    class CEFR(models.TextChoices):
        A1 = "A1", "A1"
        A2 = "A2", "A2"
        B1 = "B1", "B1"
        B2 = "B2", "B2"
        C1 = "C1", "C1"
        C2 = "C2", "C2"
        NATIVE = "native", "Native"

    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="languages"
    )
    language = models.CharField(max_length=60)
    listening = models.CharField(max_length=15, choices=SkillLevel.choices, blank=True)
    speaking = models.CharField(max_length=15, choices=SkillLevel.choices, blank=True)
    reading = models.CharField(max_length=15, choices=SkillLevel.choices, blank=True)
    writing = models.CharField(max_length=15, choices=SkillLevel.choices, blank=True)
    source = models.CharField(
        max_length=20, choices=EvidenceStatus.choices, default=EvidenceStatus.DECLARED_UNVERIFIED,
        help_text="Set to VERIFIED automatically when a matching certificate is on file.")

    _SKILL_TO_CEFR = {
        SkillLevel.BASIC: "A2", SkillLevel.INTERMEDIATE: "B1",
        SkillLevel.ADVANCED: "C1", SkillLevel.FLUENT_NATIVE: "C2",
    }

    class Meta:
        db_table = "candidate_language"
        unique_together = ("profile", "language")

    @property
    def level(self) -> str:
        """Lowest-common-denominator CEFR-equivalent across the four
        dimensions, used only internally for matching against CEFR-scale
        vacancy requirements. The everyday Basic/Intermediate/Advanced/
        Fluent-Native wording remains the source of truth shown to the user."""
        dims = [self.listening, self.speaking, self.reading, self.writing]
        scores = [self._SKILL_TO_CEFR.get(d) for d in dims if d]
        order = ["A1", "A2", "B1", "B2", "C1", "C2", "native"]
        if not scores:
            return ""
        return min(scores, key=lambda s: order.index(s) if s in order else 0)


class CandidateLanguageCertificate(models.Model):
    """Formal language certification, kept distinct from self-declared
    proficiency and from a placement/level test (client feedback §
    'Language tests and certificates'). Optional - self-declared proficiency
    remains valid on its own."""

    candidate_language = models.ForeignKey(
        CandidateLanguage, on_delete=models.CASCADE, related_name="certificates"
    )
    test_name = models.CharField(max_length=120)
    provider = models.CharField(max_length=120, blank=True)
    score = models.CharField(max_length=30, blank=True)
    cefr_level = models.CharField(max_length=10, choices=CandidateLanguage.CEFR.choices, blank=True)
    test_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "candidate_language_certificate"


class CandidateCertification(models.Model):
    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="certifications"
    )
    name = models.CharField(max_length=120)

    class Meta:
        db_table = "candidate_certification"


class CandidateSkill(models.Model):
    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="skills"
    )
    skill_uuid = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=120)
    # No default proficiency value is ever assigned - a skill the user has
    # not rated stays null/unanswered rather than becoming an artificial
    # score (client feedback).
    proficiency = models.PositiveSmallIntegerField(null=True, blank=True)
    source = models.CharField(
        max_length=20, choices=EvidenceStatus.choices, default=EvidenceStatus.DECLARED_UNVERIFIED)

    class Meta:
        db_table = "candidate_skill"
        unique_together = ("profile", "name")


class PracticeCredential(models.Model):
    class RecognitionStatus(models.TextChoices):
        YES = "yes", "Yes"
        NO = "no", "No"
        IN_PROGRESS = "in_progress", "In Progress"
        DONT_KNOW = "dont_know", "I don't Know"

    class RegulatedProfessionStatus(models.TextChoices):
        YES = "yes", "Yes"
        NO = "no", "No"
        IN_PROGRESS = "in_progress", "In Progress"
        DONT_KNOW = "dont_know", "I don't Know"

    class RecognitionRequirement(models.TextChoices):
        """System-determined output (not user input): whether professional
        recognition/registration is required for this occupation in this
        country, based on official/public sources (client feedback:
        'Professional Recognition: REQUIRED / NOT IDENTIFIED AS REQUIRED /
        FURTHER VERIFICATION REQUIRED'). Informational only - not
        individualized legal advice."""
        REQUIRED = "required", "Required"
        NOT_IDENTIFIED_AS_REQUIRED = "not_identified_as_required", "Not Identified as Required"
        FURTHER_VERIFICATION_REQUIRED = "further_verification_required", "Further Verification Required"

    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="practice_credentials"
    )
    country = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", limit_choices_to={"location_type": "country"},
    )
    recognition_status = models.CharField(
        max_length=12,
        choices=RecognitionStatus.choices,
        default=RecognitionStatus.DONT_KNOW,
    )
    regulated_profession_status = models.CharField(
        max_length=12,
        choices=RegulatedProfessionStatus.choices,
        default=RegulatedProfessionStatus.DONT_KNOW,
    )
    recognition_requirement_status = models.CharField(
        max_length=30, choices=RecognitionRequirement.choices, blank=True,
        help_text="System-populated from official sources, not user input.")
    competent_authority = models.CharField(max_length=255, blank=True)
    official_source_url = models.URLField(blank=True)

    class Meta:
        db_table = "candidate_practice_credential"
        unique_together = ("profile", "country")
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.country}: recognition={self.recognition_status}, "
            f"regulated_profession={self.regulated_profession_status}"
        )