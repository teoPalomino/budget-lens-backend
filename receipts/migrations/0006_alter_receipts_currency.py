# Generated by Django 4.1.1 on 2022-10-30 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0005_receipts_currency_receipts_important_dates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipts',
            name='currency',
            field=models.CharField(max_length=10),
        ),
    ]