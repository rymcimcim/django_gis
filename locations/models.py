from django.contrib.gis.db import models

from base.models import BaseModel

from languages.models import Language


class Location(BaseModel):
    geoname_id = models.PositiveIntegerField(null=True)
    capital = models.CharField(max_length=163, blank=True)
    languages = models.ManyToManyField(Language, blank=True)
    is_eu = models.BooleanField(default=False)

    def __repr__(self) -> str:
        ret = [str(self.id)]
        if self.geoname_id:
            ret.append(str(self.geoname_id))
        if self.capital:
            ret.append(self.capital)
        ret.append(f'is_eu={self.is_eu}')
        return '-'.join([x for x in ret])
