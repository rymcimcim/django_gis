from django.test import tag

from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.exceptions import ValidationError

from languages.models import Language
from locations.models import Location
from locations.serializers import LocationSerializer


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

