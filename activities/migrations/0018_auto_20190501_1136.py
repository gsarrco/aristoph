# Generated by Django 2.1.3 on 2019-05-01 09:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0017_participation_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='end_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
