from django.contrib.gis import admin

from geolocations.models import (
    Location,
    GeoLocation,
)

admin.site.register(Location)
admin.site.register(GeoLocation)
