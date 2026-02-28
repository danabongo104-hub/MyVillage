from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    # Nested the full sender object so the frontend knows
    # exactly who triggered the notification without
    # making a second API call to look up the user.
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'sender',
            'notification_type',
            'post',
            'is_read',
            'created_at'
        ]
        read_only_fields = ['sender', 'created_at']