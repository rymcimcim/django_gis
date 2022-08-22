import json

import os
import random

from unittest import mock

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
from geolocations.views import (
    IPSTACK_URL,
    GeoLocationViewSet,
)
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


@tag('geolocation-add-action')
class GeoLocationAddActionTests(APITestCase):
    class IPStackValidResponseMock:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def json(self):
            return {
                'ip': '134.201.250.155', 'type': 'ipv4', 'continent_code': 'NA',
                'continent_name': 'North America', 'country_code': 'US',
                'country_name': 'United States', 'region_code': 'CA', 'region_name': 'California',
                'city': 'Los Angeles', 'zip': '90012',
                'latitude': 34.0655517578125, 'longitude': -118.24053955078125,
                'location': {
                    'geoname_id': 5368361, 'capital': 'Washington D.C.',
                    'languages': [
                        {
                            'code': 'en', 'name': 'English', 'native': 'English'
                        }
                    ],
                    'country_flag': 'https://assets.ipstack.com/flags/us.svg',
                    'country_flag_emoji': '🇺🇸',
                    'country_flag_emoji_unicode': 'U+1F1FA U+1F1F8', 'calling_code': '1',
                    'is_eu': False
                }
            }
    
    class IPStackInvalidResponseMock:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def _get_error_details(self) -> tuple[int, str, str]:
            error_list = [
                (404, '404_not_found', 'The requested resource does not exist.'),
                (101, 'missing_access_key', 'No API Key was specified.'),
                (101, 'No API Key was specified or an invalid API Key was specified.'),
                (102, 'inactive_user', 'The current user account is not active. User will be prompted to get in touch with Customer Support.'),
                (103, 'invalid_api_function', 'The requested API endpoint does not exist.'),
                (104, 'usage_limit_reached', 'The maximum allowed amount of monthly API requests has been reached.'),
                (105, 'function_access_restricted', 'The current subscription plan does not support this API endpoint.'),
                (105, 'https_access_restricted', "The user's current subscription plan does not support HTTPS Encryption."),
                (301, 'invalid_fields', 'One or more invalid fields were specified using the fields parameter.'),
                (302, 'too_many_ips', 'Too many IPs have been specified for the Bulk Lookup Endpoint. (max. 50)'),
                (303, 'batch_not_supported_on_plan', 'The Bulk Lookup Endpoint is not supported on the current subscription plan'),
            ]
            random_error = random.choice(error_list)
            code, error_type, info = random_error
            return info, code, error_type

        def _json(self, info: str, code: int, error_type: str) -> dict:
            return {
                "success": 'false',
                "error": {
                    "code": code,
                    "type": error_type,
                    "info": info
                }
            }

        def json(self) -> dict:
            info, code, error_type = self._get_error_details()
            return self._json(info, code, error_type)
            

    def setUp(self) -> None:
        self.rf_client = APIRequestFactory(enforce_csrf_checks=True)
        User.objects.create_superuser(username='test_user', email='test_user@test.com', password='test_pass')
        response = self.client.post(
            reverse('token_obtain_pair'),
            json.dumps({"username": "test_user", "password": "test_pass"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data["access"]

    def test_add_no_get_parameters_negative(self):
        view = GeoLocationViewSet.as_view({'get': 'add'})
        request = self.rf_client.get(f'{reverse("api:geolocations-add")}', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]), "'url' or 'ip' parameter is required.")
        self.assertEqual(str(response.data[0].code), 'invalid')

    def test_add_both_url_ip_get_parameters_negative(self):
        view = GeoLocationViewSet.as_view({'get': 'add'})
        request = self.rf_client.get(f'{reverse("api:geolocations-add")}?url=/url/to/view/&ip=123.456.789.012', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]), "Both 'url' and 'ip' parameters provided at the same time are not supported.")
        self.assertEqual(str(response.data[0].code), 'invalid')

    def test_add_valid_ip_get_parameter_positive(self):
        ip_addr = '134.201.250.155'
        view = GeoLocationViewSet.as_view({'get': 'add'})
        with mock.patch('requests.get', mock.Mock(wraps=self.IPStackValidResponseMock)) as req_mock:
            request = self.rf_client.get(f'{reverse("api:geolocations-add")}?ip={ip_addr}', HTTP_AUTHORIZATION=f'Bearer {self.token}')
            response = view(request)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertDictContainsSubset({'ip': ip_addr}, response.data)
            self.assertEqual(GeoLocation.objects.count(), 1)
            req_mock.assert_called_once_with(IPSTACK_URL + ip_addr, params={'access_key': os.environ["IPSTACK_ACCESS_KEY"]})
    
    def test_add_valid_ip_get_parameter_ipstack_api_error_positive(self):
        ip_addr = '134.201.250.155'
        view = GeoLocationViewSet.as_view({'get': 'add'})
        with mock.patch('requests.get', mock.Mock(wraps=self.IPStackInvalidResponseMock)) as req_mock:
            request = self.rf_client.get(f'{reverse("api:geolocations-add")}?ip={ip_addr}', HTTP_AUTHORIZATION=f'Bearer {self.token}')
            response = view(request)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertDictContainsSubset({'ip': ip_addr}, response.data)
            self.assertEqual(GeoLocation.objects.count(), 1)
            req_mock.assert_called_once_with(IPSTACK_URL + ip_addr, params={'access_key': os.environ["IPSTACK_ACCESS_KEY"]})

    def test_add_valid_url_get_parameter_positive(self):
        url = 'wp.pl'
        view = GeoLocationViewSet.as_view({'get': 'add'})
        request = self.rf_client.get(f'{reverse("api:geolocations-add")}?url={url}', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GeoLocation.objects.count(), 1)

    def test_add_invalid_url_get_parameter_negative(self):
        url = 'wesgeryhr.rgtrt'
        view = GeoLocationViewSet.as_view({'get': 'add'})
        request = self.rf_client.get(f'{reverse("api:geolocations-add")}?url={url}', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]), 'Name or service not known')
        self.assertEqual(str(response.data[0].code), 'invalid')
