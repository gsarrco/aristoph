# Generated by Django 2.1.3 on 2019-10-05 09:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0027_auto_20191003_2130'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='allow_new_reservations',
            field=models.BooleanField(default=True),
        ),
    ]