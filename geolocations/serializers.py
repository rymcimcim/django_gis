from django.contrib.gis.geos import Point

from drf_extra_fields.geo_fields import PointField

from rest_framework import serializers

from rest_framework_gis.serializers import GeometrySerializerMethodField

from base.serializers import BaseModelSerializer
from geolocations.models import (
    GeoLocation,
    IPTypes,
)

from locations.serializers import LocationSerializer


class GeoIP2Serializer(serializers.Serializer):
    city = serializers.CharField(max_length=163, required=False, allow_blank=True, allow_null=True)
    continent_code = serializers.CharField(max_length=2, required=True)
    continent_name = serializers.CharField(max_length=13, required=True)
    country_code = serializers.CharField(max_length=2, required=True)
    country_name = serializers.CharField(max_length=56, required=True)
    is_in_european_union = serializers.BooleanField(default=False)
    longitude = serializers.DecimalField(max_digits=17, decimal_places=14, max_value=180, min_value=-180, required=True, write_only=True)
    latitude = serializers.DecimalField(max_digits=15, decimal_places=13, max_value=90, min_value=-90, required=True, write_only=True)
    postal_code = serializers.CharField(max_length=12, required=False, allow_blank=True, allow_null=True)
    region = serializers.CharField(max_length=2, required=False, allow_blank=True, allow_null=True)

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        ret = {
            'continent_code': internal_value['continent_code'],
            'continent_name': internal_value['continent_name'],
            'country_code': internal_value['country_code'],
            'country_name': internal_value['country_name'],
            'location': {
                'is_eu': internal_value.get('is_in_european_union', False),
            },
            'coordinates': {
                'longitude': internal_value['longitude'],
                'latitude': internal_value['latitude']
            },
        }
        update_dict = {}
        if internal_value.get('city'):
            update_dict.update({'city': internal_value['city']})
        if internal_value.get('postal_code'):
            update_dict.update({'postal_code': internal_value['postal_code']})
        if internal_value.get('region'):
            update_dict.update({'region_code': internal_value['region']})

        ret.update(update_dict)
        return ret

# class GeoIP2Serializer(BaseModelSerializer):
#     coordinates = PointField(required=True)
#     is_in_european_union = serializers.BooleanField(default=False, source='is_eu')

#     class Meta:
#         model = GeoLocation
#         fields = ('coordinates', 'continent_code', 'continent_name', 'country_code', 'country_name', 'is_in_european_union')


class IPStackSerializer(BaseModelSerializer):
    type = serializers.ChoiceField(choices=IPTypes.choices, allow_blank=True, required=False, source='ip_type')
    zip = serializers.CharField(max_length=12, allow_blank=True, required=False, source='postal_code')
    longitude = serializers.DecimalField(max_digits=17, decimal_places=14, max_value=180, min_value=-180, required=True, write_only=True)
    latitude = serializers.DecimalField(max_digits=15, decimal_places=13, max_value=90, min_value=-90, required=True, write_only=True)
    coordinates = GeometrySerializerMethodField()

    class Meta:
        model = GeoLocation
        exclude = ('ip_type', 'postal_code', 'created_at', 'updated_at')
    
    def get_coordinates(self, obj):
        return Point(obj.latitude, obj.latitude)


class GeoLocationSerializer(BaseModelSerializer):
    coordinates = PointField(required=True)

    class Meta:
        model = GeoLocation
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['location'] = LocationSerializer(instance.location).data
        return representation
