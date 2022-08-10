from django.contrib.gis.db import models
from django.contrib.auth.models import User


class IPTypes(models.TextChoices):
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    NOT_PROVIDED = ''


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Language(BaseModel):
    code = models.CharField(max_length=2, db_index=True)
    name = models.CharField(max_length=25)
    native = models.CharField(max_length=25)

    class Meta:
        unique_together = ['code', 'name', 'native']

    def __repr__(self) -> str:
        return f'{self.name}-{self.native}'


class Location(BaseModel):
    geoname_id = models.PositiveIntegerField(null=True)
    capital = models.CharField(max_length=163, blank=True)
    languages = models.ManyToManyField(Language, blank=True)

    def __repr__(self) -> str:
        return f'{self.geoname_id}-{self.capital}'


class GeoLocation(BaseModel):
    ip = models.GenericIPAddressField(null=True)
    ip_type = models.CharField(max_length=4, default=IPTypes.NOT_PROVIDED, choices=IPTypes.choices)
    continent_code = models.CharField(max_length=2)
    continent_name = models.CharField(max_length=13)
    country_code = models.CharField(max_length=2)
    country_name = models.CharField(max_length=56)
    region_code = models.CharField(max_length=2, blank=True)
    region_name = models.CharField(max_length=85, blank=True)
    city = models.CharField(max_length=163, blank=True)
    postal_code = models.CharField(max_length=12, blank=True)
    coordinates = models.PointField()
    location = models.OneToOneField(Location, on_delete=models.SET_NULL, null=True)
    is_eu = models.BooleanField(default=False)

    @property
    def latitude(self) -> float:
        return self.coordinates.x
    
    @property
    def longitude(self) -> float:
        return self.coordinates.y
    
    def __repr__(self) -> str:
        return f'{self.continent_name}-{self.country_name}:{self.latitude},{self.longitude}'
