from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from datetime import date
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import FileResponse
from django.views import View
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from .models import Laboratorios, Agenda, Carreras



class TestMixinIsAdmin(UserPassesTestMixin):
    def test_func(self):
        is_admin_or_is_staff = self.request.user.is_superuser or self.request.user.is_staff
        return bool(is_admin_or_is_staff)

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos!")
        return redirect("accounts:index")


class LaboratoriosCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):
    model = Laboratorios
    login_url = "accounts:login"
    template_name = "reservas/registro.html"
    fields = ["nombre", "capacidad", "email", "telefono", "carreras", "hora_inicio", "hora_fin"]
    success_url = reverse_lazy("reservas:laboratorio_lista")


class LaboratoriosListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    login_url = "accounts:login"
    template_name = "reservas/laboratorios_lista.html"

    def get_queryset(self):
        return Laboratorios.objects.all().order_by("-pk")


class CarrerasCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):
    model = Carreras
    login_url = "accounts:login"
    template_name = "reservas/registro.html"
    fields = [
        "nombre",
    ]
    success_url = reverse_lazy("reservas:carreras_lista")


class CarrerasListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    login_url = "accounts:login"
    template_name = "reservas/carreras_lista.html"

    def get_queryset(self):
        return Carreras.objects.all().order_by("-pk")


class ConsultarDisponibilidadCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):
    # Logica para consultar los horarios disponibles del laboratorio
    def post(self, request):
        try:
            # Busca el laboratorio por nombre
            laboratorio_obj = Laboratorios.objects.get(pk=request.POST["laboratorio"])

            # Obtén todos los horarios definidos en HORARIOS
            opciones_horario = Agenda.HORARIOS

            # Filtra los horarios registrados para el laboratorio específico
            horarios_registrados = Agenda.objects.filter(laboratorio=laboratorio_obj, dia=request.POST["fecha"]).values_list("horario", flat=True)

            # Excluye los horarios registrados de las opciones de horario
            horarios_disponibles = [horario for horario in opciones_horario if horario[0] not in horarios_registrados]

            # Convierte los horarios disponibles en una lista de diccionarios
            horarios_response = list(horarios_disponibles)

            # Retorna los horarios disponibles en formato JSON
            return JsonResponse({"horarios_disponibles": horarios_response})

        except Laboratorios.DoesNotExist:
            return JsonResponse({"error": "El laboratorio no existe"}, status=400)

        except Exception as e:
            # Maneja cualquier excepción que pueda ocurrir durante la consulta
            return JsonResponse({"error": str(e)}, status=500)


class AgendaCreateView(LoginRequiredMixin, TestMixinIsAdmin, CreateView):
    model = Agenda
    login_url = "accounts:login"
    template_name = "reservas/agenda_registro.html"
    fields = ["laboratorio", "dia", "horario"]
    success_url = reverse_lazy("reservas:agenda_lista")

    def form_valid(self, form):
        # Verificar si ya existe una reserva para la misma fecha y hora en el mismo laboratorio
        existing_reserva = Agenda.objects.filter(
            laboratorio=form.cleaned_data["laboratorio"], dia=form.cleaned_data["dia"], horario=form.cleaned_data["horario"]
        ).exists()

        if existing_reserva:
            messages.error(self.request, "Ya existe una reserva para esta fecha y hora en este laboratorio.")
            return HttpResponseRedirect(reverse_lazy("reservas:agenda_lista"))

        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener la lista de laboratorios disponibles y agregarla al contexto
        dia = self.request.GET.get("dia", date.today())
        horario = self.request.GET.get("horario", "1")

        try:
            # Formatear dia como una cadena de texto en el formato deseado
            dia_str = dia.strftime("%Y-%m-%d")
            dia_seleccionado = datetime.strptime(dia_str, "%Y-%m-%d")
        except ValueError:
            messages.error(self.request, "El formato de fecha es incorrecto.")
            return redirect("reservas:disponibilidad_laboratorios")

        laboratorios_disponibles = Laboratorios.objects.exclude(agenda__dia=dia_seleccionado.date(), agenda__horario=horario, agenda__reservado=True)

        context["laboratorios_disponibles"] = laboratorios_disponibles
        context["dia"] = dia
        context["horario"] = horario
        return context


class AgendaUpdateView(LoginRequiredMixin, TestMixinIsAdmin, UpdateView):
    model = Agenda
    login_url = "accounts:login"
    template_name = "reservas/agenda_registro.html"
    fields = ["laboratorio", "dia", "horario"]
    success_url = reverse_lazy("reservas:agenda_lista")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AgendaDeleteView(LoginRequiredMixin, TestMixinIsAdmin, DeleteView):
    model = Agenda
    success_url = reverse_lazy("reservas:agenda_lista")
    template_name = "eliminar_formulario.html"

    def get_success_url(self):
        messages.success(self.request, "¡Reserva eliminada exitosamente!")
        return reverse_lazy("reservas:agenda_lista")


class AgendaListView(LoginRequiredMixin, TestMixinIsAdmin, ListView):
    login_url = "accounts:login"
    template_name = "reservas/agenda_list.html"

    def get_queryset(self):
        return Agenda.objects.filter().order_by("-pk")


def disponibilidad_laboratorios(request):
    dia = request.GET.get("dia", date.today())
    horario_str = request.GET.get("horario", "1")

    try:
        dia_seleccionado = datetime.strptime(dia, "%Y-%m-%d")
    except ValueError:
        messages.error(request, "El formato de fecha es incorrecto.")
        return redirect("reservas:disponibilidad_laboratorios")

    try:
        # Convertir horario a un entero
        horario = int(horario_str)
    except ValueError:
        messages.error(request, "El valor del horario debe ser un número entero.")
        return redirect("reservas:disponibilidad_laboratorios")

    laboratorios_disponibles = Laboratorios.objects.exclude(agenda__dia=dia_seleccionado.date(), agenda__horario=horario, agenda__reservado=True)

    context = {
        "laboratorios_disponibles": laboratorios_disponibles,
        "dia": dia,
        "horario": horario,
    }

    return render(request, "disponibilidad_laboratorios.html", context)




def generar_informe_pdf(request):
    # Obtén datos para el informe (personalízalo según tus necesidades)
    reservas = Laboratorios.objects.all()

    # Crea un objeto HttpResponse con el tipo de contenido adecuado para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_reservas.pdf"'

    # Crea el objeto PDF
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # Contenedor para los elementos del PDF
    elements = []

    # Configura los estilos para el informe
    styles = getSampleStyleSheet()
    estilo_titulo = styles['Heading1']
    estilo_normal = styles['Normal']

    # Agrega el título al informe
    titulo = Paragraph("Informe de Reservas de Laboratorio", estilo_titulo)
    elements.append(titulo)
    elements.append(Spacer(1, 12))  # Espacio entre el título y la tabla

    # Crea una lista para los datos de las reservas
    datos = []
    encabezados = ["Nombre del Laboratorio", "Correo Electrónico", "Capacidad", "Teléfono", "Carrera", "Hora de Inicio", "Hora de Fin"]

    datos.append(encabezados)

    for reserva in reservas:
        datos_reserva = [
            reserva.nombre,
            reserva.email,
            reserva.capacidad,
            reserva.telefono,
            reserva.carreras,
            reserva.hora_inicio.strftime('%H:%M'),
            reserva.hora_fin.strftime('%H:%M')
        ]
        datos.append(datos_reserva)

    # Crea la tabla y establece el estilo
    tabla = Table(datos)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.7, 0.7, 0.7)),
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
    ]))

    # Agrega la tabla al contenido del PDF
    elements.append(tabla)

    # Construye el PDF
    doc.build(elements)

    return response


def generar_informe_Agenda_pdf(request):
    # Obtén datos para el informe (personalízalo según tus necesidades)
    reservas = Agenda.objects.all()

    # Crea un objeto HttpResponse con el tipo de contenido adecuado para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_reservas.pdf"'

    # Crea el objeto PDF
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # Contenedor para los elementos del PDF
    elements = []

    # Configura los estilos para el informe
    styles = getSampleStyleSheet()
    estilo_titulo = styles['Heading1']
    estilo_normal = styles['Normal']

    # Agrega el título al informe
    titulo = Paragraph("Informe de Reservas de Laboratorio", estilo_titulo)
    elements.append(titulo)
    elements.append(Spacer(1, 12))  # Espacio entre el título y la tabla

    # Crea una lista para los datos de las reservas
    datos = []
    encabezados = ["Nombre del Laboratorio", "Día","Horario", "Usuario", "Reservado"]

    datos.append(encabezados)

    for reserva in reservas:
        datos_reserva = [
            reserva.laboratorio,
            reserva.dia,
            reserva.horario,
            reserva.user,
            'Sí' if reserva.reservado else 'No'
          
        ]
        datos.append(datos_reserva)

    # Crea la tabla y establece el estilo
    tabla = Table(datos)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.7, 0.7, 0.7)),
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
    ]))

    # Agrega la tabla al contenido del PDF
    elements.append(tabla)

    # Construye el PDF
    doc.build(elements)

    return response
  
 


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
generar_informe_pdf = generar_informe_pdf
generar_informe_Agenda_pdf = generar_informe_Agenda_pdf
# generar_informe_clientes_pdf = generar_informe_clientes_pdf
