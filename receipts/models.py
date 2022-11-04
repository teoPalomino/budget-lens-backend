import os
import time
from math import trunc

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from merchant.models import Merchant


def upload_to(instance, filename):
    image_file_types = ['.png', '.jpg', '.jpeg']
    image_file_extension = os.path.splitext(filename)[1]

    if image_file_extension in image_file_types:

        # Here, I am simply assigning the image file name by getting the current Unix timestamp version
        # of the current scan date, which is initially of type datetime.datetime, and truncating it
        # to remove any extra decimals
        filename = f'{trunc(time.mktime(instance.scan_date.timetuple()))}{image_file_extension}'
        return 'receipt_images/{instance}/{filename}'.format(instance=instance.user.id, filename=filename)


class Receipts(models.Model):
    """A Receipts model with a user model"""
    user = models.ForeignKey(User, related_name='receipts', on_delete=models.CASCADE)
    scan_date = models.DateTimeField(default=timezone.now)
    receipt_image = models.ImageField(upload_to=upload_to)
    merchant = models.ForeignKey(Merchant, related_name='merchant', on_delete=models.DO_NOTHING)
    location = models.CharField(max_length=200)
    total = models.FloatField()
    tax = models.FloatField()
    tip = models.FloatField()
    coupon = models.FloatField()
    currency = models.CharField(max_length=10)
    important_dates = models.DateField()
    time_of_sale = models.DateTimeField(default=timezone.now())

    # When a receipt image is deleted from the database, the receipt image file is also deleted from the file system/server
    def delete(self, using=None, keep_parents=False):
        self.receipt_image.delete()
        super().delete()

    # If the receipt image is being updated using the PUT or PATCH requests, delete the old receipt image file
    @receiver(pre_save, sender='receipts.Receipts')
    def pre_save_image(sender, instance, *args, **kwargs):
        try:
            old_receipt_image = instance.__class__.objects.get(id=instance.id).receipt_image
            try:
                new_updated_receipt_image = instance.receipt_image
            except ValueError:
                new_updated_receipt_image = None
            if new_updated_receipt_image != old_receipt_image:
                if os.path.exists(old_receipt_image.path):
                    os.remove(old_receipt_image.path)
        except instance.DoesNotExist:
            pass
