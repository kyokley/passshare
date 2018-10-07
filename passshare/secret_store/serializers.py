from django.contrib.auth import get_user_model
from rest_framework import serializers

from passshare.secret_store.models import (TextSecret,
                                           # UPSecret,
                                           # FileSecret,
                                           RecoveredTextSecret,
                                           COUNTDOWN_DEFAULT,
                                           )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'username', 'email', 'groups')


class SecretSerializer(serializers.HyperlinkedModelSerializer):
    pass


class TextSecretSerializer(SecretSerializer):
    class Meta:
        model = TextSecret
        fields = ('url',
                  'owner',
                  'countdown',
                  'unencrypted_hash',
                  'size',
                  'date_created',
                  'date_edited',
                  'data',
                  'label',
                  )
        read_only_fields = ('owner', 'size')

    def create(self, validated_data):
        return TextSecret.new(validated_data['owner'],
                              validated_data['label'],
                              validated_data['data'],
                              validated_data['unencrypted_hash'],
                              countdown=validated_data.get('countdown', COUNTDOWN_DEFAULT))


class RecoveredTextSecretSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecoveredTextSecret
        fields = ('url',
                  'text_secret',
                  'user',
                  'release_date',
                  'date_created',
                  )
