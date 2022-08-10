import json

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import tag

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError

from geolocation.models import Language, Location
from geolocation.serializers import LanguageSerializer, LocationSerializer


@tag('jwt')
class JwtTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='test_user', email='test_user@test.com', password='test_pass')
        self.credentials = json.dumps({"username": "test_user", "password": "test_pass"})
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.geolocations_list_url = reverse('api:geolocation-list')

    def test_user_is_active_false(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.login_url, self.credentials, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_is_active_true(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.post(self.login_url, self.credentials, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_tokens_credentials_valid(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.post(self.login_url, self.credentials, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(len(response.data['refresh'].split('.')), 3)
        self.assertEqual(len(response.data['access'].split('.')), 3)
    
    def test_login_tokens_credentials_not_valid(self):
        self.user.is_active = True
        self.user.save()

        not_valid_credentials = json.dumps({"username": "test_user", "password": "test_pass123"})
        response = self.client.post(self.login_url, not_valid_credentials, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('No active account found with the given credentials', response.data['detail'])
    
    def test_refresh_token_valid(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.post(self.login_url, self.credentials, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.refresh_url, json.dumps({"refresh": response.data['refresh']}), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(len(response.data['access'].split('.')), 3)
    
    def test_refresh_token_not_valid(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.post(self.refresh_url, json.dumps({"refresh": "fake_refresh_token"}), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Token is invalid or expired', response.data['detail'])
    
    def test_user_is_staff_false(self):
        self.user.is_active = True
        self.user.is_staff = False
        self.user.save()

        response = self.client.post(self.login_url, self.credentials, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        response = self.client.get(self.geolocations_list_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_is_staff_true(self):
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()

        response = self.client.post(self.login_url, self.credentials, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        response = self.client.get(self.geolocations_list_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self) -> None:
        del self.user
        del self.credentials
        del self.login_url
        del self.refresh_url
        del self.geolocations_list_url


@tag('serialize', 'language')
class LanguageTests(APITestCase):
    def test_code_field_max_length(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer = LanguageSerializer(data={'code':'AAA','name':'AAA','native':'AAA'})
            serializer.is_valid(raise_exception=True)

        self.assertEqual(cm.exception.detail['code'][0].code, 'max_length')
    
    def test_code_field_required(self):
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer = LanguageSerializer(data={'name':'AAA','native':'AAA'})
            serializer.is_valid(raise_exception=True)

        self.assertEqual(cm.exception.detail['code'][0].code, 'required')
    
    def test_name_field_max_length(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 25 characters.') as cm:
            serializer = LanguageSerializer(data={'code':'AAA','name':'A' * 50,'native':'AAA'})
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['name'][0].code, 'max_length')
    
    def test_name_field_required(self):
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer = LanguageSerializer(data={'code':'AA','native':'AAA'})
            serializer.is_valid(raise_exception=True)

        self.assertEqual(cm.exception.detail['name'][0].code, 'required')
    
    def test_native_field_max_length(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 25 characters.') as cm:
            serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'A' * 50})
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['native'][0].code, 'max_length')
    
    def test_native_field_required(self):
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer = LanguageSerializer(data={'code':'AA','name':'AAA'})
            serializer.is_valid(raise_exception=True)

        self.assertEqual(cm.exception.detail['native'][0].code, 'required')
    
    def test_code_name_native_unique_together(self):
        serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        with self.assertRaisesMessage(ValidationError, 'The fields code, name, native must make a unique set.') as cm:
            serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
            serializer.is_valid(raise_exception=True)

        self.assertEqual(cm.exception.detail['non_field_errors'][0].code, 'unique')
    
    def test_language_positive(self):
        serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        serializer.is_valid(raise_exception=True)

        language = serializer.save()
        self.assertIsInstance(language, Language)


@tag('serialize', 'location')
class LocationTests(APITestCase):
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
        
        location = serializer.save()
        self.assertIsInstance(location, Location)
    
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
        
        location = serializer.save()
        self.assertIsInstance(location, Location)
    
    def test_capital_none_negative(self):
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer = LocationSerializer(data={'geoname_id':12345,'capital':None,'languages':[self.language_1.pk, self.language_2.pk]})
            self.assertTrue(serializer.is_valid(raise_exception=True))
        
        self.assertEqual(cm.exception.detail['capital'][0].code, 'null')
    
    def test_languages_no_value_positive(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City'})
        self.assertTrue(serializer.is_valid(raise_exception=True))
        
        location = serializer.save()
        self.assertIsInstance(location, Location)

    def test_language_empty_list_positive(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City', 'languages':[]})
        self.assertTrue(serializer.is_valid(raise_exception=True))
        
        location = serializer.save()
        self.assertIsInstance(location, Location)

    def test_capital_field_content(self):
        serializer = LocationSerializer(data={'geoname_id':12345,'capital':'Capital City','languages':[self.language_1.pk, self.language_2.pk]})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['capital'], 'Capital City')

    
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
