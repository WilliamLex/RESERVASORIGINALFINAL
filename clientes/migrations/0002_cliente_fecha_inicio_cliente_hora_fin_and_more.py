# Generated by Django 4.0.5 on 2023-09-06 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='fecha_inicio',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='hora_fin',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora de Finalización'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='hora_inicio',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora de Inicio'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='nombre_completo',
            field=models.CharField(max_length=255, verbose_name='Nombres Completos'),
        ),
    ]