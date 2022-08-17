import json

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geoip2 import GeoIP2
from django.shortcuts import get_object_or_404
from django.test import tag
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
)

from geolocations.models import GeoLocation
from geolocations.serializers import GeoLocationSerializer
from geolocations.views import GeoLocationViewSet
from languages.serializers import LanguageSerializer
from locations.serializers import LocationSerializer


@tag('geolocation', 'viewset')
class GeoLocationSerializerTests(APITestCase):
    def setUp(self) -> None:
        location_serializer = LocationSerializer(data={'geoname_id': 12345, 'capital':'Capital City', 'is_eu': True})
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

    def test_serializer_expected_fields(self):
        serializer = GeoLocationSerializer(data=self.payload_data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(set(serializer.validated_data.keys()), set(self.payload_data.keys()))
    
    def test_ip_null(self):
        payload_data = self.payload_data
        payload_data['ip'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
    
    def test_ip_blank(self):
        payload_data = self.payload_data
        payload_data['ip'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['ip'][0].code, 'blank')
    
    def test_ip_type_null(self):
        payload_data = self.payload_data
        payload_data['ip_type'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['ip_type'][0].code, 'null')
    
    def test_ip_type_max_length(self):
        payload_data = self.payload_data
        field_value = 'A' * 50
        payload_data['ip_type'] = 'A' * 50
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, f'"{field_value}" is not a valid choice.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['ip_type'][0].code, 'invalid_choice')
    
    def test_continent_code_blank(self):
        payload_data = self.payload_data
        payload_data['continent_code'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'blank')
    
    def test_continent_code_null(self):
        payload_data = self.payload_data
        payload_data['continent_code'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'null')
    
    def test_continent_code_max_length(self):
        payload_data = self.payload_data
        payload_data['continent_code'] = 'A' * 50
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'max_length')
    
    def test_continent_name_blank(self):
        payload_data = self.payload_data
        payload_data['continent_name'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'blank')
    
    def test_continent_name_null(self):
        payload_data = self.payload_data
        payload_data['continent_name'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'null')
    
    def test_continent_name_max_length(self):
        payload_data = self.payload_data
        payload_data['continent_name'] = 'A' * 50
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 13 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'max_length')
    
    def test_region_code_blank(self):
        payload_data = self.payload_data
        payload_data['region_code'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_region_code_null(self):
        payload_data = self.payload_data
        payload_data['region_code'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_code'][0].code, 'null')
    
    def test_region_code_max_length(self):
        payload_data = self.payload_data
        payload_data['region_code'] = 'A' * 50
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_code'][0].code, 'max_length')
    
    def test_region_name_blank(self):
        payload_data = self.payload_data
        payload_data['region_name'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_region_name_null(self):
        payload_data = self.payload_data
        payload_data['region_name'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_name'][0].code, 'null')
    
    def test_region_name_max_length(self):
        payload_data = self.payload_data
        payload_data['region_name'] = 'A' * 100
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 85 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_name'][0].code, 'max_length')
    
    def test_city_blank(self):
        payload_data = self.payload_data
        payload_data['city'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_city_null(self):
        payload_data = self.payload_data
        payload_data['city'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['city'][0].code, 'null')
    
    def test_city_max_length(self):
        payload_data = self.payload_data
        payload_data['city'] = 'A' * 200
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 163 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['city'][0].code, 'max_length')
    
    def test_postal_code_blank(self):
        payload_data = self.payload_data
        payload_data['postal_code'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_postal_code_null(self):
        payload_data = self.payload_data
        payload_data['postal_code'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['postal_code'][0].code, 'null')
    
    def test_postal_code_max_length(self):
        payload_data = self.payload_data
        payload_data['postal_code'] = 'A' * 20
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 12 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['postal_code'][0].code, 'max_length')
    
    def test_coordinates_blank_negative(self):
        payload_data = self.payload_data
        payload_data['coordinates'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Enter a valid location.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['coordinates'][0].code, 'invalid')

    def test_coordinates_null_negative(self):
        payload_data = self.payload_data
        payload_data['coordinates'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['coordinates'][0].code, 'null')

    def test_location_null_positive(self):
        payload_data = self.payload_data
        payload_data['location'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        serializer.is_valid(raise_exception=True)
    
    def test_location_blank_positive(self):
        payload_data = self.payload_data
        payload_data['location'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        serializer.is_valid(raise_exception=True)

    def test_latitude_proprety_positive(self):
        payload_data = self.payload_data
        payload_data['latitude'] = 90
        payload_data['longitude'] = -180
        serializer = GeoLocationSerializer(data=payload_data)
        serializer.is_valid(raise_exception=True)

    def test_location_to_representation(self):
        serializer = GeoLocationSerializer(data=self.payload_data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['location'], self.location_1)


@tag('geolocation, viewset')
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


@tag('geolocation', 'api')
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

    def test_can_get_locations(self):
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
