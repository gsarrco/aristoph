# Generated by Django 2.1.3 on 2019-01-14 15:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0008_auto_20190112_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='activity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='activities.Activity'),
            preserve_default=False,
        ),
    ]
