from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
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


class AgendaCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):

    model = Agenda
    login_url = 'accounts:login'
    template_name = 'reservas/agenda_registro.html'
    fields = ['laboratorio', 'dia', 'horario']
    success_url = reverse_lazy('reservas:agenda_lista')
  
    
   
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

  

    
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
    


    
laboratorio_registro = LaboratoriosCreateView.as_view()
laboratorio_lista = LaboratoriosListView.as_view()
carreras_registro = CarrerasCreateView.as_view()
carreras_lista = CarrerasListView.as_view()
agenda_registro = AgendaCreateView.as_view()
agenda_actualizar = AgendaUpdateView.as_view()
agenda_lista = AgendaListView.as_view()
agenda_eliminar = AgendaDeleteView.as_view()

