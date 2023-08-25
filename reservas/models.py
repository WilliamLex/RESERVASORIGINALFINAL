from datetime import date
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignKey

class Carreras(models.Model):
    nombre = models.CharField(verbose_name="Nombre", max_length=200)
    
    def __str__(self):
        return f'{self.nombre}'
    
class Laboratorios(models.Model):
    nombre = models.CharField(verbose_name="Nombre del laboratorio", max_length=200)
    email = models.EmailField(verbose_name="Correo electronico")
    capacidad = models.CharField(verbose_name="Capacidad", max_length=200)
    phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="El número debe estar en este formato: \
                    '+593 999999999'.")

    telefono = models.CharField(verbose_name="Telefono",
                                validators=[phone_regex],
                                max_length=17, null=True, blank=True)
    carreras = ForeignKey(Carreras,
                               on_delete=models.CASCADE,
                               related_name='reservas')
    
    def __str__(self):
        return f'{self.nombre}'

def validar_dia(value):
    today = date.today()
    weekday = date.fromisoformat(f'{value}').weekday()

    if value < today:
        raise ValidationError('No es posible elegir una fecha pasada.')
    if (weekday == 5) or (weekday == 6):
        raise ValidationError('Elige un día laborable de la semana.')

class Agenda(models.Model):
    laboratorio = ForeignKey(Laboratorios, on_delete=models.CASCADE, related_name='agenda')
    dia = models.DateField(help_text="Ingrese una fecha para la agenda", validators=[validar_dia])
    
    HORARIOS = (
        ("1", "07:00 a 08:00"),
        ("2", "08:00 a 09:00"),
        ("3", "09:00 a 10:00"),
        ("4", "10:00 a 11:00"),
        ("5", "11:00 a 12:00"),
    )
    horario = models.CharField(max_length=10, choices=HORARIOS)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name='Usuario', 
        on_delete=models.CASCADE
    )
    class Meta:
        unique_together = ('horario', 'dia')
        
    def __str__(self):
        return f'{self.dia.strftime("%b %d %Y")} - {self.get_horario_display()} - {self.laboratorio}'