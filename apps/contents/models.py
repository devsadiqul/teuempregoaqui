import uuid
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.locations.models import Location


# Create your models here.
class NewsCategory(models.Model):
    name = models.CharField(max_length=100)
    name_es = models.CharField(max_length=100, blank=True, null=True)
    name_pt = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=120, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Position in the list (0 is first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "News Categories"
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['order'], name='unique_newscategory_order')
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)


    def localized_name(self, lang="en"):
        lang = (lang or "en").lower()[:2]
        if lang == "es" and self.name_es:
            return self.name_es
        if lang == "pt" and self.name_pt:
            return self.name_pt
        return self.name

    def __str__(self):
        return self.name


class News(models.Model):
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, related_name='news')
    author_id = models.CharField(max_length=255, db_index=True)
    author_name = models.CharField(max_length=255, blank=True, null=True)
    author_avatar_url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=255)
    title_es = models.CharField(max_length=255, blank=True, null=True)
    title_pt = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    location = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='news/thumbnails/')
    content = models.TextField()
    content_es = models.TextField(blank=True, null=True)
    content_pt = models.TextField(blank=True, null=True)
    read_time = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Auto-calculated read time in minutes"
    )
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "News"
        ordering = ['-created_at']


    def localized_title(self, lang="en"):
        lang = (lang or "en").lower()[:2]
        if lang == "es" and self.title_es:
            return self.title_es
        if lang == "pt" and self.title_pt:
            return self.title_pt
        return self.title

    def localized_content(self, lang="en"):
        lang = (lang or "en").lower()[:2]
        if lang == "es" and self.content_es:
            return self.content_es
        if lang == "pt" and self.content_pt:
            return self.content_pt
        return self.content

    def calculate_read_time(self):
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:8]}")
        self.read_time = self.calculate_read_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ArticleCategory(models.Model):
    name = models.CharField(max_length=100)
    name_es = models.CharField(max_length=100, blank=True, null=True)
    name_pt = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=120, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Position in the list (0 is first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Article Category"
        verbose_name_plural = "Article Categories"
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['order'], name='unique_articlecategory_order')
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)


    def localized_name(self, lang="en"):
        lang = (lang or "en").lower()[:2]
        if lang == "es" and self.name_es:
            return self.name_es
        if lang == "pt" and self.name_pt:
            return self.name_pt
        return self.name

    def __str__(self):
        return self.name


class Article(models.Model):
    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles'
    )
    title = models.CharField(max_length=255)
    title_es = models.CharField(max_length=255, blank=True, null=True)
    title_pt = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    content = models.TextField()
    content_es = models.TextField(blank=True, null=True)
    content_pt = models.TextField(blank=True, null=True)
    read_time = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Auto-calculated read time in minutes"
    )
    official_source_label = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="e.g. SEF / AIMA"
    )
    official_source_url = models.URLField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Article"
        verbose_name_plural = "Articles"


    def localized_title(self, lang="en"):
        lang = (lang or "en").lower()[:2]
        if lang == "es" and self.title_es:
            return self.title_es
        if lang == "pt" and self.title_pt:
            return self.title_pt
        return self.title

    def localized_content(self, lang="en"):
        lang = (lang or "en").lower()[:2]
        if lang == "es" and self.content_es:
            return self.content_es
        if lang == "pt" and self.content_pt:
            return self.content_pt
        return self.content

    def calculate_read_time(self):
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:8]}")
        self.read_time = self.calculate_read_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class OfficialSource(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_pt = models.TextField(blank=True, null=True)
    url = models.URLField()
    icon = models.ImageField(upload_to='official_sources/icons/')
    country = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", limit_choices_to={"location_type": "country"},
        help_text="Leave blank for sources that aren't country-specific (e.g. EU-wide).",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['order'], name='unique_officialsource_order')
        ]
        verbose_name = "Official Source"
        verbose_name_plural = "Official Sources"

    def localized_description(self, lang="en"):
        lang = (lang or "en").lower()[:2]
        if lang == "es" and self.description_es:
            return self.description_es
        if lang == "pt" and self.description_pt:
            return self.description_pt
        return self.description

    def __str__(self):
        return self.name



class FAQ(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('pt', 'Portuguese'),
    ]

    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['language', 'order'],
                                    name='unique_faq_language_order')
        ]

    def __str__(self):
        return f"[{self.language}] {self.question}"



class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('bug_report', 'Bug report'),
        ('feature_request', 'Feature request'),
        ('data_issue', 'Data issue'),
        ('ux_feedback', 'UX feedback'),
        ('other', 'Other'),
    ]

    user_id = models.CharField(max_length=255, db_index=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Star rating from 1 to 5"
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False, help_text="For internal tracking")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        return f"{self.category} - {self.rating} Stars"