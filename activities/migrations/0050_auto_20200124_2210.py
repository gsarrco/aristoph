# Generated by Django 3.0 on 2020-01-24 21:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0049_auto_20200124_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]