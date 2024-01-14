# Generated by Django 2.1.3 on 2019-03-10 08:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0013_auto_20190206_1356'),
    ]

    operations = [
        migrations.CreateModel(
            name='PresenceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('icon', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
