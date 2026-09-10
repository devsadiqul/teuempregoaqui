from django.db import models


class LocationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Location.StatusChoices.ACTIVE)

    def countries(self):
        return self.filter(location_type=Location.LocationType.COUNTRY, is_active=True)

    def children_of(self, parent_id):
        return self.filter(parent_id=parent_id, is_active=True)

    def descendants_of(self, location):
        return self.filter(path__startswith=f"{location.path}/", is_active=True)

    def leaves_for_country(self, country_code):
        return self.filter(country_code=country_code.upper(), is_leaf=True, is_active=True)

    def by_type(self, country_code, location_type):
        return self.filter(country_code=country_code.upper(), location_type=location_type, is_active=True)

    def search(self, query, country_code=None):
        qs = self.filter(is_leaf=True, is_active=True, name__icontains=query)
        if country_code:
            qs = qs.filter(country_code=country_code.upper())
        return qs


class Location(models.Model):
    class LocationType(models.TextChoices):
        COUNTRY = "country", "Country"
        REGION = "region", "Region"
        DISTRICT = "district", "District"
        MUNICIPALITY = "municipality", "Municipality"
        CITY = "city", "City"
        SUBDIVISION = "subdivision", "Subdivision"

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        COMING_SOON = "coming_soon", "Coming Soon"
        PLANNED = "planned", "Planned"

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    name = models.CharField(max_length=150)
    local_name = models.CharField(max_length=150, blank=True)
    location_type = models.CharField(max_length=20, choices=LocationType.choices)
    country_code = models.CharField(max_length=2, db_index=True, blank=True)
    depth = models.PositiveSmallIntegerField(default=0)
    path = models.CharField(max_length=500, db_index=True, blank=True)
    external_id = models.CharField(max_length=50, unique=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, db_index=True)
    is_active = models.BooleanField(default=True)
    is_leaf = models.BooleanField(default=True)
    synced_at = models.DateTimeField(auto_now=True)

    objects = LocationQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        unique_together = ["parent", "name", "location_type"]
        indexes = [
            models.Index(fields=["country_code", "location_type"]),
            models.Index(fields=["parent", "is_active"]),
            models.Index(fields=["path"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"

    def get_ancestors(self):
        ancestors = []
        node = self.parent
        while node:
            ancestors.append(node)
            node = node.parent
        return list(reversed(ancestors))

    def get_full_path(self):
        names = [a.name for a in self.get_ancestors()] + [self.name]
        return " > ".join(names)