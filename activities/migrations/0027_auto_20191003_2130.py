# Generated by Django 2.1.3 on 2019-10-03 19:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0026_auto_20190922_2050'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'verbose_name': 'attività', 'verbose_name_plural': 'attività'},
        ),
        migrations.AlterModelOptions(
            name='application',
            options={'verbose_name': 'candidatura', 'verbose_name_plural': 'candidature'},
        ),
        migrations.AlterModelOptions(
            name='meeting',
            options={'verbose_name': 'incontro', 'verbose_name_plural': 'incontri'},
        ),
        migrations.AlterModelOptions(
            name='participation',
            options={'ordering': ['id'], 'verbose_name': 'partecipazione', 'verbose_name_plural': 'partecipazioni'},
        ),
        migrations.AlterModelOptions(
            name='presencetype',
            options={'ordering': ['id'], 'verbose_name': 'tipo di presenza', 'verbose_name_plural': 'tipi di presenza'},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ['name'], 'verbose_name': 'materia', 'verbose_name_plural': 'materie'},
        ),
        migrations.AlterModelOptions(
            name='weekday',
            options={'verbose_name': 'giorno settimanale', 'verbose_name_plural': 'giorni settimanali'},
        ),
    ]
