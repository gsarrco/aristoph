# Generated by Django 2.1.3 on 2019-11-24 22:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0039_participation_is_absent_morning'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participation',
            name='is_absent_morning',
        ),
    ]