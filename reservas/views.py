import re  
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from datetime import date
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Laboratorios, Agenda, Carreras


class TestMixinIsAdmin(UserPassesTestMixin):
    def test_func(self):
        is_admin_or_is_staff = self.request.user.is_superuser or \
            self.request.user.is_staff
        return bool(is_admin_or_is_staff)

    def handle_no_permission(self):
        messages.error(
            self.request, "No tienes permisos!"
        )
        return redirect("accounts:index")

class LaboratoriosCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):

    model = Laboratorios
    login_url = 'accounts:login'
    template_name = 'reservas/registro.html'
    fields = ['nombre', 'capacidad', 'email', 'telefono', 'carreras', 'hora_inicio', 'hora_fin']
    success_url = reverse_lazy('reservas:laboratorio_lista')
    
class LaboratoriosListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    
    login_url = 'accounts:login'
    template_name = 'reservas/laboratorios_lista.html'

    def get_queryset(self):
        return Laboratorios.objects.all().order_by('-pk')
    
class CarrerasCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):

    model = Carreras
    login_url = 'accounts:login'
    template_name = 'reservas/registro.html'
    fields = ['nombre',]
    success_url = reverse_lazy('reservas:carreras_lista')
    
class CarrerasListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    
    login_url = 'accounts:login'
    template_name = 'reservas/carreras_lista.html'

    def get_queryset(self):
        return Carreras.objects.all().order_by('-pk')

class ConsultarDisponibilidadCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):
    
    # Logica para consultar los horarios disponibles del laboratorio
    def consultar(self, laboratorio, fecha):
        
        return None


class AgendaCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):

    model = Agenda
    login_url = 'accounts:login'
    template_name = 'reservas/agenda_registro.html'
    fields = ['laboratorio', 'dia', 'horario']
    success_url = reverse_lazy('reservas:agenda_lista')
  
    
   
    
    
    def form_valid(self, form):
        # Verificar si ya existe una reserva para la misma fecha y hora en el mismo laboratorio
        existing_reserva = Agenda.objects.filter(
            laboratorio=form.cleaned_data['laboratorio'],
            dia=form.cleaned_data['dia'],
            horario=form.cleaned_data['horario']
        ).exists()
        
        if existing_reserva:
            messages.error(self.request, "Ya existe una reserva para esta fecha y hora en este laboratorio.")
            return redirect("reservas:agenda_lista")

        form.instance.user = self.request.user
        return super().form_valid(form)
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener la lista de laboratorios disponibles y agregarla al contexto
        dia = self.request.GET.get('dia', date.today())
        horario = self.request.GET.get('horario', '1')

        try:
            # Formatear dia como una cadena de texto en el formato deseado
            dia_str = dia.strftime('%Y-%m-%d')
            dia_seleccionado = datetime.strptime(dia_str, '%Y-%m-%d')
        except ValueError:
            messages.error(self.request, "El formato de fecha es incorrecto.")
            return redirect("reservas:disponibilidad_laboratorios")

        laboratorios_disponibles = Laboratorios.objects.exclude(
            agenda__dia=dia_seleccionado.date(),
            agenda__horario=horario,
            agenda__reservado=True
        )

        context['laboratorios_disponibles'] = laboratorios_disponibles
        context['dia'] = dia
        context['horario'] = horario
        return context
    
class AgendaUpdateView(LoginRequiredMixin, TestMixinIsAdmin, UpdateView):

    model = Agenda
    login_url = 'accounts:login'
    template_name = 'reservas/agenda_registro.html'
    fields = ['laboratorio', 'dia', 'horario']
    success_url = reverse_lazy('reservas:agenda_lista')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
   
    
class AgendaDeleteView(LoginRequiredMixin, TestMixinIsAdmin, DeleteView):
    model = Agenda
    success_url = reverse_lazy('reservas:agenda_lista')
    template_name = 'eliminar_formulario.html'

    def get_success_url(self):
        messages.success(self.request, "¡Reserva eliminada exitosamente!")
        return reverse_lazy('reservas:agenda_lista')


class AgendaListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    
    login_url = 'accounts:login'
    template_name = 'reservas/agenda_list.html'

    def get_queryset(self):
        return Agenda.objects.filter().order_by('-pk')
    
def disponibilidad_laboratorios(request):
    dia = request.GET.get('dia', date.today())
    horario_str= request.GET.get('horario', '1')

    try:
        dia_seleccionado = datetime.strptime(dia, '%Y-%m-%d')
    except ValueError:
        messages.error(request, "El formato de fecha es incorrecto.")
        return redirect("reservas:disponibilidad_laboratorios")
    
    try:
        # Convertir horario a un entero
        horario = int(horario_str)
    except ValueError:
        messages.error(request, "El valor del horario debe ser un número entero.")
        return redirect("reservas:disponibilidad_laboratorios")


    laboratorios_disponibles = Laboratorios.objects.exclude(
        agenda__dia=dia_seleccionado.date(),
        agenda__horario=horario,
        agenda__reservado=True
    )

    context = {
        'laboratorios_disponibles': laboratorios_disponibles,
        'dia': dia,
        'horario': horario,
    }

    return render(request, 'disponibilidad_laboratorios.html', context)


    
laboratorio_registro = LaboratoriosCreateView.as_view()
laboratorio_lista = LaboratoriosListView.as_view()
carreras_registro = CarrerasCreateView.as_view()
carreras_lista = CarrerasListView.as_view()
agenda_registro = AgendaCreateView.as_view()
consultar_disponibilidad = ConsultarDisponibilidadCreateView.as_view()
agenda_actualizar = AgendaUpdateView.as_view()
agenda_lista = AgendaListView.as_view()
agenda_eliminar = AgendaDeleteView.as_view()
disponibilidad_laboratorios = disponibilidad_laboratorios


