from django.contrib import admin

from reservas.models import Carreras, Laboratorios, Agenda

class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    
class MedicoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'capacidad', 'telefono', 'hora_inicio', 'hora_fin'
    ]
    
class AgendaAdmin(admin.ModelAdmin):
    list_display = [
        'dia', 'laboratorio', 'horario', 'laboratorios_disponibles'
    ]
    def laboratorios_disponibles(self, obj):
        # Calcula y muestra los laboratorios disponibles para este registro de Agenda
        laboratorios_disponibles = Laboratorios.objects.exclude(
            agenda__dia=obj.dia,
            agenda__horario=obj.horario,
            agenda__reservado=True
        ).values_list('nombre', flat=True)
        
        return ', '.join(laboratorios_disponibles) if laboratorios_disponibles else 'Ninguno'
    
admin.site.register(Carreras, EspecialidadeAdmin)
admin.site.register(Laboratorios, MedicoAdmin)
admin.site.register(Agenda, AgendaAdmin)