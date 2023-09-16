import colorsys
from msilib import Table
import colorama
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import reservas

from reservas.models import Carreras, Laboratorios
from .models import Cliente, Consulta, Agenda
from django import forms
from django.http import FileResponse
from django.views import View
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors 
from datetime import datetime
from reportlab.lib.pagesizes import landscape
import os
import datetime




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
    fields = ["nombre_completo", "telefono", "carrera", "laboratorio", "fecha_inicio", "hora_inicio", "hora_fin"]
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
    

def generar_informe_clientes_pdf(request):
#    # Obtén datos para el informe (personalízalo según tus necesidades)
#     clientes = Cliente.objects.all()

#     # Configura el tamaño de la hoja en orientación horizontal (landscape)
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="informe_clientes.pdf"'
#     doc = SimpleDocTemplate(response, pagesize=landscape(letter))

#     # Contenedor para los elementos del PDF
#     elements = []

#     # Configura los estilos para el informe
#     styles = getSampleStyleSheet()
#     estilo_titulo = styles['Heading1']
#     estilo_normal = styles['Normal']

#     # Agrega el título al informe
#     titulo = Paragraph("Informe de Detalles de Reserva de Laboratorios", estilo_titulo)
#     elements.append(titulo)

#     # Crea una lista para los datos de los clientes
#     datos = []
#     encabezados = ["Teléfono", "Carrera", "Laboratorios", "Nombres", "Fecha de Inicio", "Hora de Inicio", "Hora de Fin", "Usuario"]
#     datos.append(encabezados)

#     for cliente in clientes:
#         datos_cliente = [
#             cliente.telefono or "",
#             cliente.carrera or "",
#             cliente.laboratorio or "",
#             cliente.nombre_completo or "",
#             cliente.fecha_inicio.strftime('%d/%m/%Y') if cliente.fecha_inicio else "",
#             cliente.hora_inicio.strftime('%H:%M') if cliente.hora_inicio else "",
#             cliente.hora_fin.strftime('%H:%M') if cliente.hora_fin else "",
#             cliente.user.username if cliente.user else "",
#         ]
#         datos.append(datos_cliente)

#     # Crea la tabla y establece el estilo
#     tabla = Table(datos)
#     tabla.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     # Ajusta automáticamente el espacio de las columnas al contenido
#     tabla.autoSpace = True

#     # Agrega la tabla al contenido del PDF
#     elements.append(tabla)

#     # Construye el PDF
#     doc.build(elements)

#     return response

# # Obtén datos para el informe (personalízalo según tus necesidades)
    # clientes = Cliente.objects.all()

    # # Configura el tamaño de la hoja en orientación horizontal (landscape)
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="informe_reservas_por_cliente.pdf"'
    # doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # # Contenedor para los elementos del PDF
    # elements = []

    # # Configura los estilos para el informe
    # styles = getSampleStyleSheet()
    # estilo_titulo = styles['Heading1']
    # estilo_normal = styles['Normal']

    # # Agrega el título al informe
    # titulo = Paragraph("Informe de Reservas de Laboratorio por Cliente", estilo_titulo)
    # elements.append(titulo)

    # # Crea una lista para los datos de las reservas
    # datos = []
    # encabezados = ["Cliente", "Fecha de Reserva", "Laboratorio", "Hora de Inicio", "Hora de Fin"]
    # datos.append(encabezados)

    # for cliente in clientes:
    #     reservas_cliente = Consulta.objects.filter(cliente=cliente)
    #     for reserva in reservas_cliente:
    #         datos_reserva = [
    #             cliente.nombre_completo if cliente.nombre_completo else "",
    #             reserva.agenda.dia.strftime('%d/%m/%Y') if reserva.agenda else "",
    #             reserva.agenda.laboratorio.nombre if reserva.agenda and reserva.agenda.laboratorio else "",
    #             reserva.agenda.horario if reserva.agenda else "",
    #             "",  # No se proporciona hora de fin en el modelo Consulta
    #         ]
    #         datos.append(datos_reserva)

    # # Crea la tabla y establece el estilo
    # tabla = Table(datos)
    # tabla.setStyle(TableStyle([
    #     ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    #     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    #     ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
    #     ('GRID', (0, 0), (-1, -1), 1, colors.black),
    # ]))

    # # Ajusta automáticamente el espacio de las columnas al contenido
    # tabla.autoSpace = True

    # # Agrega la tabla al contenido del PDF
    # elements.append(tabla)

    # # Construye el PDF
    # doc.build(elements)

    # return response

   # Obtén datos para el informe (personalízalo según tus necesidades)
   # Filtra las consultas que tengan un horario seleccionado por el cliente
     # Filtra las consultas que tengan un horario seleccionado por el cliente
  # Filtra las consultas que tienen un horario seleccionado por el cliente


  #Origin
#  # Filtra las consultas que tengan un horario seleccionado por el cliente
#     consultas = Consulta.objects.exclude(horario_cliente__isnull=True)
    
#     # Configura el tamaño de la hoja en orientación horizontal (landscape)
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="informe_reservas_por_cliente.pdf"'
#     doc = SimpleDocTemplate(response, pagesize=landscape(letter))

#     # Contenedor para los elementos del PDF
#     elements = []

#     # Configura los estilos para el informe
#     styles = getSampleStyleSheet()
#     estilo_titulo = styles['Heading1']
#     estilo_normal = styles['Normal']

#     # Agrega el título al informe
#     titulo = Paragraph("Informe de Reservas de Laboratorio por Cliente", estilo_titulo)
#     elements.append(titulo)

#     # Crea una lista para los datos de las reservas
#     datos = []
#     encabezados = ["Cliente", "Fecha de Reserva", "Laboratorio", "Horario", "Carrera"]
#     datos.append(encabezados)

#     for consulta in consultas:
#         cliente = consulta.cliente
#         reserva = consulta.agenda

#         # Verifica que la reserva esté completa (con laboratorio y horario)
#         if reserva and reserva.laboratorio and reserva.horario:

#         #     datos.append(datos_reserva)
#             carrera_del_cliente = cliente.carrera  # Accede a la carrera del laboratorio seleccionado por el cliente
         

#             datos_reserva = [
                
#                 cliente.nombre_completo if cliente.nombre_completo else "",
#                 reserva.dia.strftime('%d/%m/%Y'),
#                 reserva.laboratorio.nombre,
#                 reserva.get_horario_display(),
#                 carrera_del_cliente.nombre if carrera_del_cliente else "",  # Agrega la carrera del cliente si existe
#             ]

#             datos.append(datos_reserva) 


#     # Crea la tabla y establece el estilo
#     tabla = Table(datos)
#     tabla.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     # Ajusta automáticamente el espacio de las columnas al contenido
#     tabla.autoSpace = True

#     # Agrega la tabla al contenido del PDF
#     elements.append(tabla)

#     # Construye el PDF
#     doc.build(elements)

#     return response



    consultas = Consulta.objects.exclude(horario_cliente__isnull=True)
        
    # Configura el tamaño de la hoja en orientación horizontal (landscape)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_reservas_por_cliente.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # Contenedor para los elementos del PDF
    elements = []

    # Configura los estilos para el informe
    styles = getSampleStyleSheet()
    estilo_titulo = styles['Heading1']
    estilo_normal = styles['Normal']

    # Agrega el título al informe
    titulo = Paragraph("Informe de Reservas de Laboratorio por Cliente", estilo_titulo)
    elements.append(titulo)

    # Crea una lista para los datos de las reservas
    datos = []
    encabezados = ["Cliente", "Fecha de Reserva", "Laboratorio", "Horario", "Carrera"]
    datos.append(encabezados)

    for consulta in consultas:
        cliente = consulta.cliente
        reserva = consulta.agenda

        # Verifica que la reserva esté completa (con laboratorio y horario)
        if reserva and reserva.laboratorio and reserva.horario:
            # Obtén la carrera del laboratorio seleccionado por el cliente
            carrera_del_cliente = reserva.laboratorio.carreras  # Accede a la carrera del laboratorio seleccionado por el cliente

            datos_reserva = [
                cliente.nombre_completo if cliente.nombre_completo else "",
                reserva.dia.strftime('%d/%m/%Y'),
                reserva.laboratorio.nombre,
                reserva.get_horario_display(),
                carrera_del_cliente.nombre if carrera_del_cliente else "",  # Agrega la carrera del cliente si existe
            ]

            datos.append(datos_reserva) 

    # Crea la tabla y establece el estilo
    tabla = Table(datos)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Ajusta automáticamente el espacio de las columnas al contenido
    tabla.autoSpace = True

    # Agrega la tabla al contenido del PDF
    elements.append(tabla)

    # Construye el PDF
    doc.build(elements)

    return response





  # Tu código para obtener las consultas aquí...

    # Configura el tamaño de la hoja en orientación horizontal (landscape)
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="informe_reservas_por_cliente.pdf"'
    # doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # # Contenedor para los elementos del PDF
    # elements = []

    # # Configura los estilos para el informe
    # styles = getSampleStyleSheet()
    # estilo_titulo = styles['Heading1']
    # estilo_normal = styles['Normal']

    # # Agrega el título al informe con un estilo personalizado
    # titulo = Paragraph("Informe de Reservas de Laboratorio por Cliente", estilo_titulo)
    # elements.append(titulo)

    # # Crea una lista para los datos de las reservas
    # datos = []
    # encabezados = ["Cliente", "Fecha de Reserva", "Laboratorio", "Horario", "Carrera"]
    # datos.append(encabezados)

    # for consulta in consultas:
    #     cliente = consulta.cliente
    #     reserva = consulta.agenda

    #     # Verifica que la reserva esté completa (con laboratorio y horario)
    #     if reserva and reserva.laboratorio and reserva.horario:
    #         carrera_del_cliente = cliente.carrera  # Accede a la carrera del laboratorio seleccionado por el cliente
    #         datos_reserva = [
    #             cliente.nombre_completo if cliente.nombre_completo else "",
    #             reserva.dia.strftime('%d/%m/%Y'),
    #             reserva.laboratorio.nombre,
    #             reserva.get_horario_display(),
    #             carrera_del_cliente.nombre if carrera_del_cliente else "",  # Agrega la carrera del cliente si existe
    #         ]

    #         datos.append(datos_reserva)

    # # Crea la tabla y establece el estilo
    # tabla = Table(datos)
    # tabla.setStyle(TableStyle([
    #     ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    #     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    #     ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
    #     ('GRID', (0, 0), (-1, -1), 1, colors.black),
    #     ('GRID', (0, 0), (-1, 0), 2, colors.black),  # Línea más gruesa para la primera fila (encabezados)
    # ]))

    # # Ajusta automáticamente el espacio de las columnas al contenido
    # tabla.autoSpace = True

    # # Agrega la tabla al contenido del PDF
    # elements.append(tabla)

    # # Construye el PDF
    # doc.build(elements)

    # return response

cliente_registro = ClienteCreateView.as_view()
cliente_actualizar = ClienteUpdateView.as_view()
consulta_lista = ConsultaListView.as_view()
consulta_registro = ConsultaCreateView.as_view()
consulta_actualizar = ConsultaUpdateView.as_view()
consulta_excluir = ConsultaDeleteView.as_view()
consulta_laboratorio = GetConsultaDateView.as_view()
generar_informe_clientes_pdf = generar_informe_clientes_pdf
