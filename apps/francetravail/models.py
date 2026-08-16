from django.db import models


class JobOffer(models.Model):
    source = models.CharField(max_length=30, default="france_travail")
    source_id = models.CharField(max_length=64, unique=True)
    source_url = models.URLField(blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rome_code = models.CharField(max_length=10, db_index=True, blank=True)
    rome_label = models.CharField(max_length=255, blank=True)
    appellation_code = models.CharField(max_length=20, db_index=True, blank=True)
    appellation_label = models.CharField(max_length=255, blank=True)

    esco_uuid = models.UUIDField(null=True, blank=True, db_index=True)

    contract_type = models.CharField(max_length=80, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=5, blank=True)
    salary = models.CharField(max_length=255, blank=True)

    posted_at = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "job_offer"
        indexes = [models.Index(fields=["source", "is_active"])]

    def __str__(self):
        return f"{self.title} ({self.rome_code})"


class TranslationCache(models.Model):
    content_hash = models.CharField(max_length=64, db_index=True)
    target_lang = models.CharField(max_length=5)
    translated = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "translation_cache"
        unique_together = ("content_hash", "target_lang")

    def __str__(self):
        return f"{self.content_hash[:8]}.. -> {self.target_lang}"