from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


class Legal(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('privacy_policy', 'Privacy Policy'),
        ('terms_conditions', 'Terms & Conditions'),
        ('disclaimer', 'Disclaimer'),
        ('about_us', 'About Us'),
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('pt', 'Portuguese'),
    ]

    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    title = models.CharField(max_length=255)
    content = models.TextField()
    version = models.CharField(max_length=20, editable=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('document_type', 'language', 'version')]

    def __str__(self):
        return f"{self.get_document_type_display()} [{self.language}] v{self.version}"

    def _get_next_version(self):
        versions = (
            Legal.objects
            .select_for_update()
            .filter(document_type=self.document_type, language=self.language)
            .exclude(pk=self.pk)
            .values_list('version', flat=True)
        )
        if not versions:
            return '1.0.0'
        try:
            last = max(versions, key=lambda v: list(map(int, v.split('.'))))
            major, minor, patch = map(int, last.split('.'))
            return f"{major + 1}.0.0"
        except ValueError:
            return '1.0.0'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                self.version = self._get_next_version()
            else:
                old = Legal.objects.filter(pk=self.pk).values(
                    'title', 'content', 'document_type', 'language'
                ).first()
                changed = old and (
                    old['title'] != self.title or
                    old['content'] != self.content or
                    old['document_type'] != self.document_type or
                    old['language'] != self.language
                )
                if changed:
                    self.version = self._get_next_version()
            super().save(*args, **kwargs)


@receiver(post_save, sender=Legal)
def deactivate_others(sender, instance, **kwargs):
    if instance.is_active:
        Legal.objects.filter(
            document_type=instance.document_type,
            language=instance.language,
            is_active=True
        ).exclude(pk=instance.pk).update(is_active=False)
