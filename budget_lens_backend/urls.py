"""budget_lens_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from budget_lens_backend import settings

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),  # rest_framework
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('receipts.urls')),
    path('', include('friends.urls')),
    path('', include('category.urls')),
    path('', include('item.urls')),
    path('', include('merchant.urls')),
    path('', include('rules.urls')),
    path('', include('important_dates.urls')),
    path('', include('item_split.urls')),
    path('', include('receipt_split.urls')),
    path('file/', include('filemanagement.urls'), name='file'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL)  # static files
