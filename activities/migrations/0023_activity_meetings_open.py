# Generated by Django 2.1.3 on 2019-09-21 10:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0022_activity_applications_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='meetings_open',
            field=models.BooleanField(default=False),
        ),
    ]
