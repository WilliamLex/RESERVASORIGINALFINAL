from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cliente, Consulta


class ClienteCreateView(LoginRequiredMixin ,CreateView):
    
    model = Cliente
    template_name = 'clientes/registro.html'
    fields = ['telefone', 'carrera']
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class ClienteUpdateView(LoginRequiredMixin, UpdateView):

    model = Cliente
    login_url = reverse_lazy('accounts:login')
    template_name = 'accounts/update_user.html'
    fields = ['telefone', 'carrera']
    success_url = reverse_lazy('accounts:index')

    def get_object(self):
        user = self.request.user
        try:
            return Cliente.objects.get(user=user)
        except Cliente.DoesNotExist:
            return None
        
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
        

class ConsultaCreateView(LoginRequiredMixin, CreateView):

    model = Consulta
    login_url = 'accounts:login'
    template_name = 'clientes/registro.html'
    fields = ['agenda']
    success_url = reverse_lazy('clientes:consulta_list')
    
    def form_valid(self, form):
        try:
            form.instance.cliente = Cliente.objects.get(user=self.request.user)
            form.save()
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in e.args[0]:
                messages.warning(self.request, 'No puedes agendar esta reserva')
                return HttpResponseRedirect(reverse_lazy('clientes:consulta_create'))
        except Cliente.DoesNotExist:
            messages.warning(self.request, 'Completa tu registro')
            return HttpResponseRedirect(reverse_lazy('clientes:cliente_registro'))
        messages.info(self.request, 'Reserva agendada con éxito!')
        return HttpResponseRedirect(reverse_lazy('clientes:consulta_list'))
    
class ConsultaUpdateView(LoginRequiredMixin, UpdateView):

    model = Consulta
    login_url = 'accounts:login'
    template_name = 'clientes/registro.html'
    fields = ['agenda']
    success_url = reverse_lazy('reservas:Consulta_lista')
    
    def form_valid(self, form):
        form.instance.cliente = Cliente.objects.get(user=self.request.user)
        return super().form_valid(form)
    
class ConsultaDeleteView(LoginRequiredMixin, DeleteView):
    model = Consulta
    success_url = reverse_lazy('clientes:consulta_list')
    template_name = 'eliminar_formulario.html'

    def get_success_url(self):
        messages.success(self.request, "Reserva eliminada con éxito!")
        return reverse_lazy('clientes:consulta_list')


class ConsultaListView(LoginRequiredMixin, ListView):
    
    login_url = 'accounts:login'
    template_name = 'clientes/consulta_list.html'

    def get_queryset(self):
        user=self.request.user
        try:
            cliente = Cliente.objects.get(user=user)
        except Cliente.DoesNotExist:
            messages.warning(self.request, 'Crea una reserva')
            return None
        try:
            consultas = Consulta.objects.filter(cliente=cliente).order_by('-pk')
        except Consulta.DoesNotExist:
            messages.warning(self.request, 'Crea una reserva')
            return None
        return consultas


cliente_registro = ClienteCreateView.as_view()
cliente_actualizar = ClienteUpdateView.as_view()
consulta_lista = ConsultaListView.as_view()
consulta_registro = ConsultaCreateView.as_view()
consulta_actualizar = ConsultaUpdateView.as_view()
consulta_excluir = ConsultaDeleteView.as_view()
