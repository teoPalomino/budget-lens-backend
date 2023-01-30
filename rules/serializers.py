from rest_framework import serializers
from rules.models import Rule
from datetime import datetime


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ('regex', 'category', 'created_at')

    def create(self, validated_data):
        rule = Rule.objects.create(
            user=self.context['request'].user,
            regex=validated_data['regex'],
            category=validated_data['category'],
            created_at=datetime.now()
        )
        return rule


class PutPatchRuleSerializer(serializers.ModelSerializer):
    """Serializer for PutRules, used to update a users rules"""

    class Meta:
        model = Rule
        fields = ('regex', 'category')
