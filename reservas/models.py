from datetime import date
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignKey
from datetime import time

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
    hora_inicio = models.TimeField(verbose_name="Hora de inicio", default=time(7, 30))
    hora_fin = models.TimeField(verbose_name="Hora de fin", default=time(17, 30))

    def esta_disponible(self, dia, horario):
        """
        Verifica si el laboratorio está disponible en un día y horario específicos.
        """
        reservas = Agenda.objects.filter(laboratorio=self, dia=dia, horario=horario)
        return not reservas.exists()  # Retorna True si no hay reservas, lo que indica disponibilidad


    
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
        ("1", "07:30 a 08:30"),
        ("2", "08:30 a 09:30"),
        ("3", "09:30 a 10:30"),
        ("4", "10:30 a 11:30"),
        ("5", "11:30 a 12:30"),
        ("6", "13:30 a 14:30"),
        ("7", "15:30 a 16:30"),
        ("8", "16:30 a 17:30"),
    )
    horario = models.CharField(
        max_length=2,
        choices=HORARIOS
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name='Usuario', 
        on_delete=models.CASCADE
    )

    reservado = models.BooleanField(
        default=False,
        verbose_name='Reservado'
    )

    class Meta:
         ordering = ['-pk']
         
    def __str__(self):
        return f'{self.dia.strftime("%b %d %Y")} - {self.get_horario_display()} - {self.laboratorio}'