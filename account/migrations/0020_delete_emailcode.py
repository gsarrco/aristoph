# Generated by Django 3.0.8 on 2020-07-31 20:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0019_user_verified'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmailCode',
        ),
    ]
