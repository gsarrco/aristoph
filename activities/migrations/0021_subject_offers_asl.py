# Generated by Django 2.1.3 on 2019-09-16 20:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0020_application'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='offers_asl',
            field=models.BooleanField(default=False),
        ),
    ]
