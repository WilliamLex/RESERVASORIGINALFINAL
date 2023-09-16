from django.contrib import admin
from .models import Cliente, Consulta

    
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'telefono', 'carrera', 'laboratorio', 'nombre_completo', 'fecha_inicio', 'hora_inicio', 'hora_fin',
    ]
    
class ConsultaAdmin(admin.ModelAdmin):
    list_display = [
        'agenda', 'cliente', 'horario_cliente',
    ]
    
    
admin.site.register(Cliente, ClientAdmin)
admin.site.register(Consulta, ConsultaAdmin)