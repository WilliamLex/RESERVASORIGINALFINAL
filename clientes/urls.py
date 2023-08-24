from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('registro/', views.cliente_cadastro, name='cliente_cadastro'),
    path('actualizar/', views.cliente_atualizar, name='cliente_atualizar'),
    path('consultas/', views.consulta_lista, name='consulta_list'),
    path('consultas/crear/', views.consulta_cadastro, name='consulta_create'),
    path('consultas/editar/<int:pk>/', views.consulta_atualizar, name='consulta_update'),
    path('consultas/eliminar/<int:pk>/', views.consulta_excluir, name='consulta_delete'),
]