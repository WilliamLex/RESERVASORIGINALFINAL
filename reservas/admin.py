from django.contrib import admin

from reservas.models import Carreras, Laboratorios, Agenda

class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['nome']
    
class MedicoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'crm', 'telefone',
    ]
    
class AgendaAdmin(admin.ModelAdmin):
    list_display = [
        'dia', 'laboratorio', 'horario'
    ]
    
admin.site.register(Carreras, EspecialidadeAdmin)
admin.site.register(Laboratorios, MedicoAdmin)
admin.site.register(Agenda, AgendaAdmin)