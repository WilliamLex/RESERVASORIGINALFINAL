from django.urls import path
from . import views



app_name = 'reservas'

urlpatterns = [
    path('registro/laboratorio/', views.laboratorio_registro, name='laboratorio_registro'),
    path('registro/carreras/', views.carreras_registro, name='carreras_registro'),
    path('agendar/', views.agenda_registro, name='agendar_reserva'),
    path('agendar/actualizar/<int:pk>/', views.agenda_actualizar, name='agendar_reserva_actualizar'),
    path('agendar/eliminar/<int:pk>/', views.agenda_eliminar, name='agendar_reserva_eliminar'),
    path('mis/consultas/', views.agenda_lista, name="agenda_lista"),
    path('admim/lista/reserva/', views.laboratorio_lista, name="laboratorio_lista"),
    path('admim/lista/carreras/', views.carreras_lista, name="carreras_lista"),
    path('disponibilidad-laboratorios/', views.disponibilidad_laboratorios, name='disponibilidad_laboratorios'),
    
      
]