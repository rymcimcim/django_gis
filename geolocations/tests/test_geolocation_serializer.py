from django.test import tag

from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from geolocations.serializers import GeoLocationSerializer
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
