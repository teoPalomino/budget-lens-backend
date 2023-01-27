from rest_framework import serializers
from rules.models import Rule


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ('regex', 'category', 'created_at')

    def create(self, validated_data):
        rule = Rule.objects.create(
            user=self.context['request'].user,
            regex=validated_data['regex'],
            category=validated_data['category'],
            created_at=validated_data['created_at']
        )
        return rule


class PutPatchRuleSerializer(serializers.ModelSerializer):
    """Serializer for PutRules, used to update a users rules"""

    class Meta:
        model = Rule
        fields = ('regex', 'category')
