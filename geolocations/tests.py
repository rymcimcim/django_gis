from decimal import Decimal
import json

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
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
from geolocations.serializers import (
    GeoIP2Serializer,
    GeoLocationSerializer,
)
from geolocations.views import GeoLocationViewSet
from languages.serializers import LanguageSerializer
from locations.serializers import LocationSerializer


@tag('geolocations-serializer')
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

    def test_country_code_blank(self):
        payload_data = self.payload_data
        payload_data['country_code'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'blank')
    
    def test_country_code_null(self):
        payload_data = self.payload_data
        payload_data['country_code'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'null')
    
    def test_country_code_max_length(self):
        payload_data = self.payload_data
        payload_data['country_code'] = 'A' * 50
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'max_length')
    
    def test_country_name_blank(self):
        payload_data = self.payload_data
        payload_data['country_name'] = ''
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'blank')
    
    def test_country_name_null(self):
        payload_data = self.payload_data
        payload_data['country_name'] = None
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'null')
    
    def test_country_name_max_length(self):
        payload_data = self.payload_data
        payload_data['country_name'] = 'A' * 100
        serializer = GeoLocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 56 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'max_length')

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


@tag('geoip2-serializer')
class GeoIP2SerializerTests(APITestCase):
    def setUp(self) -> None:
        self.geoip2_payload = {
            'city': None, 'continent_code': 'NA', 'continent_name': 'North America',
            'country_code': 'US', 'country_name': 'United States', 'dma_code': None,
            'is_in_european_union': False, 'latitude': 37.751, 'longitude': -97.822,
            'postal_code': None, 'region': None, 'time_zone': 'America/Chicago'
        }
        self.expected_input_keys = {
            'city', 'continent_code', 'continent_name', 'country_code',
            'country_name', 'is_in_european_union', 'postal_code', 'region' 
        }
        self.expected_output_keys = [
            'continent_code','continent_name','country_code',
            'country_name','location','coordinates',
        ]

    def test_serializer_expected_input_fields(self):
        serializer = GeoIP2Serializer(instance=self.geoip2_payload)
        self.assertEqual(set(serializer.data.keys()), set(self.expected_input_keys))

    def test_serializer_expected_output_fields(self):
        serializer = GeoIP2Serializer(data=self.geoip2_payload)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(set(serializer.validated_data.keys()), set(self.expected_output_keys))

    def test_geoip2_city_max_length(self):
        payload_data = self.geoip2_payload
        payload_data['city'] = 'A' * 200
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 163 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['city'][0].code, 'max_length')
    
    def test_geoip2_city_required_false(self):
        payload_data = self.geoip2_payload
        del payload_data['city']
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_geoip2_city_blank_positive(self):
        payload_data = self.geoip2_payload
        payload_data['city'] = ''
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_geoip2_city_null_positive(self):
        payload_data = self.geoip2_payload
        payload_data['city'] = None
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_geoip2_continent_code_blank(self):
        payload_data = self.geoip2_payload
        payload_data['continent_code'] = ''
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'blank')
    
    def test_geoip2_continent_code_null(self):
        payload_data = self.geoip2_payload
        payload_data['continent_code'] = None
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'null')
    
    def test_geoip2_continent_code_max_length(self):
        payload_data = self.geoip2_payload
        payload_data['continent_code'] = 'A' * 50
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'max_length')

    def test_geoip2_continent_code_required_true(self):
        payload_data = self.geoip2_payload
        del payload_data['continent_code']
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'required')
    
    def test_geoip2_continent_name_blank(self):
        payload_data = self.geoip2_payload
        payload_data['continent_name'] = ''
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'blank')
    
    def test_geoip2_continent_name_null(self):
        payload_data = self.geoip2_payload
        payload_data['continent_name'] = None
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'null')
    
    def test_geoip2_continent_name_max_length(self):
        payload_data = self.geoip2_payload
        payload_data['continent_name'] = 'A' * 50
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 13 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'max_length')

    def test_geoip2_continent_name_required_true(self):
        payload_data = self.geoip2_payload
        del payload_data['continent_name']
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'required')

    def test_geoip2_country_code_blank(self):
        payload_data = self.geoip2_payload
        payload_data['country_code'] = ''
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'blank')
    
    def test_geoip2_country_code_null(self):
        payload_data = self.geoip2_payload
        payload_data['country_code'] = None
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'null')
    
    def test_geoip2_country_code_max_length(self):
        payload_data = self.geoip2_payload
        payload_data['country_code'] = 'A' * 50
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'max_length')

    def test_geoip2_country_code_required_true(self):
        payload_data = self.geoip2_payload
        del payload_data['country_code']
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'required')
    
    def test_geoip2_country_name_blank(self):
        payload_data = self.geoip2_payload
        payload_data['country_name'] = ''
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'blank')
    
    def test_geoip2_country_name_null(self):
        payload_data = self.geoip2_payload
        payload_data['country_name'] = None
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'null')
    
    def test_geoip2_country_name_max_length(self):
        payload_data = self.geoip2_payload
        payload_data['country_name'] = 'A' * 100
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 56 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'max_length')

    def test_geoip2_country_name_required_true(self):
        payload_data = self.geoip2_payload
        del payload_data['country_name']
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'required')
    
    def test_geoip2_is_in_european_union_none_positive(self):
        payload_data = self.geoip2_payload
        del payload_data['is_in_european_union']
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertNotIn('is_in_european_union', serializer.initial_data)

    def test_geoip2_is_in_european_union_blank_negative(self):
        payload_data = self.geoip2_payload
        payload_data['is_in_european_union'] = ''
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Must be a valid boolean.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['is_in_european_union'][0].code, 'invalid')

    def test_geoip2_is_in_european_union_null_negative(self):
        payload_data = self.geoip2_payload
        payload_data['is_in_european_union'] = None
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['is_in_european_union'][0].code, 'null')

    def test_geoip2_is_in_european_union_location_is_eu_in_output(self):
        payload_data = self.geoip2_payload
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertIn('is_in_european_union', serializer.initial_data)
        self.assertNotIn('is_in_european_union', serializer.validated_data)
        self.assertIn('is_eu', serializer.validated_data['location'])
    
    def test_geoip2_longitude_required(self):
        payload_data = self.geoip2_payload
        del payload_data['longitude']
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'required')
    
    def test_geoip2_longitude_max_digits(self):
        payload_data = self.geoip2_payload
        payload_data['longitude'] = Decimal('1234.12345678901234')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 17 digits in total.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_digits')
    
    def test_geoip2_longitude_max_decimal_places(self):
        payload_data = self.geoip2_payload
        payload_data['longitude'] = Decimal('0.123456789012345')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 14 decimal places.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_decimal_places')
    
    def test_geoip2_longitude_max_whole_digits(self):
        payload_data = self.geoip2_payload
        payload_data['longitude'] = Decimal('1234.0')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 3 digits before the decimal point.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_whole_digits')
    
    def test_geoip2_longitude_max_string_length(self):
        payload_data = self.geoip2_payload
        payload_data['longitude'] = Decimal('1' * 1001)
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'String value too large.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_string_length')
    
    def test_geoip2_longitude_max_value(self):
        payload_data = self.geoip2_payload
        payload_data['longitude'] = Decimal('181')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 180.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_value')
    
    def test_geoip2_longitude_min_value(self):
        payload_data = self.geoip2_payload
        payload_data['longitude'] = Decimal('-181')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to -180.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'min_value')
    
    def test_geoip2_longitude_coordinates_in_output(self):
        payload_data = self.geoip2_payload
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertIn('longitude', serializer.initial_data)
        self.assertNotIn('longitude', serializer.validated_data)
        self.assertIn('longitude', serializer.validated_data['coordinates'])
    
    def test_geoip2_latutude_required(self):
        payload_data = self.geoip2_payload
        del payload_data['latitude']
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'required')
    
    def test_geoip2_latitude_max_digits(self):
        payload_data = self.geoip2_payload
        payload_data['latitude'] = Decimal('123.1234567890123')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 15 digits in total.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_digits')
    
    def test_geoip2_latitude_max_decimal_places(self):
        payload_data = self.geoip2_payload
        payload_data['latitude'] = Decimal('0.12345678901234')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 13 decimal places.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_decimal_places')
    
    def test_geoip2_latitude_max_whole_digits(self):
        payload_data = self.geoip2_payload
        payload_data['latitude'] = Decimal('123.0')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 2 digits before the decimal point.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_whole_digits')
    
    def test_geoip2_latitude_max_string_length(self):
        payload_data = self.geoip2_payload
        payload_data['latitude'] = Decimal('1' * 1001)
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'String value too large.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_string_length')
    
    def test_geoip2_latitude_max_value(self):
        payload_data = self.geoip2_payload
        payload_data['latitude'] = Decimal('91')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 90.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_value')
    
    def test_geoip2_latitude_min_value(self):
        payload_data = self.geoip2_payload
        payload_data['latitude'] = Decimal('-91')
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to -90.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'min_value')
    
    def test_geoip2_latitude_coordinates_in_output(self):
        payload_data = self.geoip2_payload
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertIn('latitude', serializer.initial_data)
        self.assertNotIn('latitude', serializer.validated_data)
        self.assertIn('latitude', serializer.validated_data['coordinates'])

    def test_geoip2_postal_code_max_length(self):
        payload_data = self.geoip2_payload
        payload_data['postal_code'] = 'A' * 200
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 12 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['postal_code'][0].code, 'max_length')
    
    def test_geoip2_postal_code_required_false(self):
        payload_data = self.geoip2_payload
        del payload_data['postal_code']
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_geoip2_postal_code_blank_positive(self):
        payload_data = self.geoip2_payload
        payload_data['postal_code'] = ''
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_geoip2_postal_code_null_positive(self):
        payload_data = self.geoip2_payload
        payload_data['postal_code'] = None
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_geoip2_region_max_length(self):
        payload_data = self.geoip2_payload
        payload_data['region'] = 'A' * 200
        serializer = GeoIP2Serializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region'][0].code, 'max_length')
    
    def test_geoip2_region_required_false(self):
        payload_data = self.geoip2_payload
        del payload_data['region']
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_geoip2_region_blank_positive(self):
        payload_data = self.geoip2_payload
        payload_data['region'] = ''
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_geoip2_region_null_positive(self):
        payload_data = self.geoip2_payload
        payload_data['region'] = None
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
    
    def test_geoip2_region_region_code_in_output(self):
        payload_data = self.geoip2_payload
        payload_data['region'] = 'AA'
        serializer = GeoIP2Serializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertIn('region', serializer.initial_data)
        self.assertNotIn('region', serializer.validated_data)
        self.assertIn('region_code', serializer.validated_data)


