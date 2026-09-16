from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import UUIDField

from foodguard.core.models.message import Message
from foodguard.api.serializers.openfoodfacts import OpenFoodFactsSerializer


class MessageSerializer(ModelSerializer):
    chat_id = UUIDField(required=False)
    food_data = OpenFoodFactsSerializer(write_only=True, required=False)

    class Meta:
        model = Message
        fields = [
            'chat_id', 'role', 'content', 'created_at', 'food_data',
            'verdict', 'recommends_doctor',
        ]
        read_only_fields = ['created_at', 'verdict', 'recommends_doctor']

    def create(self, validated_data):
        validated_data.pop('food_data', None)
        validated_data.pop('chat_id', None)
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['chat_id'] = str(instance.chat_id)
        return data