# Generated by Django 4.1.1 on 2023-02-20 00:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0016_alter_receipts_receipt_image'),
        ('receipt_split', '0002_alter_receiptsplit_shared_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receiptsplit',
            name='receipt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='receipt_user', to='receipts.receipts'),
        ),
    ]