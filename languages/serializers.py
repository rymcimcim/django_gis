from base.serializers import BaseModelSerializer

from languages.models import Language


class LanguageSerializer(BaseModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'
