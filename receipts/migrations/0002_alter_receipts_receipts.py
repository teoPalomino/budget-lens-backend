# Generated by Django 4.1.1 on 2022-10-10 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("receipts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receipts",
            name="receipts",
            field=models.ImageField(upload_to="receipt_images"),
        ),
    ]
