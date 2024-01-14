# Generated by Django 2.1.3 on 2019-10-06 06:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0028_activity_allow_new_reservations'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='allow_student_topics',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='allow_teacher_topics',
            field=models.BooleanField(default=False),
        ),
    ]