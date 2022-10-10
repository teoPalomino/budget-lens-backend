import binascii
import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework.authentication import TokenAuthentication


class BearerToken(models.Model):
    """
    The BearerToken model which was extracted fromt the default authorization token model in Django.
    All this to change the size of the token.
    """
    key = models.CharField(_("Key"), max_length=500, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='auth_bearertoken',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
        verbose_name = _("BearerToken")
        verbose_name_plural = _("BearerTokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(250)).decode()

    def __str__(self):
        return self.key


class BearerTokenProxy(BearerToken):
    """
    Proxy mapping pk to user pk for use in admin.
    From Django rest framework libraries
    """
    @property
    def pk(self):
        return self.user_id

    class Meta:
        proxy = 'rest_framework.authtoken' in settings.INSTALLED_APPS
        abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
        verbose_name = "bearertoken"


class BearerAuthentication(TokenAuthentication):
    keyword = 'Bearer'
    model = BearerToken
