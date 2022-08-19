import json

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.shortcuts import get_object_or_404
from django.test import tag
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from geolocations.models import GeoLocation
from geolocations.serializers import GeoLocationSerializer
from languages.serializers import LanguageSerializer
from locations.serializers import LocationSerializer


@tag('geolocations-api')
class GeoLocationApiTests(APITestCase):
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

        User.objects.create_superuser(username='test_user', email='test_user@test.com', password='test_pass')
        response = self.client.post(
            reverse('token_obtain_pair'),
            json.dumps({"username": "test_user", "password": "test_pass"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

    def test_can_get_geolocations(self):
        language_payload = {'code': 'pl', 'name': 'Polish', 'native': 'Polski'}
        language_serializer = LanguageSerializer(data=language_payload)
        language_serializer.is_valid(raise_exception=True)
        language = language_serializer.save()

        location_payload = {'geoname_id': 3099434, 'capital': 'Warsaw', 'is_eu': True}
        location_serializer = LocationSerializer(data=location_payload)
        location_serializer.is_valid(raise_exception=True)
        location = location_serializer.save()
        location.languages.add(language)
        geolocation_payload_data = {
            'ip': '212.77.100.101', 'type': 'ipv4', 'continent_code': 'EU',
            'continent_name': 'Europe', 'country_code': 'PL', 'country_name': 'Poland',
            'region_code': 'PM', 'region_name': 'Pomerania', 'city': 'Gdańsk',
            'zip': '80-009', 'coordinates': {'latitude': 54.31930923461914, 'longitude': 18.63736915588379},
            'location': location.pk}
        geolocation_serializer = GeoLocationSerializer(data=geolocation_payload_data)
        geolocation_serializer.is_valid(raise_exception=True)
        geolocation_serializer.save()
        response = self.client.get(reverse('api:geolocations-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data['results'], GeoLocationSerializer(GeoLocation.objects.all(), many=True).data)

    def test_can_get_geolocation_details(self):
        response = self.client.get(reverse('api:geolocations-detail', args=(self.geolocation_1.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        location = GeoLocation.objects.get(pk=self.geolocation_1.pk)
        self.assertEqual(response.data, GeoLocationSerializer(instance=location).data)

    def test_can_delete_geolocation(self):
        pk = self.geolocation_1.pk
        response = self.client.delete(reverse('api:geolocations-detail', args=(pk,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaisesMessage(GeoLocation.DoesNotExist, 'GeoLocation matching query does not exist.'):
            GeoLocation.objects.get(pk=pk)
        
        self.assertEqual(GeoLocation.objects.count(), 0)
    
    def test_can_put_geolocation(self):
        put_payload = {  # changed city
            'ip': '212.77.100.101', 'ip_type': 'ipv4', 'continent_code': 'EU',
            'continent_name': 'Europe', 'country_code': 'PL', 'country_name': 'Poland',
            'region_code': 'PM', 'region_name': 'Pomerania', 'city': 'Gdynia',
            'postal_code': '80-009', 'coordinates': {'latitude': 54.31930923461914, 'longitude': 18.63736915588379},
            'location': self.location_1.pk}
        response = self.client.put(reverse('api:geolocations-detail', args=(self.geolocation_1.pk,)), put_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        put_payload['coordinates'] = GEOSGeometry(f'POINT({put_payload["coordinates"]["longitude"]} {put_payload["coordinates"]["latitude"]})')
        geolocation = get_object_or_404(GeoLocation, **put_payload)
        self.assertEqual(response.data, GeoLocationSerializer(geolocation).data)
    
    def test_can_patch_geolocation(self):
        payload_data = self.payload_data
        patch_payload_data = {'city': 'Sopot'}
        response = self.client.patch(reverse('api:geolocations-detail', args=(self.geolocation_1.pk,)), patch_payload_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload_data['city'] = 'Sopot'
        payload_data['coordinates'] = GEOSGeometry(f'POINT({payload_data["coordinates"]["longitude"]} {payload_data["coordinates"]["latitude"]})')
        geolocation = get_object_or_404(GeoLocation, **payload_data)
        self.assertEqual(response.data, GeoLocationSerializer(geolocation).data)
