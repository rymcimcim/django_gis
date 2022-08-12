import json

from django.contrib.auth.models import User
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.test import tag
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, APITestCase

from languages.serializers import LanguageSerializer
from languages.models import Language
from languages.views import LanguageViewSet


@tag('language', 'serializer')
class LanguageSerializerTests(APITestCase):
    def test_serializer_expected_fields(self):
        payload_data = {'code':'AA','name':'AAA','native':'AAA'}
        serializer = LanguageSerializer(data=payload_data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data.keys(), payload_data.keys())

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

    def test_code_field_content(self):
        serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['code'], 'AA')
    
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

    def test_name_field_content(self):
        serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['name'], 'AAA')
    
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

    def test_native_field_content(self):
        serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['native'], 'AAA')
    
    def test_code_name_native_unique_together(self):
        serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        with self.assertRaisesMessage(ValidationError, 'The fields code, name, native must make a unique set.') as cm:
            serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
            serializer.is_valid(raise_exception=True)

        self.assertEqual(Language.objects.count(), 1)
        self.assertEqual(cm.exception.detail['non_field_errors'][0].code, 'unique')
    
    def test_language_positive(self):
        serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        serializer.is_valid(raise_exception=True)


@tag('language', 'viewset')
class LanguageViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.language_1 = Language.objects.create(**{'code':'AA','name':'AAA','native':'AAA'})
        self.language_2 = Language.objects.create(**{'code':'BB','name':'BBB','native':'BBB'})
        self.rf_client = APIRequestFactory(enforce_csrf_checks=True)
        User.objects.create_superuser(username='test_user', email='test_user@test.com', password='test_pass')
        response = self.client.post(
            reverse('token_obtain_pair'),
            json.dumps({"username": "test_user", "password": "test_pass"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data["access"]

    def test_superuser_can_see_languages(self):
        view = LanguageViewSet.as_view({'get': 'list'})
        request = self.rf_client.get(reverse('api:languages-list'), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        queryset = Language.objects.filter(id__in=[self.language_1.pk, self.language_2.pk])
        data = LanguageSerializer(queryset, many=True).data
        self.assertListEqual(response.data.get("results"), data)
    
    def test_superuser_can_see_single_language(self):
        view = LanguageViewSet.as_view({'get': 'retrieve'})
        request = self.rf_client.get(reverse('api:languages-detail', args=(self.language_1.pk,)), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=self.language_1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = LanguageSerializer(self.language_1).data
        self.assertDictEqual(response.data, data)
    
    def test_superuser_can_see_delete_language(self):
        view = LanguageViewSet.as_view({'delete': 'destroy'})
        pk = self.language_1.pk
        request = self.rf_client.delete(reverse('api:languages-detail', args=(pk,)), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaisesMessage(Http404, 'No Language matches the given query.'):
            get_object_or_404(Language, pk=pk)
    
    def test_superuser_can_see_single_language(self):
        view = LanguageViewSet.as_view({'get': 'retrieve'})
        request = self.rf_client.get(reverse('api:languages-detail', args=(self.language_1.pk,)), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=self.language_1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = LanguageSerializer(self.language_1).data
        self.assertDictEqual(response.data, data)
    
    def test_superuser_can_update_language(self):
        view = LanguageViewSet.as_view({'put': 'update'})
        update_payload = {'code':'CC','name':'CCC','native':'CCC'}
        pk = self.language_1.pk
        request = self.rf_client.put(reverse('api:languages-detail', args=(pk,)), update_payload, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        language = get_object_or_404(Language, pk=pk)
        data = LanguageSerializer(language).data
        self.assertDictEqual(response.data, data)
    
    def test_superuser_can_partial_update_language(self):
        view = LanguageViewSet.as_view({'patch': 'partial_update'})
        update_payload = {'code':'CC'}
        pk = self.language_1.pk
        request = self.rf_client.patch(reverse('api:languages-detail', args=(pk,)), update_payload, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        language = get_object_or_404(Language, pk=pk)
        data = LanguageSerializer(language).data
        self.assertDictEqual(response.data, data)
