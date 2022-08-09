import json

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from geolocation.models import Language


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


class LanguageTest(APITestCase):
    def test_code_field_max_length(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value has at most 2 characters (it has 3).') as cm:
            Language.objects.create(code='AAA', name='AAA', native='AAA')

        self.assertEqual(cm.exception.error_dict['code'][0].code, 'max_length')
    
    def test_code_field_required(self):
        with self.assertRaisesMessage(ValidationError, 'This field cannot be blank.') as cm:
            Language.objects.create(name='AAA', native='AAA')
        
        self.assertEqual(cm.exception.error_dict['code'][0].code, 'blank')
    
    def test_name_field_max_length(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value has at most 25 characters (it has 50).') as cm:
            Language.objects.create(code='AAA', name='A' * 50, native='AAA')
        
        self.assertEqual(cm.exception.error_dict['name'][0].code, 'max_length')
    
    def test_name_field_required(self):
        with self.assertRaisesMessage(ValidationError, 'This field cannot be blank.') as cm:
            Language.objects.create(code='AA', native='AAA')
        
        self.assertEqual(cm.exception.error_dict['name'][0].code, 'blank')
    
    def test_native_field_max_length(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value has at most 25 characters (it has 50).') as cm:
            Language.objects.create(code='AAA', name='AAA', native='A' * 50)
        
        self.assertEqual(cm.exception.error_dict['native'][0].code, 'max_length')
    
    def test_native_field_required(self):
        with self.assertRaisesMessage(ValidationError, 'This field cannot be blank.') as cm:
            Language.objects.create(code='AA', name='AAA')
        
        self.assertEqual(cm.exception.error_dict['native'][0].code, 'blank')
    
    def test_code_name_native_unique_together(self):
        Language.objects.create(code='AA', name='AAA', native='AAA')
        with self.assertRaisesMessage(ValidationError, 'Language with this Code, Name and Native already exists.'):
            Language.objects.create(code='AA', name='AAA', native='AAA')
