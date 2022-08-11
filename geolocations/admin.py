from django.contrib.gis import admin

from geolocations.models import GeoLocation


admin.site.register(GeoLocation)
