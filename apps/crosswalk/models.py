from django.db import models


class EscoOccupation(models.Model):
    esco_uuid = models.UUIDField(primary_key=True)
    code = models.CharField(max_length=20, db_index=True)
    isco_group = models.CharField(max_length=10, db_index=True, blank=True)
    label = models.CharField(max_length=255)
    label_es = models.CharField(max_length=255, blank=True)
    label_pt = models.CharField(max_length=255, blank=True)
    regulated = models.BooleanField(default=False)

    class Meta:
        db_table = "esco_occupation"
        indexes = [models.Index(fields=["label"])]

    def __str__(self):
        return f"{self.code} - {self.label}"

    def localized_label(self, lang="en"):
        if lang == "es" and self.label_es:
            return self.label_es
        if lang == "pt" and self.label_pt:
            return self.label_pt
        return self.label


class OccupationSkill(models.Model):
    ESSENTIAL = "essential"
    OPTIONAL = "optional"

    occupation = models.ForeignKey(
        EscoOccupation, on_delete=models.CASCADE, related_name="skills"
    )
    skill_uuid = models.UUIDField()
    skill_label = models.CharField(max_length=255)
    relation = models.CharField(max_length=20, db_index=True)
    skill_type = models.CharField(max_length=30)

    class Meta:
        db_table = "esco_occupation_skill"
        indexes = [models.Index(fields=["occupation", "relation"])]


class SkillLabel(models.Model):
    skill_uuid = models.UUIDField(db_index=True)
    lang = models.CharField(max_length=5)
    label = models.CharField(max_length=255)

    class Meta:
        db_table = "esco_skill_label"
        unique_together = ("skill_uuid", "lang")
        indexes = [models.Index(fields=["skill_uuid", "lang"])]


class RomeEscoMapping(models.Model):
    rome_appellation_id = models.CharField(max_length=20, db_index=True)
    occupation = models.ForeignKey(
        EscoOccupation, on_delete=models.CASCADE, related_name="rome_mappings"
    )
    rome_label = models.CharField(max_length=255)
    skos_match = models.CharField(max_length=20)

    class Meta:
        db_table = "rome_esco_mapping"
        indexes = [models.Index(fields=["rome_appellation_id"])]