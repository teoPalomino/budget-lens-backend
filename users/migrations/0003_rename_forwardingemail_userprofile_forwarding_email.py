# Generated by Django 4.1.1 on 2023-04-02 23:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile_forwardingemail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='forwardingEmail',
            new_name='forwarding_email',
        ),
    ]
