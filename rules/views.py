from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rules.models import Rule
from rules.serializers import RuleSerializer, PutPatchRuleSerializer


class GetRulesAPI(generics.ListAPIView):
    """ Returns a list of rules for a user """
    serializer_class = RuleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        rules = self.get_queryset()
        serializer = RuleSerializer(rules, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def get_queryset(self):
        return Rule.objects.filter(user=self.request.user)


class AddRuleAPI(generics.CreateAPIView):
    """ Adds a rule for a user """
    serializer_class = RuleSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rule = serializer.save()
        return Response({
            "user": rule.user.id,
            "regex": rule.regex,
            "category": rule.category.id,
            "created_at": rule.created_at
        }, status=HTTP_200_OK)


class RuleDetailAPIView(generics.ListAPIView):
    """ details for a rule and edit a rule """
    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchRuleSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get('rule_id'):
            rule = self.get_queryset().filter(id=kwargs.get('rule_id'))
            if rule.exists():
                serializer = RuleSerializer(rule, many=True)
                return Response(serializer.data, status=HTTP_200_OK)
            return Response({
                "Error": "Rule does not exist"
            }, status=HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        if kwargs.get('rule_id'):
            rule = self.get_queryset().filter(id=kwargs.get('rule_id'))
            if rule.exists():
                rule = rule.first()  # get the instance of the rule object, not a queryset
                serializer = PutPatchRuleSerializer(rule, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"Rule edited successfully": serializer.data}, status=HTTP_200_OK)
                return Response({"Error editing rule": serializer.errors}, status=HTTP_400_BAD_REQUEST)
            return Response({"Error": "Rule does not exist"}, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Rule.objects.filter(user=self.request.user)


class DeleteRuleAPI(generics.DestroyAPIView):
    """ Deletes a rule """
    permission_classes = [IsAuthenticated]
    serializer_class = RuleSerializer
    lookup_url_kwarg = 'rule_id'

    def get_queryset(self):
        return Rule.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        if kwargs.get('rule_id'):
            rule = self.get_queryset().filter(id=kwargs.get('rule_id'))
            if rule.exists():
                rule.delete()
                return Response({"response: Rule deleted successfully"}, status=HTTP_200_OK)
            else:
                return Response({"response": "Rule does not exist"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"response": "Rule ID not provided"}, status=HTTP_400_BAD_REQUEST)
