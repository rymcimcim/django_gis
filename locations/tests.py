import json

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.test import tag
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
)

from languages.models import Language
from locations.models import Location
from locations.serializers import LocationSerializer
from locations.views import LocationViewSet


@tag('location', 'serializer')
class LocationSerializerTests(APITestCase):
    def setUp(self) -> None:
        self.language_1 = Language.objects.create(**{'code':'AA','name':'AAA','native':'AAA'})
        self.language_2 = Language.objects.create(**{'code':'BB','name':'BBB','native':'BBB'})

    def test_serializer_expected_fields(self):
        payload_data = {'geoname_id':12345,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]}
        serializer = LocationSerializer(data=payload_data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data.keys(), payload_data.keys())

    def test_geoname_id_none(self):
        serializer = LocationSerializer(data={'geoname_id':None,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
        self.assertTrue(serializer.is_valid(raise_exception=True))
    
    def test_geoname_id_max_value(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 2147483647.') as cm:
            serializer = LocationSerializer(data={'geoname_id':10 ** 10,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
            serializer.is_valid(raise_exception=True)
    
        self.assertEqual(cm.exception.detail['geoname_id'][0].code, 'max_value')
    
    def test_geoname_id_min_value(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to 0.') as cm:
            serializer = LocationSerializer(data={'geoname_id':-10,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
            serializer.is_valid(raise_exception=True)
    
        self.assertEqual(cm.exception.detail['geoname_id'][0].code, 'min_value')

    def test_geoname_field_content(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['geoname_id'], 12345)
    
    def test_capital_blank_positive(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'','languages':[self.language_1.pk, self.language_2.pk]})
        self.assertTrue(serializer.is_valid(raise_exception=True))
    
    def test_capital_none_negative(self):
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer = LocationSerializer(data={'geoname_id':12345,'capital':None,'languages':[self.language_1.pk, self.language_2.pk]})
            self.assertTrue(serializer.is_valid(raise_exception=True))
        
        self.assertEqual(cm.exception.detail['capital'][0].code, 'null')
    
    def test_languages_no_value_positive(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City'})
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_language_empty_list_positive(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City', 'languages':[]})
        self.assertTrue(serializer.is_valid(raise_exception=True))
        
        location = serializer.save()
        self.assertIsInstance(location, Location)

    def test_capital_field_content(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['capital'], 'Capital City')

    def test_is_eu_negative(self):
        payload_data = {'geoname_id':12345,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]}
        payload_data['is_eu'] = ''
        serializer = LocationSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Must be a valid boolean.') as cm:
            serializer.is_valid(raise_exception=True)
        
        payload_data['is_eu'] = None
        with self.assertRaisesMessage(ValidationError, 'Must be a valid boolean.') as cm:
            serializer.is_valid(raise_exception=True)
    
    def test_languages_null_negative(self):
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City', 'languages':None})
            self.assertTrue(serializer.is_valid(raise_exception=True))
        
        self.assertEqual(cm.exception.detail['languages'][0].code, 'null')
    
    def test_languages_field_content_pk_write_positive(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
        self.assertTrue(serializer.is_valid(raise_exception=True))
        
        location = serializer.save()
        self.assertIsInstance(location, Location)
    
    def test_languages_field_content_instance_write_negative(self):
        with self.assertRaisesMessage(ValidationError, 'Incorrect type. Expected pk value, received Language.') as cm:
            serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City','languages':[self.language_1, self.language_2]})
            self.assertTrue(serializer.is_valid(raise_exception=True))
        
        self.assertEqual(cm.exception.detail['languages'][0].code, 'incorrect_type')

    def test_languages_to_representation_instance_read_positive(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['languages'], [self.language_1, self.language_2])

    def test_languages_to_representation_pk_read_negative(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
        serializer.is_valid(raise_exception=True)
        self.assertNotEqual(serializer.validated_data['languages'], [self.language_1.pk, self.language_2.pk])
        

    def tearDown(self) -> None:
        self.language_1.delete()
        self.language_2.delete()


@tag('location', 'viewset')
class LocationViewSetTests(APITestCase):
    def setUp(self) -> None:
        language_1 = Language.objects.create(**{'code':'AA','name':'AAA','native':'AAA'})
        self.language_2 = Language.objects.create(**{'code':'BB','name':'BBB','native':'BBB'})
        self.location_1 = Location.objects.create(**{'geoname_id': 12345, 'capital':'Capital City', 'is_eu': True})
        self.location_1.languages.add(language_1.pk, self.language_2.pk)
        self.rf_client = APIRequestFactory(enforce_csrf_checks=True)
        User.objects.create_superuser(username='test_user', email='test_user@test.com', password='test_pass')
        response = self.client.post(
            reverse('token_obtain_pair'),
            json.dumps({"username": "test_user", "password": "test_pass"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data["access"]

    def test_superuser_can_see_locations(self):
        location_2 = Location.objects.create(**{'geoname_id': 54321, 'capital':'Capital City 2'})
        location_2.languages.add(self.language_2.pk)
        view = LocationViewSet.as_view({'get': 'list'})
        request = self.rf_client.get(reverse('api:locations-list'), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        queryset = Location.objects.filter(id__in=[self.location_1.pk, location_2.pk])
        data = LocationSerializer(queryset, many=True).data
        self.assertListEqual(response.data.get("results"), data)
    
    def test_superuser_can_see_single_location(self):
        view = LocationViewSet.as_view({'get': 'retrieve'})
        request = self.rf_client.get(reverse('api:locations-detail', args=(self.location_1.pk,)), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=self.location_1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = LocationSerializer(self.location_1).data
        self.assertDictEqual(response.data, data)

    def test_superuser_can_delete_location(self):
        view = LocationViewSet.as_view({'delete': 'destroy'})
        pk = self.location_1.pk
        request = self.rf_client.delete(reverse('api:locations-detail', args=(pk,)), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaisesMessage(Location.DoesNotExist, 'Location matching query does not exist.'):
            Location.objects.get(pk=pk)
    
    def test_superuser_can_update_location(self):
        view = LocationViewSet.as_view({'put': 'update'})
        update_payload = {'geoname_id': 54321, 'capital':'Capital City 2', 'is_eu': False}
        pk = self.location_1.pk
        request = self.rf_client.put(reverse('api:locations-detail', args=(pk,)), update_payload, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        location = get_object_or_404(Location, pk=pk)
        data = LocationSerializer(location).data
        self.assertDictEqual(response.data, data)
    
    def test_superuser_can_partial_update_location(self):
        view = LocationViewSet.as_view({'patch': 'partial_update'})
        update_payload = {'geoname_id': 54321}
        pk = self.location_1.pk
        request = self.rf_client.patch(reverse('api:locations-detail', args=(pk,)), update_payload, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        location = get_object_or_404(Location, pk=pk)
        data = LocationSerializer(location).data
        self.assertDictEqual(response.data, data)


@tag('location', 'api')
class LocationApiTests(APITestCase):
    def setUp(self) -> None:
        self.language_1 = Language.objects.create(**{'code':'AA','name':'AAA','native':'AAA'})
        self.language_2 = Language.objects.create(**{'code':'BB','name':'BBB','native':'BBB'})
        self.location_1 = Location.objects.create(**{'geoname_id': 12345, 'capital':'Capital City'})
        self.location_1.languages.add(self.language_1.pk, self.language_2.pk)
        User.objects.create_superuser(username='test_user', email='test_user@test.com', password='test_pass')
        response = self.client.post(
            reverse('token_obtain_pair'),
            json.dumps({"username": "test_user", "password": "test_pass"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

    def test_can_get_locations(self):
        location_2 = Location.objects.create(**{'geoname_id': 54321, 'capital':'Capital City 2'})
        response = self.client.get(reverse('api:locations-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        queryset = Location.objects.filter(id__in=[self.location_1.pk, location_2.pk])
        self.assertListEqual(response.data['results'], LocationSerializer(queryset, many=True).data)

    def test_can_get_location_details(self):
        response = self.client.get(reverse('api:locations-detail', args=(self.location_1.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        location = Location.objects.get(pk=self.location_1.pk)
        self.assertEqual(response.data, LocationSerializer(instance=location).data)

    def test_can_delete_location(self):
        pk = self.location_1.pk
        response = self.client.delete(reverse('api:locations-detail', args=(pk,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaisesMessage(Location.DoesNotExist, 'Location matching query does not exist.'):
            Location.objects.get(pk=pk)
        
        self.assertEqual(Location.objects.count(), 0)
    
    def test_can_put_location(self):
        put_payload = {'geoname_id': 54321, 'capital':'Capital City 2'}
        response = self.client.put(reverse('api:locations-detail', args=(self.location_1.pk,)), put_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        location = get_object_or_404(Location, **put_payload)
        self.assertEqual(response.data, LocationSerializer(location).data)
    
    def test_can_patch_location(self):
        response = self.client.patch(reverse('api:locations-detail', args=(self.location_1.pk,)), {'geoname_id':54321})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        location = get_object_or_404(Location, **{'geoname_id':54321,'capital':'Capital City'})
        self.assertEqual(response.data, LocationSerializer(location).data)
