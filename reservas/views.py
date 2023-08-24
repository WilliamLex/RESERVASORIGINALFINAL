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
            self.request, "Você não tem permissões!"
        )
        return redirect("accounts:index")

class MedicoCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):

    model = Laboratorios
    login_url = 'accounts:login'
    template_name = 'reservas/cadastro.html'
    fields = ['nome', 'crm', 'email', 'telefone', 'especialidade']
    success_url = reverse_lazy('reservas:medicos_lista')
    
class MedicoListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    
    login_url = 'accounts:login'
    template_name = 'reservas/medicos_list.html'

    def get_queryset(self):
        return Laboratorios.objects.all().order_by('-pk')
    
class EspecialidadeCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):

    model = Carreras
    login_url = 'accounts:login'
    template_name = 'reservas/cadastro.html'
    fields = ['nome',]
    success_url = reverse_lazy('reservas:especialidade_lista')
    
class EspecialidadeListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    
    login_url = 'accounts:login'
    template_name = 'reservas/especialidade_list.html'

    def get_queryset(self):
        return Carreras.objects.all().order_by('-pk')


class AgendaCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):

    model = Agenda
    login_url = 'accounts:login'
    template_name = 'reservas/agenda_cadastro.html'
    fields = ['laboratorio', 'dia', 'horario']
    success_url = reverse_lazy('reservas:agenda_lista')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class AgendaUpdateView(LoginRequiredMixin, TestMixinIsAdmin, UpdateView):

    model = Agenda
    login_url = 'accounts:login'
    template_name = 'reservas/agenda_cadastro.html'
    fields = ['laboratorio', 'dia', 'horario']
    success_url = reverse_lazy('reservas:agenda_lista')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class AgendaDeleteView(LoginRequiredMixin, TestMixinIsAdmin, DeleteView):
    model = Agenda
    success_url = reverse_lazy('reservas:agenda_lista')
    template_name = 'form_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Consulta excluída com sucesso!")
        return reverse_lazy('reservas:agenda_lista')


class AgendaListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    
    login_url = 'accounts:login'
    template_name = 'reservas/agenda_list.html'

    def get_queryset(self):
        return Agenda.objects.filter().order_by('-pk')
    
medico_cadastro = MedicoCreateView.as_view()
medico_lista = MedicoListView.as_view()
especialidade_cadastro = EspecialidadeCreateView.as_view()
especialidade_lista = EspecialidadeListView.as_view()
agenda_cadastro = AgendaCreateView.as_view()
agenda_atualizar = AgendaUpdateView.as_view()
agenda_lista = AgendaListView.as_view()
agenda_deletar = AgendaDeleteView.as_view()

