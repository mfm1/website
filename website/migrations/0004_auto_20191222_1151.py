# Generated by Django 3.0 on 2019-12-22 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_country'),
    ]

    operations = [
        migrations.RenameField(
            model_name='country',
            old_name='User',
            new_name='user',
        ),
    ]
