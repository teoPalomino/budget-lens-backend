from django.urls import path
from . import views

urlpatterns = [
    path('rules/', views.GetRulesAPI.as_view(), name='rules'),  # Get rules list
    path('rules/add/', views.AddRuleAPI.as_view(), name='add_rule'),  # Add a rule
    path('rules/<int:rule_id>/', views.RuleDetailAPIView.as_view(), name='rule_details'),  # Observe details of a rule
    path('rules/delete/<int:rule_id>/', views.DeleteRuleAPI.as_view(), name='delete_rule'),  # Delete a rule
]