from rest_framework import serializers
from .models import Friends


class FriendSerializer(serializers.ModelSerializer):
    """Validates the email for adding a friend"""

    class Meta:
        model = Friends
        fields = '__all__'

    def create(self, validated_data):
        friend = Friends.objects.create(
            main_user=validated_data['main_user'],
            friend_user=validated_data['friend_user'],
            confirmed=validated_data['confirmed'],
            temp_email=validated_data['temp_email'],
        )
        return friend
