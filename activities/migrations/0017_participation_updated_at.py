# Generated by Django 2.1.3 on 2019-04-07 13:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0016_auto_20190310_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='participation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
