# Generated by Django 4.1.1 on 2023-01-25 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0011_item_category_id'),
        ('item_split', '0005_alter_itemsplit_shared_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemsplit',
            name='item',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='item_user', to='item.item'),
        ),
    ]
