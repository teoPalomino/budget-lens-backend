# Generated by Django 4.1.1 on 2023-01-13 04:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('item', '0011_item_category_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemSplit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shared_user_ids', models.CharField(max_length=100)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='item_user', to='item.item')),
            ],
        ),
    ]
