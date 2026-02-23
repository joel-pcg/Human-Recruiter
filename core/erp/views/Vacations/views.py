import json
from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.views.generic import ListView, CreateView, UpdateView
from weasyprint import HTML

from core.erp.encoders import CustomJSONEncoder
from core.erp.forms import *
from core.erp.mixins import *
from core.erp.models import *


class VacationsListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Vacations
    template_name = 'vacations/list.html'
    permission_required = 'view_vacations'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Vacations.objects.all():
                    data.append(i.toJSON())
            elif action == 'delete':
                vacations = Vacations.objects.get(pk=request.POST['id'])
                vacations.delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listados de Vacaciones'
        context['entity'] = 'Vacaciones'
        context['create_url'] = reverse_lazy('erp:vacations_create')
        return context


class VacationsCreatView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Vacations
    form_class = VacationsForm
    template_name = 'Vacations/create.html'
    permission_required = 'add_vacations'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Solicitud de Vacaciones'
        context['entity'] = 'Vacaciones'
        context['list_url'] = reverse_lazy('erp:vacations_list')
        context['action'] = 'add'
        return context


class VacationsUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Vacations
    form_class = VacationsForm
    template_name = 'Vacations/create.html'
    permission_required = 'change_vacations'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de una solicitud de Vacaciones'
        context['entity'] = 'Vacaciones'
        context['list_url'] = reverse_lazy('erp:vacations_list')
        context['action'] = 'edit'
        return context


def send_email_vacation_finished(vacations):
    try:
        mailServer = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        email_to = vacations.empleado.person.email
        messages = MIMEMultipart()
        messages['From'] = settings.EMAIL_HOST_USER
        messages['To'] = email_to
        messages['Subject'] = "Recordatorio: Vacaciones Finalizadas"

        # Personaliza el mensaje
        content = render_to_string('Vacations/vacation_finished.html', {'vacations': vacations})

        messages.attach(MIMEText(content, 'html'))
        mailServer.sendmail(settings.EMAIL_HOST_USER, email_to, messages.as_string())
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir al enviar el correo
        print(f"Error al enviar el correo: {str(e)}")


def send_reminder_vacation_ending(vacations):
    try:
        mailServer = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        email_to = vacations.empleado.person.email
        messages = MIMEMultipart()
        messages['From'] = settings.EMAIL_HOST_USER
        messages['To'] = email_to
        messages['Subject'] = "Recordatorio: Vacaciones tus finalizan mañana"
        content = render_to_string('Vacations/vacation_reminder.html', {'vacations': vacations})
        messages.attach(MIMEText(content, 'html'))
        mailServer.sendmail(settings.EMAIL_HOST_USER, email_to, messages.as_string())

    except Exception as e:
        print(f"Error al enviar el correo de recordatorio: {str(e)}")


def generate_pdf_report(request,pk):
    empleado = Employee.objects.get(id=pk)
    vacations = Vacations.objects.filter(empleado=empleado)
    company = Company.objects.first()
    current_day = datetime.date.today()
    template = get_template("pdf_vacations.html")
    context = {
        'fecha': current_day,
        "vacations": vacations,
        'compañia': company,
    }
    html_template = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Solicitud_de_Vacaciones.pdf"'
    HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf(response)
    return response

