# Generated by Django 2.1.3 on 2019-03-10 09:26

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0015_participation_presence_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participation',
            name='is_justified',
        ),
        migrations.RemoveField(
            model_name='participation',
            name='is_present',
        ),
    ]