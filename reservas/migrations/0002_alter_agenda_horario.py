# Generated by Django 4.0.1 on 2023-09-12 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agenda',
            name='horario',
            field=models.CharField(choices=[('1', '07:30 a 08:30'), ('2', '08:30 a 09:30'), ('3', '09:30 a 10:30'), ('4', '10:30 a 11:30'), ('5', '11:30 a 12:30'), ('6', '13:30 a 14:30'), ('7', '14:30 a 15:30'), ('8', '15:30 a 16:30'), ('9', '16:30 a 17:30')], max_length=2),
        ),
    ]
