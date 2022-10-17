from rest_framework import serializers
from .models import Friends


class FriendSerializer(serializers.ModelSerializer):
    """Validates the email for adding a friend"""

    class Meta:
        model = Friends
        fields = '__all__'

    def create(self, validated_data):
        main_user = validated_data.pop('main_user')
        friend_user = validated_data.pop('friend_user')
        confirmed = validated_data.pop('confirmed')
        temp_email = validated_data.pop('temp_email')

        friend = Friends.objects.create(main_user=main_user, friend_user=friend_user, confirmed=confirmed,
                                        temp_email=temp_email)

        return friend
