from django.contrib.gis.geos import Point
from django.db import transaction

from rest_framework import serializers
from rest_framework_gis.serializers import GeometrySerializerMethodField

from geolocation.models import (
    GeoLocation,
    IPTypes,
    Language,
    Location
)
from geolocation.tasks import dump_data_base


class BaseModelSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        instance = super().save(**kwargs)
        transaction.on_commit(lambda: dump_data_base.delay())
        return instance
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        transaction.on_commit(lambda: dump_data_base.delay())
        return instance


class GeoIP2Serializer(BaseModelSerializer):
    is_in_european_union = serializers.BooleanField(default=False, source='is_eu')
    region = serializers.CharField(max_length=85, allow_blank=True, required=False, source='region_name')

    class Meta:
        model = GeoLocation
        fields = ('coordinates', 'city', 'continent_code', 'continent_name', 'country_code', 'country_name', 'postal_code')


class LanguageSerializer(BaseModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class LocationSerializer(BaseModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['languages'] = LanguageSerializer(instance.languages, many=True).data
        return representation


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
