from django.contrib.gis.db import models

from base.models import BaseModel


class Language(BaseModel):
    code = models.CharField(max_length=2, db_index=True)
    name = models.CharField(max_length=25)
    native = models.CharField(max_length=25)

    class Meta:
        unique_together = ['code', 'name', 'native']

    def __repr__(self) -> str:
        return f'{self.name}-{self.native}'
