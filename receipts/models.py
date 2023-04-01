import os
import time
from math import trunc

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from merchant.models import Merchant

from utility.create_update_receipt import create_update_receipt


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
    scan_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    receipt_image = models.ImageField(upload_to=upload_to)
    merchant = models.ForeignKey(Merchant, related_name='merchant', on_delete=models.DO_NOTHING, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    tax = models.FloatField(null=True, blank=True)
    tip = models.FloatField(null=True, blank=True)
    coupon = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    receipt_text = models.TextField(default=None, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Receipts, self).save(*args, **kwargs)
        # if self.receipt_image and self.receipt_text is None:
        #     analyze_receipts(self.receipt_image.path)

    # When a receipt image is deleted from the database, the receipt image file is also deleted from the file
    # system/server
    def delete(self, using=None, keep_parents=False):
        # self.receipt_image.delete()
        self.receipt_image = ''
        super().delete()

    # If the receipt image is being updated using the PUT or PATCH requests, delete the old receipt image file

    @receiver(pre_save, sender='receipts.Receipts')
    def pre_save_image(sender, instance, *args, **kwargs):
        create_update_receipt(sender, instance)
        pass

    @receiver(post_save, sender='receipts.Receipts')
    def post_save_receipt(sender, instance, created, *args, **kwargs):
        if os.getenv('APP_ENV') != 'test':
            from utility.analyze_receipt import analyze_receipts
            from utility.categorize_line_items import categorize_line_items
            if created:
                instance.receipt_text = analyze_receipts(instance.receipt_image.path, instance)
                categorize_line_items(instance)
                instance.save()
