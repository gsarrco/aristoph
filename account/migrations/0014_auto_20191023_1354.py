# Generated by Django 2.1.3 on 2019-10-23 11:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0013_remove_user_birth_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='full_name',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='short_full_name',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
