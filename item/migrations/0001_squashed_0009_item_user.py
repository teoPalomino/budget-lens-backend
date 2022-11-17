# Generated by Django 4.1.1 on 2022-11-17 02:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('item', '0001_initial'), ('item', '0002_alter_item_tax'), ('item', '0003_alter_item_receipt_id'), ('item', '0004_alter_item_receipt_id'), ('item', '0005_alter_item_receipt_id'), ('item', '0006_rename_receipt_id_item_receipt'), ('item', '0007_remove_item_tax'), ('item', '0008_alter_item_price'), ('item', '0009_item_user')]

    initial = True

    dependencies = [
        ('receipts', '0009_merge_20221104_2058'),
        ('receipts', '0012_alter_receipts_receipt_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=36)),
                ('price', models.DecimalField(decimal_places=2, max_digits=18)),
                ('important_dates', models.DateField(blank=True, null=True)),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='receipts.receipts')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='item_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
