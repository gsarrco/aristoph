# Generated by Django 2.1.3 on 2019-02-06 11:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0010_remove_meeting_reservations_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participation',
            old_name='present',
            new_name='is_present',
        ),
    ]