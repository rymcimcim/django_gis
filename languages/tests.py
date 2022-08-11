from django.test import tag

from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from languages.serializers import LanguageSerializer


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

        self.assertEqual(cm.exception.detail['non_field_errors'][0].code, 'unique')
    
    def test_language_positive(self):
        serializer = LanguageSerializer(data={'code':'AA','name':'AAA','native':'AAA'})
        serializer.is_valid(raise_exception=True)
