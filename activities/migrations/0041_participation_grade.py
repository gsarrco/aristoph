# Generated by Django 2.1.3 on 2019-12-02 20:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0040_remove_participation_is_absent_morning'),
    ]

    operations = [
        migrations.AddField(
            model_name='participation',
            name='grade',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
