# Generated by Django 4.1.1 on 2022-10-10 23:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_friends'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friends',
            old_name='friend_user_id',
            new_name='friend_user',
        ),
        migrations.RenameField(
            model_name='friends',
            old_name='main_user_id',
            new_name='main_user',
        ),
    ]
