import json

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.test import tag
from django.urls import reverse

from rest_framework import status
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
)

from geolocations.models import GeoLocation
from geolocations.serializers import GeoLocationSerializer
from geolocations.views import GeoLocationViewSet
from languages.serializers import LanguageSerializer
from locations.serializers import LocationSerializer


@tag('geolocations-viewset')
class GeoLocationViewSetTests(APITestCase):
    def setUp(self) -> None:
        location_serializer = LocationSerializer(data={'geoname_id': 12345, 'capital':'Capital City'})
        location_serializer.is_valid(raise_exception=True)
        self.location_1 = location_serializer.save()

        language_serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        language_serializer.is_valid(raise_exception=True)
        self.language_1 = language_serializer.save()
        self.location_1.languages.add(self.language_1)

        self.payload_data = {
            'ip': '134.201.250.155', 'ip_type': 'ipv4', 'continent_code': 'NA',
            'continent_name': 'North America', 'country_code': 'US', 'country_name': 'United States',
            'region_code': 'CA', 'region_name': 'California', 'city': 'Los Angeles',
            'postal_code': '90012', 'coordinates': {'latitude': 34.0655517578125, 'longitude': -118.24053955078125},
            'location': self.location_1.pk,
        }
        serializer = GeoLocationSerializer(data=self.payload_data)
        serializer.is_valid(raise_exception=True)
        self.geolocation_1 = serializer.save()

        self.rf_client = APIRequestFactory(enforce_csrf_checks=True)
        User.objects.create_superuser(username='test_user', email='test_user@test.com', password='test_pass')
        response = self.client.post(
            reverse('token_obtain_pair'),
            json.dumps({"username": "test_user", "password": "test_pass"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data["access"]

    def test_superuser_can_see_geolocations(self):
        language_payload = {'code': 'pl', 'name': 'Polish', 'native': 'Polski'}
        language_serializer = LanguageSerializer(data=language_payload)
        language_serializer.is_valid(raise_exception=True)
        language = language_serializer.save()

        location_payload = {'geoname_id': 3099434, 'capital': 'Warsaw', 'is_eu': True}
        location_serializer = LocationSerializer(data=location_payload)
        location_serializer.is_valid(raise_exception=True)
        location = location_serializer.save()
        location.languages.add(language)

        payload_data = {
            'ip': '212.77.100.101', 'type': 'ipv4', 'continent_code': 'EU',
            'continent_name': 'Europe', 'country_code': 'PL', 'country_name': 'Poland',
            'region_code': 'PM', 'region_name': 'Pomerania', 'city': 'Gdańsk',
            'zip': '80-009', 'coordinates': {'latitude': 54.31930923461914, 'longitude': 18.63736915588379},
            'location': location.pk}
        serializer = GeoLocationSerializer(data=payload_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        view = GeoLocationViewSet.as_view({'get': 'list'})
        request = self.rf_client.get(reverse('api:geolocations-list'), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        queryset = GeoLocation.objects.all()
        data = GeoLocationSerializer(queryset, many=True).data
        self.assertListEqual(response.data.get("results"), data)
    
    def test_superuser_can_see_single_geolocation(self):
        view = GeoLocationViewSet.as_view({'get': 'retrieve'})
        request = self.rf_client.get(reverse('api:geolocations-detail', args=(self.location_1.pk,)), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=self.geolocation_1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = GeoLocationSerializer(self.geolocation_1).data
        self.assertDictEqual(response.data, data)

    def test_superuser_can_delete_geolocation(self):
        view = GeoLocationViewSet.as_view({'delete': 'destroy'})
        pk = self.geolocation_1.pk
        request = self.rf_client.delete(reverse('api:geolocations-detail', args=(pk,)), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaisesMessage(GeoLocation.DoesNotExist, 'GeoLocation matching query does not exist.'):
            GeoLocation.objects.get(pk=pk)
    
    def test_superuser_can_update_geolocation(self):
        view = GeoLocationViewSet.as_view({'put': 'update'})
        update_payload = {  # country code updated
            'ip': '134.201.250.155', 'ip_type': 'ipv4', 'continent_code': 'NA',
            'continent_name': 'North America', 'country_code': 'SU', 'country_name': 'United States',
            'region_code': 'CA', 'region_name': 'California', 'city': 'Los Angeles',
            'postal_code': '90012', 'coordinates': {'latitude': 34.0655517578125, 'longitude': -118.24053955078125},
            'location': self.location_1.pk
        }
        pk = self.geolocation_1.pk
        request = self.rf_client.put(reverse('api:geolocations-detail', args=(pk,)), update_payload, HTTP_AUTHORIZATION=f'Bearer {self.token}', format='json')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        geolocation = get_object_or_404(GeoLocation, pk=pk)
        data = GeoLocationSerializer(geolocation).data
        self.assertDictEqual(response.data, data)
    
    def test_superuser_can_partial_update_geolocation(self):
        view = GeoLocationViewSet.as_view({'patch': 'partial_update'})
        update_payload = {'city': 'Gdańsk'}
        pk = self.geolocation_1.pk
        request = self.rf_client.patch(reverse('api:geolocations-detail', args=(pk,)), update_payload, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        geolocation = get_object_or_404(GeoLocation, pk=pk)
        data = GeoLocationSerializer(geolocation).data
        self.assertDictEqual(response.data, data)
