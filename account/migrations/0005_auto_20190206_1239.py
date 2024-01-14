# Generated by Django 2.1.3 on 2019-02-06 11:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0004_auto_20181224_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='current_classe',
            field=models.CharField(blank=True, choices=[('1AC', '1AC'), ('2AC', '2AC'), ('3AC', '3AC'), ('4AC', '4AC'),
                                                        ('5AC', '5AC'), ('1BC', '1BC'), ('2BC', '2BC'), ('3BC', '3BC'),
                                                        ('4BC', '4BC'), ('5BC', '5BC'), ('1CC', '1CC'), ('2CC', '2CC'),
                                                        ('3CC', '3CC'), ('4CC', '4CC'), ('5CC', '5CC'), ('1DC', '1DC'),
                                                        ('2DC', '2DC'), ('3DC', '3DC'), ('4DC', '4DC'), ('5DC', '5DC'),
                                                        ('1EC', '1EC'), ('2EC', '2EC'), ('3EC', '3EC'), ('4EC', '4EC'),
                                                        ('5EC', '5EC'), ('1AL', '1AL'), ('2AL', '2AL'), ('3AL', '3AL'),
                                                        ('4AL', '4AL'), ('5AL', '5AL'), ('1BL', '1BL'), ('2BL', '2BL'),
                                                        ('3BL', '3BL'), ('4BL', '4BL'), ('5BL', '5BL'), ('1CL', '1CL'),
                                                        ('2CL', '2CL'), ('3CL', '3CL'), ('4CL', '4CL'), ('5CL', '5CL'),
                                                        ('1DL', '1DL'), ('2DL', '2DL'), ('3DL', '3DL'), ('4DL', '4DL'),
                                                        ('5DL', '5DL'), ('1EL', '1EL'), ('2EL', '2EL'), ('3EL', '3EL'),
                                                        ('4EL', '4EL'), ('5EL', '5EL'), ('1FL', '1FL'), ('2FL', '2FL'),
                                                        ('3FL', '3FL'), ('4FL', '4FL'), ('5FL', '5FL'), ('1GL', '1GL'),
                                                        ('2GL', '2GL'), ('3GL', '3GL'), ('4GL', '4GL'), ('5GL', '5GL'),
                                                        ('1HL', '1HL'), ('2HL', '2HL'), ('3HL', '3HL'), ('4HL', '4HL'),
                                                        ('5HL', '5HL')], default=None, max_length=3, null=True),
        ),
    ]