from django.test import tag

from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.exceptions import ValidationError

from geolocations.models import GeoLocation
from geolocations.serializers import GeoIP2Serializer, GeoLocationSerializer
