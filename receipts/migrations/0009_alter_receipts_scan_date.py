# Generated by Django 4.1.1 on 2022-10-12 00:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("receipts", "0008_alter_receipts_scan_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receipts",
            name="scan_date",
            field=models.DateField(
                default=datetime.datetime(
                    2022, 10, 12, 0, 51, 45, 702526, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
