from django.contrib.gis import admin

from geolocation.models import (
    Location,
    GeoLocation,
    Language
)

admin.site.register(Location)
admin.site.register(Language)
admin.site.register(GeoLocation)
