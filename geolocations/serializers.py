from django.contrib.gis.geos import Point

from rest_framework import serializers
from rest_framework_gis.serializers import GeometrySerializerMethodField

from geolocations.models import (
    GeoLocation,
    IPTypes,
)
from base.serializers import BaseModelSerializer

from locations.serializers import LocationSerializer


class GeoIP2Serializer(BaseModelSerializer):
    is_in_european_union = serializers.BooleanField(default=False, source='is_eu')
    region = serializers.CharField(max_length=85, allow_blank=True, required=False, source='region_name')

    class Meta:
        model = GeoLocation
        fields = ('coordinates', 'city', 'continent_code', 'continent_name', 'country_code', 'country_name', 'postal_code')


class IPStackSerializer(BaseModelSerializer):
    type = serializers.ChoiceField(choices=IPTypes.choices, allow_blank=True, required=False, source='ip_type')
    zip = serializers.CharField(max_length=12, allow_blank=True, required=False, source='postal_code')
    longitude = serializers.DecimalField(max_digits=7, decimal_places=4, max_value=180, min_value=-180, required=True, write_only=True)
    latitude = serializers.DecimalField(max_digits=6, decimal_places=4, max_value=90, min_value=-90, required=True, write_only=True)
    coordinates = GeometrySerializerMethodField()

    class Meta:
        model = GeoLocation
        exclude = ('ip_type', 'postal_code', 'created_at', 'updated_at')
    
    def get_coordinates(self, obj):
        return Point(obj.latitude, obj.latitude)


class GeoLocationSerializer(BaseModelSerializer):
    location = LocationSerializer(allow_null=True)

    class Meta:
        model = GeoLocation
        fields = '__all__'
