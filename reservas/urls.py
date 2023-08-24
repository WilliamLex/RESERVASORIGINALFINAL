from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('registro/laboratorio/', views.medico_cadastro, name='medico_cadastro'),
    path('registro/carreras/', views.especialidade_cadastro, name='especialidade_cadastro'),
    path('agendar/', views.agenda_cadastro, name='agendar_consulta'),
    path('agendar/actualizar/<int:pk>/', views.agenda_atualizar, name='agendar_consulta_atualizar'),
    path('agendar/eliminar/<int:pk>/', views.agenda_deletar, name='agendar_consulta_deletar'),
    path('mis/consultas/', views.agenda_lista, name="agenda_lista"),
    path('admim/lista/reserva/', views.medico_lista, name="medicos_lista"),
    path('admim/lista/carreras/', views.especialidade_lista, name="especialidade_lista")
    
]