# Generated by Django 2.1.3 on 2019-02-06 12:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0011_auto_20190206_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='participation',
            name='is_justified',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
