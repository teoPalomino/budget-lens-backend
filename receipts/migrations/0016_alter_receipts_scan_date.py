# Generated by Django 4.1.1 on 2022-10-12 03:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("receipts", "0015_rename_receipt_image_url_receipts_receipt_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receipts",
            name="scan_date",
            field=models.DateField(
                default=datetime.datetime(
                    2022, 10, 12, 3, 44, 30, 203619, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
