# Generated by Django 4.1.1 on 2023-01-18 00:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('item', '0011_item_category_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportantDates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=36, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='important_date_item', to='item.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='important_date_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]