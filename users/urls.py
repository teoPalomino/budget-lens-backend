from django.urls import path
from . import views

urlpatterns = [
    path('registerEndpoint/', views.RegisterAPI.as_view(), name='register_user'),
    path('loginEndpoint/', views.LoginAPI.as_view(), name='login_user'),
    path('userEndpoint/', views.UserAPI.as_view(), name='user_data'),
    path('logoutEndpoint/', views.LogoutAPI.as_view(), name='logout_user'),
    path('generateDigitCodeEndpoint/', views.GenerateDigitCodeView.as_view(), name='generate_digit_code'),
    path('validateDigitCodeEndpoint/', views.ValidateDigitCodeView.as_view(), name='validate_digit_code'),
    path('changePasswordEndpoint/', views.ChangePasswordView.as_view(), name='change_password')

]
