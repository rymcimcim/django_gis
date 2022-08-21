from decimal import Decimal

from django.test import tag

from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from geolocations.serializers import IPStackSerializer
from locations.models import Location


@tag('ipstack-serializer')
class IPStackSerializerTests(APITestCase):
    def setUp(self) -> None:
        self.ipstack_payload = {
            'ip': '134.201.250.155', 'type': 'ipv4', 'continent_code': 'NA',
            'continent_name': 'North America', 'country_code': 'US',
            'country_name': 'United States', 'region_code': 'CA',
            'region_name': 'California', 'city': 'Los Angeles', 'zip': '90012',
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

        self.expected_output_keys = [
            'ip', 'ip_type', 'continent_code', 'continent_name', 'country_code',
            'country_name', 'region_code','region_name', 'city', 'postal_code',
            'coordinates','location'
        ]

    def test_serializer_expected_input_fields(self):
        serializer = IPStackSerializer(data=self.ipstack_payload)
        self.assertEqual(set(serializer.initial_data.keys()), set(self.ipstack_payload.keys()))

    def test_serializer_expected_output_fields(self):
        serializer = IPStackSerializer(data=self.ipstack_payload)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(set(serializer.validated_data.keys()), set(self.expected_output_keys))

    def test_ip_invalid_address_negative(self):
        payload_data = self.ipstack_payload
        payload_data['ip'] = 'abcdefgh'
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Enter a valid IPv4 or IPv6 address.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['ip'][0].code, 'invalid')

    def test_ip_blank_negative(self):
        payload_data = self.ipstack_payload
        payload_data['ip'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['ip'][0].code, 'blank')

    def test_ip_null_negative(self):
        payload_data = self.ipstack_payload
        payload_data['ip'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['ip'][0].code, 'null')

    def test_ipstack_ip_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['ip']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['ip'][0].code, 'required')

    def test_type_invalid_negative(self):
        payload_data = self.ipstack_payload
        payload_data['type'] = 'abcdefgh'
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, '"abcdefgh" is not a valid choice.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['type'][0].code, 'invalid_choice')

    def test_type_blank_negative(self):
        payload_data = self.ipstack_payload
        payload_data['type'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, '"" is not a valid choice.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['type'][0].code, 'invalid_choice')

    def test_type_null_negative(self):
        payload_data = self.ipstack_payload
        payload_data['type'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['type'][0].code, 'null')

    def test_ipstack_type_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['type']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['type'][0].code, 'required')

    def test_ipstack_continent_code_blank(self):
        payload_data = self.ipstack_payload
        payload_data['continent_code'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'blank')
    
    def test_ipstack_continent_code_null(self):
        payload_data = self.ipstack_payload
        payload_data['continent_code'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'null')
    
    def test_ipstack_continent_code_max_length(self):
        payload_data = self.ipstack_payload
        payload_data['continent_code'] = 'A' * 50
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'max_length')

    def test_ipstack_continent_code_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['continent_code']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_code'][0].code, 'required')
    
    def test_ipstack_continent_name_blank(self):
        payload_data = self.ipstack_payload
        payload_data['continent_name'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'blank')
    
    def test_ipstack_continent_name_null(self):
        payload_data = self.ipstack_payload
        payload_data['continent_name'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'null')
    
    def test_ipstack_continent_name_max_length(self):
        payload_data = self.ipstack_payload
        payload_data['continent_name'] = 'A' * 50
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 13 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'max_length')

    def test_ipstack_continent_name_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['continent_name']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['continent_name'][0].code, 'required')

    def test_ipstack_country_code_blank(self):
        payload_data = self.ipstack_payload
        payload_data['country_code'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'blank')
    
    def test_ipstack_country_code_null(self):
        payload_data = self.ipstack_payload
        payload_data['country_code'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'null')
    
    def test_ipstack_country_code_max_length(self):
        payload_data = self.ipstack_payload
        payload_data['country_code'] = 'A' * 50
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'max_length')

    def test_ipstack_country_code_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['country_code']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_code'][0].code, 'required')
    
    def test_ipstack_country_name_blank(self):
        payload_data = self.ipstack_payload
        payload_data['country_name'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'blank')
    
    def test_ipstack_country_name_null(self):
        payload_data = self.ipstack_payload
        payload_data['country_name'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'null')
    
    def test_ipstack_country_name_max_length(self):
        payload_data = self.ipstack_payload
        payload_data['country_name'] = 'A' * 100
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 56 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'max_length')

    def test_ipstack_country_name_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['country_name']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['country_name'][0].code, 'required')

    def test_ipstack_region_code_blank(self):
        payload_data = self.ipstack_payload
        payload_data['region_code'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_code'][0].code, 'blank')
    
    def test_ipstack_region_code_null(self):
        payload_data = self.ipstack_payload
        payload_data['region_code'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_code'][0].code, 'null')
    
    def test_ipstack_region_code_max_length(self):
        payload_data = self.ipstack_payload
        payload_data['region_code'] = 'A' * 50
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 2 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_code'][0].code, 'max_length')

    def test_ipstack_region_code_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['region_code']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_code'][0].code, 'required')
    
    def test_ipstack_region_name_blank(self):
        payload_data = self.ipstack_payload
        payload_data['region_name'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_name'][0].code, 'blank')
    
    def test_ipstack_region_name_null(self):
        payload_data = self.ipstack_payload
        payload_data['region_name'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_name'][0].code, 'null')
    
    def test_ipstack_region_name_max_length(self):
        payload_data = self.ipstack_payload
        payload_data['region_name'] = 'A' * 100
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 85 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_name'][0].code, 'max_length')

    def test_ipstack_region_name_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['region_name']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['region_name'][0].code, 'required')
    
    def test_ipstack_city_blank(self):
        payload_data = self.ipstack_payload
        payload_data['city'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['city'][0].code, 'blank')

    def test_ipstack_city_null(self):
        payload_data = self.ipstack_payload
        payload_data['city'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['city'][0].code, 'null')
    
    def test_ipstack_city_max_length(self):
        payload_data = self.ipstack_payload
        payload_data['city'] = 'A' * 200
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 163 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['city'][0].code, 'max_length')

    def test_ipstack_city_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['city']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['city'][0].code, 'required')

    def test_ipstack_zip_max_length(self):
        payload_data = self.ipstack_payload
        payload_data['zip'] = 'A' * 200
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this field has no more than 12 characters.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['zip'][0].code, 'max_length')
    
    def test_ipstack_zip_required_true(self):
        payload_data = self.ipstack_payload
        del payload_data['zip']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['zip'][0].code, 'required')

    def test_ipstack_zip_blank_negative(self):
        payload_data = self.ipstack_payload
        payload_data['zip'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be blank.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['zip'][0].code, 'blank')

    def test_ipstack_zip_null_negative(self):
        payload_data = self.ipstack_payload
        payload_data['zip'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['zip'][0].code, 'null')
 
    def test_ipstack_longitude_required(self):
        payload_data = self.ipstack_payload
        del payload_data['longitude']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'required')
    
    def test_ipstack_longitude_max_digits(self):
        payload_data = self.ipstack_payload
        payload_data['longitude'] = Decimal('1234.12345678901234')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 17 digits in total.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_digits')
    
    def test_ipstack_longitude_max_decimal_places(self):
        payload_data = self.ipstack_payload
        payload_data['longitude'] = Decimal('0.123456789012345')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 14 decimal places.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_decimal_places')
    
    def test_ipstack_longitude_max_whole_digits(self):
        payload_data = self.ipstack_payload
        payload_data['longitude'] = Decimal('1234.0')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 3 digits before the decimal point.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_whole_digits')
    
    def test_ipstack_longitude_max_string_length(self):
        payload_data = self.ipstack_payload
        payload_data['longitude'] = Decimal('1' * 1001)
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'String value too large.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_string_length')
    
    def test_ipstack_longitude_max_value(self):
        payload_data = self.ipstack_payload
        payload_data['longitude'] = Decimal('181')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 180.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'max_value')
    
    def test_ipstack_longitude_min_value(self):
        payload_data = self.ipstack_payload
        payload_data['longitude'] = Decimal('-181')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to -180.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['longitude'][0].code, 'min_value')
    
    def test_ipstack_longitude_coordinates_in_output(self):
        payload_data = self.ipstack_payload
        serializer = IPStackSerializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertIn('longitude', serializer.initial_data)
        self.assertNotIn('longitude', serializer.validated_data)
        self.assertIn('longitude', serializer.validated_data['coordinates'])
    
    def test_ipstack_latitude_required(self):
        payload_data = self.ipstack_payload
        del payload_data['latitude']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'required')
    
    def test_ipstack_latitude_max_digits(self):
        payload_data = self.ipstack_payload
        payload_data['latitude'] = Decimal('123.1234567890123')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 15 digits in total.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_digits')
    
    def test_ipstack_latitude_max_decimal_places(self):
        payload_data = self.ipstack_payload
        payload_data['latitude'] = Decimal('0.12345678901234')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 13 decimal places.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_decimal_places')
    
    def test_ipstack_latitude_max_whole_digits(self):
        payload_data = self.ipstack_payload
        payload_data['latitude'] = Decimal('123.0')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure that there are no more than 2 digits before the decimal point.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_whole_digits')
    
    def test_ipstack_latitude_max_string_length(self):
        payload_data = self.ipstack_payload
        payload_data['latitude'] = Decimal('1' * 1001)
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'String value too large.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_string_length')
    
    def test_ipstack_latitude_max_value(self):
        payload_data = self.ipstack_payload
        payload_data['latitude'] = Decimal('91')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 90.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'max_value')
    
    def test_ipstack_latitude_min_value(self):
        payload_data = self.ipstack_payload
        payload_data['latitude'] = Decimal('-91')
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to -90.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['latitude'][0].code, 'min_value')
    
    def test_ipstack_latitude_coordinates_in_output(self):
        payload_data = self.ipstack_payload
        serializer = IPStackSerializer(data=payload_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertIn('latitude', serializer.initial_data)
        self.assertNotIn('latitude', serializer.validated_data)
        self.assertIn('latitude', serializer.validated_data['coordinates'])

    def test_ipstack_location_null_negative(self):
        payload_data = self.ipstack_payload
        payload_data['location'] = None
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field may not be null.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['location'][0].code, 'null')
    
    def test_ipstack_location_blank_negative(self):
        payload_data = self.ipstack_payload
        payload_data['location'] = ''
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'Invalid data. Expected a dictionary, but got str.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['location']['non_field_errors'][0].code, 'invalid')
    
    def test_ipstack_location_required(self):
        payload_data = self.ipstack_payload
        del payload_data['location']
        serializer = IPStackSerializer(data=payload_data)
        with self.assertRaisesMessage(ValidationError, 'This field is required.') as cm:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(cm.exception.detail['location'][0].code, 'required')
