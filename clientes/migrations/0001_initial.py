# Generated by Django 3.2.6 on 2023-08-25 01:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reservas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', models.CharField(blank=True, max_length=17, null=True, validators=[django.core.validators.RegexValidator(message="El número debe estar en este formato.:                         '+593 999999999'.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Telefono')),
                ('carrera', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
        ),
        migrations.CreateModel(
            name='Consulta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agenda', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='consulta', to='reservas.agenda')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consulta', to='clientes.cliente')),
            ],
            options={
                'unique_together': {('agenda', 'cliente')},
            },
        ),
    ]
