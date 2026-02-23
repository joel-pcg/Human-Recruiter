import json
import logging
from decimal import Decimal
import datetime
from datetime import date

logger = logging.getLogger(__name__)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from weasyprint import HTML

from core.erp.encoders import CustomJSONEncoder
from core.erp.forms import *
from core.erp.models import *
from core.erp.mixins import *
from django.core.paginator import Paginator


class EmpleadoListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Employee
    template_name = 'empleado/list.html'
    permission_required = 'view_employee'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                search_value = request.POST.get('search[value]', '')
                employees = Employee.objects.annotate(
                    full_name=Concat('person__firstname', Value(' '), 'person__lastname')
                ).filter(
                    Q(id__icontains=search_value) |
                    Q(hiring_date__icontains=search_value) |
                    Q(codigo__icontains=search_value) |
                    Q(full_name__icontains=search_value) |  # Búsqueda por nombre completo usando el método get_full_name
                    Q(department__name__icontains=search_value) |
                    Q(position__name__icontains=search_value) |
                    Q(turn__name__icontains=search_value) |
                    Q(salary__icontains=search_value) |
                    Q(estado__icontains=search_value)
                ).order_by('id')

                e = Employee.objects.all().count()

                paginator = Paginator(employees, request.POST.get('length', e))
                start = int(request.POST.get('start', 0))
                length = int(request.POST.get('length', 10))
                page_number = start // length + 1
                page = paginator.get_page(page_number)

                data = {
                    'data': [
                        {
                            'id': employee.id,
                            'hiring_date': employee.hiring_date.strftime('%Y-%m-%d'),
                            'codigo': employee.codigo,
                            'full_name': employee.get_full_name(),
                            'department__name': employee.department.name,
                            'position__name': employee.position.name,
                            'turn__name': employee.turn.name,
                            'salary': employee.format_salary_as_dominican_currency(),
                            'estado': employee.estado,
                        }
                        for employee in page
                    ],
                    'recordsTotal': employees.count(),
                    'recordsFiltered': paginator.count,
                }
            elif action == 'deactive':
                employe = Employee.objects.get(pk=request.POST['id'])
                if employe.estado == 'Contratado' or employe.estado == 'Vacaciones' or employe.estado == 'Licencia':
                    employe.estado = 'Despedido'
                    employe.save()
                else:
                    employe.save()
            elif action == 'active':
                employe = Employee.objects.get(pk=request.POST['id'])
                if employe.estado == 'Despedido'or employe.estado == 'Vacaciones' or employe.estado == 'Licencia':
                    employe.estado = 'Contratado'  # Contratado
                    employe.save()
                else:
                    employe.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de empleados'
        context['entity'] = 'Empleados'
        context['list_url'] = reverse_lazy('erp:empleados_list')
        context['create_url'] = reverse_lazy('erp:empleados_create')
        context['estados'] = Employee.objects.values_list('estado', flat=True).distinct()
        return context


class EmpleadoCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Employee
    template_name = 'empleado/create.html'
    form_class = EmployeForm
    permission_required = 'add_employee'

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
        context['title'] = 'Crea un empleado'
        context['entity'] = 'Empleados'
        context['action'] = 'add'
        context['list_url'] = reverse_lazy('erp:empleados_list')
        context['create_url'] = reverse_lazy('erp:empleados_create')
        return context


class EmpleadoUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Employee
    template_name = 'empleado/create.html'
    form_class = EmployeForm
    permission_required = 'change_employee'

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
        context['title'] = 'Edita un empleado'
        context['entity'] = 'Empleados'
        context['action'] = 'edit'
        context['list_url'] = reverse_lazy('erp:empleados_list')
        context['create_url'] = reverse_lazy('erp:empleados_create')
        return context


class EmpleadoInformeView(View):
    def get(self, request, *args, **kwargs):
        try:
            employee = Employee.objects.get(pk=self.kwargs['pk'])
            start_turn = datetime.combine(datetime.now(), employee.turn.start_turn)
            end_turn = datetime.combine(datetime.now(), employee.turn.end_turn)
            shift_duration = end_turn - start_turn
            total_hours = int(shift_duration.total_seconds() * 5 / 3600)
            template = get_template("empleado/report-empleado.html")
            context = {
                'employee': employee,
                "company" : Company.objects.first(),
                "current_day" : datetime.today(),
                'total_hours':total_hours
            }
            html_template = template.render(context)
            # Crear un flujo de bytes para el archivo PDF
            pdf_file = HTML(string=html_template,base_url=request.build_absolute_uri()).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="Informe_personal_de_empleado.pdf"'
            return response
        except Exception as e:
            logger.exception("Error generating employee report")
        return HttpResponseRedirect(reverse_lazy('erp:empleados_list'))


def generar_informe_empleados(request):
    company = Company.objects.first()
    current_day = datetime.today()
    estado = request.GET.get('estado')
    total_empleado = Employee.objects.filter(estado=estado).count()

    if estado:
        empleados = Employee.objects.filter(estado=estado).order_by('person__employee')
    else:
        empleados = Employee.objects.all()
    context = {
        'empleados': empleados,
        'company': company,
        'fecha': current_day,
        'title': estado,
        "total_empleado":total_empleado
    }
    html_string = render_to_string('pdf_report_employee.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=informe_empleados_{estado}.pdf'
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    return response
