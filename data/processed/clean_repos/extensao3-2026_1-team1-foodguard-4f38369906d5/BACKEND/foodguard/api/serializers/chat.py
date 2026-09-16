from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import HyperlinkedIdentityField

from foodguard.core.models.chat import Chat


class ChatSerializer(ModelSerializer):
    messages = HyperlinkedIdentityField(view_name='list-messages', lookup_url_kwarg='chat_id')

    class Meta:
        model = Chat
        fields = [
            'id', 'title', 'created_at', 'is_active', 'is_open',
            'image_url', 'severity', 'messages',
        ]