# Generated by Django 2.1.3 on 2019-05-06 19:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0018_auto_20190501_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='duration',
            field=models.FloatField(default=1.5),
        ),
    ]
