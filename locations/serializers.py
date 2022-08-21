from base.serializers import BaseModelSerializer
from languages.models import Language

from languages.serializers import LanguageSerializer

from locations.models import Location


class LocationSerializer(BaseModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['languages'] = LanguageSerializer(instance.languages, many=True).data
        return representation


class LocationWithLanguagesSerializer(BaseModelSerializer):
    languages = LanguageSerializer(required=True, many=True)

    class Meta:
        model = Location
        fields = '__all__'
    
    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        internal_value['languages'] = Language.objects.bulk_create(
            [Language(**language) for language in internal_value['languages']]
        )
        return internal_value
