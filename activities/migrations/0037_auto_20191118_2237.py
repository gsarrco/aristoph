# Generated by Django 2.1.3 on 2019-11-18 21:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0036_presencetype_text_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participation',
            name='topic',
            field=models.CharField(blank=True, default=None, max_length=300, null=True),
        ),
    ]