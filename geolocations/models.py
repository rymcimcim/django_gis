from django.contrib.gis.db import models

from base.models import BaseModel

from locations.models import Location


class IPTypes(models.TextChoices):
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    NOT_PROVIDED = ''


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
