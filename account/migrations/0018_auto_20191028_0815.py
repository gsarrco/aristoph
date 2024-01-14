# Generated by Django 2.1.3 on 2019-10-28 07:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0017_auto_20191027_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='email address'),
        ),
    ]
