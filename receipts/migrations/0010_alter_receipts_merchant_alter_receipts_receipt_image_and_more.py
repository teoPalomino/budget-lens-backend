# Generated by Django 4.1.1 on 2022-11-09 22:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import receipts.models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0002_alter_merchant_name'),
        ('receipts', '0009_merge_20221104_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipts',
            name='merchant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='merchant', to='merchant.merchant'),
        ),
        migrations.AlterField(
            model_name='receipts',
            name='receipt_image',
            field=models.ImageField(upload_to=receipts.models.upload_to),
        ),
        migrations.AlterField(
            model_name='receipts',
            name='scan_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='receipts',
            name='tax',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='receipts',
            name='total',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
