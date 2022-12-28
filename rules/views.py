from rest_framework import generics


class GetRulesAPI(generics.ListAPIView):
    pass


class AddRuleAPI(generics.CreateAPIView):
    pass


class RuleDetailAPIView(generics.ListAPIView):
    pass


class DeleteRuleAPI(generics.DestroyAPIView):
    pass
