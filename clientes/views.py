from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cliente, Consulta, Agenda
from django import forms
from datetime import datetime


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    template_name = "clientes/registro.html"
    fields = ["telefono", "carrera"]
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    login_url = reverse_lazy("accounts:login")
    template_name = "accounts/update_user.html"
    fields = ["nombre_completo", "telefono", "carrera", "fecha_inicio", "hora_inicio", "hora_fin"]
    success_url = reverse_lazy("accounts:index")

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
    login_url = "accounts:login"
    template_name = "clientes/registro.html"
    fields = ["agenda"]
    success_url = reverse_lazy("clientes:consulta_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Definir el formulario directamente dentro de get_context_data
        class ConsultaForm(forms.Form):
            agenda = forms.ModelChoiceField(queryset=Agenda.objects.exclude(consulta__isnull=False), label="Agendas disponibles")

        if self.request.method == "POST":
            form = ConsultaForm(self.request.POST)
        else:
            form = ConsultaForm()

        context["form"] = form
        return context

    def form_valid(self, form):
        try:
            form.instance.cliente = Cliente.objects.get(user=self.request.user)
            form.save()
        except IntegrityError as e:
            if "UNIQUE constraint failed" in e.args[0]:
                messages.warning(self.request, "No puedes agendar esta reserva")
                return HttpResponseRedirect(reverse_lazy("clientes:consulta_create"))
        except Cliente.DoesNotExist:
            messages.warning(self.request, "Completa tu registro")
            return HttpResponseRedirect(reverse_lazy("clientes:cliente_registro"))
        messages.info(self.request, "Reserva agendada con éxito!")
        return HttpResponseRedirect(reverse_lazy("clientes:consulta_list"))


class GetConsultaDateView(LoginRequiredMixin, ListView):
    def post(self, request):
        # Obtener todas las agendas que tienen consultas
        agendas_con_consultas = Agenda.objects.filter(consulta__isnull=False).distinct()

        # Crear una estructura de datos para el JSON final
        data = []

        for agenda in agendas_con_consultas:
            fecha_agenda = agenda.dia
            dia = fecha_agenda.day
            mes = fecha_agenda.month
            anio = fecha_agenda.year

            # Filtrar las consultas para esta agenda
            consultas = Consulta.objects.filter(agenda=agenda)

            eventos = []

            for consulta in consultas:
                evento = {
                    "title": f"{consulta.agenda.laboratorio.nombre} - {consulta.agenda.HORARIOS[int(consulta.agenda.horario)-1][1]}",
                    "client": consulta.cliente.nombre_completo,
                }
                eventos.append(evento)

            # Verificar si ya existe un objeto en data con la misma fecha
            encontrado = False
            for item in data:
                if item["day"] == dia and item["month"] == mes and item["year"] == anio:
                    item["events"].extend(eventos)
                    encontrado = True
                    break

            # Si no se encontró una fecha similar, crear un nuevo objeto
            if not encontrado:
                nuevo_objeto = {
                    "day": dia,
                    "month": mes,
                    "year": anio,
                    "events": eventos,
                }
                data.append(nuevo_objeto)

        return JsonResponse(data, safe=False)


class ConsultaUpdateView(LoginRequiredMixin, UpdateView):
    model = Consulta
    login_url = "accounts:login"
    template_name = "clientes/registro.html"
    fields = ["agenda"]
    success_url = reverse_lazy("reservas:Consulta_lista")

    def form_valid(self, form):
        form.instance.cliente = Cliente.objects.get(user=self.request.user)
        return super().form_valid(form)


class ConsultaDeleteView(LoginRequiredMixin, DeleteView):
    model = Consulta
    success_url = reverse_lazy("clientes:consulta_list")
    template_name = "eliminar_formulario.html"

    def get_success_url(self):
        messages.success(self.request, "Reserva eliminada con éxito!")
        return reverse_lazy("clientes:consulta_list")


class ConsultaListView(LoginRequiredMixin, ListView):
    login_url = "accounts:login"
    template_name = "clientes/consulta_list.html"

    def get_queryset(self):
        user = self.request.user
        try:
            cliente = Cliente.objects.get(user=user)
        except Cliente.DoesNotExist:
            messages.warning(self.request, "Crea una reserva")
            return None
        try:
            consultas = Consulta.objects.filter(cliente=cliente).order_by("-pk")
        except Consulta.DoesNotExist:
            messages.warning(self.request, "Crea una reserva")
            return None
        return consultas


cliente_registro = ClienteCreateView.as_view()
cliente_actualizar = ClienteUpdateView.as_view()
consulta_lista = ConsultaListView.as_view()
consulta_registro = ConsultaCreateView.as_view()
consulta_actualizar = ConsultaUpdateView.as_view()
consulta_excluir = ConsultaDeleteView.as_view()
consulta_laboratorio = GetConsultaDateView.as_view()
