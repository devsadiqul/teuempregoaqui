from datetime import timedelta
from django.db import models
from django.utils import timezone

PRIVATE_TTL = timedelta(hours=24)


class TriState(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    IN_PROGRESS = "in_progress", "In Progress"


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

    class TargetCountry(models.TextChoices):
        PORTUGAL = "PT", "Portugal"
        SPAIN = "ES", "Spain"
        FRANCE = "FR", "France"
        GERMANY = "DE", "Germany"
        ITALY = "IT", "Italy"
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
    expires_at = models.DateTimeField(null=True, blank=True)

    full_name = models.CharField(max_length=255)
    country_of_birth = models.CharField(max_length=100, blank=True)
    current_nationality = models.CharField(max_length=100, blank=True)
    country_of_residence = models.CharField(max_length=100, blank=True)
    city_of_residence = models.CharField(max_length=100, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    linkedin_profile = models.URLField(blank=True)

    immigration_status = models.CharField(max_length=30, choices=ImmigrationStatus.choices)
    target_country = models.CharField(max_length=10, choices=TargetCountry.choices)
    work_authorization = models.CharField(max_length=12, choices=TriState.choices, blank=True)
    residency_authorization = models.CharField(max_length=12, choices=TriState.choices, blank=True)

    current_occupation = models.CharField(max_length=255, blank=True)
    years_experience = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Optional. If blank, derived from previous positions' dates.")
    international_experience = models.BooleanField(default=False)

    willing_to_relocate = models.BooleanField(default=False)
    willing_to_change_country = models.BooleanField(default=False)
    preferred_work_model = models.CharField(
        max_length=15, choices=WorkModel.choices, default=WorkModel.NO_PREFERENCE
    )

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
    country_of_qualification = models.CharField(max_length=100, blank=True)

    # Linked to the official INEP institution database (apps.education.Institution).
    # PROTECT so an institution can't be deleted while candidate records reference it.
    institution = models.ForeignKey(
        "education.Institution", on_delete=models.PROTECT,
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
        max_length=12, choices=Recognition.choices, default=Recognition.DONT_KNOW
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
    country = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    key_responsibilities = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    international = models.BooleanField(default=False)

    class Meta:
        db_table = "candidate_work_experience"


class CandidateLanguage(models.Model):
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
    level = models.CharField(max_length=10, choices=CEFR.choices)

    class Meta:
        db_table = "candidate_language"
        unique_together = ("profile", "language")


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
    proficiency = models.PositiveSmallIntegerField(null=True, blank=True)

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

    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="practice_credentials"
    )
    country = models.CharField(max_length=100)
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

    class Meta:
        db_table = "candidate_practice_credential"
        unique_together = ("profile", "country")
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.country}: recognition={self.recognition_status}, "
            f"regulated_profession={self.regulated_profession_status}"
        )