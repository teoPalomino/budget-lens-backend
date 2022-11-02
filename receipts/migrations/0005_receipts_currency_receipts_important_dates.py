# Generated by Django 4.1.1 on 2022-10-30 18:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0004_alter_receipts_merchant'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipts',
            name='currency',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='receipts',
            name='important_dates',
            field=models.DateField(default=datetime.date(2022, 10, 30)),
            preserve_default=False,
        ),
    ]