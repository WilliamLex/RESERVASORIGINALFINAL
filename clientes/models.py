from django.conf import settings
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.core.validators import RegexValidator
from django.db import models
from reservas.models import Agenda


class Cliente(models.Model):
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="El número debe estar en este formato.: \
                        '+593 999999999'.",
    )

    telefono = models.CharField(verbose_name="Telefono", validators=[phone_regex], max_length=17, null=True, blank=True)

    carrera = models.CharField(max_length=100)  # Cambiamos la longitud para permitir más caracteres

    nombre_completo = models.CharField(max_length=255, verbose_name="Nombres Completos")

    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio", null=True, blank=True)

    hora_inicio = models.TimeField(verbose_name="Hora de Inicio", null=True, blank=True)

    hora_fin = models.TimeField(verbose_name="Hora de Finalización", null=True, blank=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="Usuário", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name}"


class Consulta(models.Model):
    agenda = OneToOneField(Agenda, on_delete=models.CASCADE, related_name="consulta")
    cliente = ForeignKey(Cliente, on_delete=models.CASCADE, related_name="consulta")

    class Meta:
        unique_together = ("agenda", "cliente")

    def __str__(self):
        return f"{self.agenda} - {self.cliente}"
