from base.serializers import BaseModelSerializer

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
