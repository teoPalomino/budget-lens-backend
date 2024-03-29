# Generated by Django 4.1.1 on 2022-10-17 23:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed', models.BooleanField(default=False)),
                ('temp_email', models.EmailField(max_length=254, null=True)),
                ('friend_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friend_user', to=settings.AUTH_USER_MODEL)),
                ('main_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
