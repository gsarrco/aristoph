# Generated by Django 3.0 on 2019-12-21 11:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0042_auto_20191215_2204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
