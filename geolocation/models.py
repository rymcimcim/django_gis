from django.contrib.gis.db import models


class IPTypes(models.TextChoices):
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    NOT_PROVIDED = None


class Location(models.Model):
    geoname_id = models.PositiveIntegerField(null=True)
    capital = models.CharField(max_length=163, blank=True)

    def __repr__(self) -> str:
        return f'{self.geoname_id}-{self.capital}'


class GeoLocation(models.Model):
    ip = models.GenericIPAddressField(null=True)
    ip_type = models.CharField(max_length=4, blank=True, choices=IPTypes.choices)
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


class Language(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    code = models.CharField(max_length=2, blank=True)
    name = models.CharField(max_length=25, blank=True)
    native = models.CharField(max_length=25, blank=True)

    def __repr__(self) -> str:
        return f'{self.name}-{self.native}'
