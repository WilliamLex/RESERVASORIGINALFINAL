from django.urls import path
from . import views

app_name = "clientes"

urlpatterns = [
    path("registro/", views.cliente_registro, name="cliente_registro"),
    path("actualizar/", views.cliente_actualizar, name="cliente_actualizar"),
    path("consultas/", views.consulta_lista, name="consulta_list"),
    path("consultas/crear/", views.consulta_registro, name="consulta_create"),
    path("consultas/editar/<int:pk>/", views.consulta_actualizar, name="consulta_update"),
    path("consultas/eliminar/<int:pk>/", views.consulta_excluir, name="consulta_delete"), 
    path('consultas/generar_informe_clientes_pdf/', views.generar_informe_clientes_pdf, name='generar_informe_clientes_pdf'),
    path("consulta/laboratorio/", views.consulta_laboratorio, name="consulta_laboratorio"), 
]
