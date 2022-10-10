from django.urls import path
from . import views

urlpatterns = [
    path('registerEndpoint/', views.RegisterAPI.as_view(), name='register_user'),
    path('loginEndpoint/', views.LoginAPI.as_view(), name='login_user'),
    path('userEndpoint/', views.UserAPI.as_view(), name='user_data'),
    path('logoutEndpoint/', views.LogoutAPI.as_view(), name='logout_user'),
    path('verifyEmailEndpoint/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('changePasswordEndpoint/', views.ChangePasswordView.as_view(), name='change_password')

]
