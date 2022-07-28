from typing_extensions import Self
from django.contrib.gis.db import models


class IPTypes(models.TextChoices):
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    NOT_PROVIDED = None


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None) -> Self:
        del using

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using='primary',
            update_fields=update_fields)
        
        super().save(
            force_insert=True,
            force_update=force_update,
            using='replica',
            update_fields=update_fields)

        return self.refresh_from_db(fields=('id',))
    
    def delete(self, using=None, keep_parents=False) -> tuple[int, dict[str, int]]:
        del using

        pk = self.pk
        super().delete(using='primary', keep_parents=keep_parents)
        self.pk = pk
        return super().delete(using='replica', keep_parents=keep_parents)

    class Meta:
        abstract = True


class Location(BaseModel):
    geoname_id = models.PositiveIntegerField(null=True)
    capital = models.CharField(max_length=163, blank=True)

    def __repr__(self) -> str:
        return f'{self.geoname_id}-{self.capital}'


class GeoLocation(BaseModel):
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


class Language(BaseModel):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    code = models.CharField(max_length=2, blank=True)
    name = models.CharField(max_length=25, blank=True)
    native = models.CharField(max_length=25, blank=True)

    def __repr__(self) -> str:
        return f'{self.name}-{self.native}'
