# Generated by Django 2.1.3 on 2019-09-22 18:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0025_participation_classe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='start_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
