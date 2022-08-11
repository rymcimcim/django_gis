from django.db import transaction

from rest_framework import serializers

from base.tasks import dump_data_base


class BaseModelSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        instance = super().save(**kwargs)
        transaction.on_commit(lambda: dump_data_base.delay())
        return instance
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        transaction.on_commit(lambda: dump_data_base.delay())
        return instance
