import os
import time
from math import trunc

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from budget_lens_backend import settings


def upload_to(instance, filename):
    if not os.path.exists(os.path.join(settings.RECEIPT_IMAGES_ROOT, f'{instance.user.id}')):

        # the following piece of commented code was used to create the sub folders for the user's receipts:

        # os.mkdir(os.path.join(settings.RECEIPT_IMAGES_ROOT, f'{instance.user.id}'))
        # settings.RECEIPT_IMAGES_URL = os.path.join(settings.RECEIPT_IMAGES_URL, f'{instance.user.id}')
        # if not os.path.exists(os.path.join(settings.RECEIPT_IMAGES_URL, f'{instance.id}')):
        #     os.mkdir(os.path.join(settings.RECEIPT_IMAGES_ROOT, f'{instance.user.id}', f'{instance.id}'))
        if filename.endswith('.jpg'):
            filename = f'{trunc(time.mktime(instance.scan_date.timetuple()))}.jpg'
            return 'receipt_images/{instance}/{filename}'.format(instance=instance.user.id, filename=filename)
        elif filename.endswith('.png'):
            filename = f'{trunc(time.mktime(instance.scan_date.timetuple()))}.png'
            return 'receipt_images/{instance}/{filename}'.format(instance=instance.user.id, filename=filename)
        elif filename.endswith('.jpeg'):
            filename = f'{trunc(time.mktime(instance.scan_date.timetuple()))}.jpeg'
            return 'receipt_images/{instance}/{filename}'.format(instance=instance.user.id, filename=filename)
    else:
        if filename.endswith('.jpg'):
            filename = f'{trunc(time.mktime(instance.scan_date.timetuple()))}.jpg'
            return 'receipt_images/{instance}/{filename}'.format(instance=instance.user.id, filename=filename)
        elif filename.endswith('.png'):
            filename = f'{trunc(time.mktime(instance.scan_date.timetuple()))}.png'
            return 'receipt_images/{instance}/{filename}'.format(instance=instance.user.id, filename=filename)
        elif filename.endswith('.jpeg'):
            filename = f'{trunc(time.mktime(instance.scan_date.timetuple()))}.jpeg'
            return 'receipt_images/{instance}/{filename}'.format(instance=instance.user.id, filename=filename)


class Receipts(models.Model):
    """A Receipts model with a user model"""
    user = models.ForeignKey(User, related_name='receipts', on_delete=models.CASCADE)
    scan_date = models.DateTimeField(default=timezone.now)
    receipt_image = models.ImageField(default=None, upload_to=upload_to)
