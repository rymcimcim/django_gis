from drf_extra_fields.geo_fields import PointField

from rest_framework import serializers

from base.serializers import BaseModelSerializer
from geolocations.models import (
    GeoLocation,
    IPTypes,
)
from locations.models import Location

from locations.serializers import LocationSerializer, LocationWithLanguagesSerializer


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
        location = Location.objects.create(is_eu=internal_value.get('is_in_european_union', False))
        ret = {
            'continent_code': internal_value['continent_code'],
            'continent_name': internal_value['continent_name'],
            'country_code': internal_value['country_code'],
            'country_name': internal_value['country_name'],
            'location': location.pk,
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


class IPStackSerializer(serializers.Serializer):
    ip = serializers.IPAddressField(required=True)
    type = serializers.ChoiceField(choices=('ipv4', 'ipv6'), required=True)
    continent_code = serializers.CharField(max_length=2, required=True)
    continent_name = serializers.CharField(max_length=13, required=True)
    country_code = serializers.CharField(max_length=2, required=True)
    country_name = serializers.CharField(max_length=56, required=True)
    region_code = serializers.CharField(max_length=2, required=True)
    region_name = serializers.CharField(max_length=85, required=True)
    city = serializers.CharField(max_length=163, required=True)
    zip = serializers.CharField(max_length=12, required=True)
    latitude = serializers.DecimalField(max_digits=15, decimal_places=13, max_value=90, min_value=-90, required=True, write_only=True)
    longitude = serializers.DecimalField(max_digits=17, decimal_places=14, max_value=180, min_value=-180, required=True, write_only=True)
    location = LocationWithLanguagesSerializer(required=True)

    def to_internal_value(self, data):
        internal_value =  super().to_internal_value(data)
        languages = internal_value['location'].pop('languages', None)
        location = Location.objects.create(**internal_value['location'])
        if languages:
            location.languages.add(*languages)

        return {
            'ip': internal_value['ip'],
            'ip_type': internal_value['type'],
            'continent_code': internal_value['continent_code'],
            'continent_name': internal_value['continent_name'],
            'country_code': internal_value['country_code'],
            'country_name': internal_value['country_name'],
            'region_code': internal_value['region_code'],
            'region_name': internal_value['region_name'],
            'city': internal_value['city'],
            'postal_code': internal_value['zip'],
            'coordinates': {
                'longitude': internal_value['longitude'],
                'latitude': internal_value['latitude']
            },
            'location': location.pk
        }


class GeoLocationSerializer(BaseModelSerializer):
    coordinates = PointField(required=True)

    class Meta:
        model = GeoLocation
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['location'] = LocationSerializer(instance.location).data
        return representation
