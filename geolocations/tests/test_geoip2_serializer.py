from decimal import Decimal

from django.test import tag

from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from geolocations.serializers import GeoIP2Serializer
from locations.models import Location


@tag('geoip2-serializer')
class GeoIP2SerializerTests(APITestCase):
    def setUp(self) -> None:
        self.geoip2_payload = {
            'city': None, 'continent_code': 'NA', 'continent_name': 'North America',
            'country_code': 'US', 'country_name': 'United States', 'dma_code': None,
            'is_in_european_union': False, 'latitude': 37.751, 'longitude': -97.822,
            'postal_code': None, 'region': None, 'time_zone': 'America/Chicago'
        }
        self.expected_output_keys = [
            'continent_code','continent_name','country_code',
            'country_name','location','coordinates',
        ]

    def test_serializer_expected_input_fields(self):
        serializer = GeoIP2Serializer(data=self.geoip2_payload)
        self.assertEqual(set(serializer.initial_data.keys()), set(self.geoip2_payload.keys()))

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
        
        location = Location.objects.last()
        self.assertEqual(location.pk, serializer.validated_data['location'])
        self.assertEqual(location.is_eu, serializer.initial_data['is_in_european_union'])
    
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
    
    def test_geoip2_latitude_required(self):
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
