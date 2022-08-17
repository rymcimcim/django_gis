from django.contrib.gis.db import models

from base.models import BaseModel

from languages.models import Language


class Location(BaseModel):
    geoname_id = models.PositiveIntegerField(null=True)
    capital = models.CharField(max_length=163, blank=True)
    languages = models.ManyToManyField(Language, blank=True)
    is_eu = models.BooleanField(default=False)

    def __repr__(self) -> str:
        return f'{self.geoname_id}-{self.capital}'
