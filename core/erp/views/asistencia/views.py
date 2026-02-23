import json
from datetime import *
from decimal import Decimal
from io import BytesIO
import datetime
import xlsxwriter as xlsxwriter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.views.generic import *
from core.erp.encoders import CustomJSONEncoder
from core.erp.forms import *
from core.erp.mixins import *
from core.erp.models import *


class AssistanceListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, FormView):
    form_class = AssistanceForm
    template_name = 'attendance/list.html'
    permission_required = 'view_assistance'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search':
                data = []
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                queryset = AssistanceDetail.objects.all()
                if len(start_date) and len(end_date):
                    queryset = queryset.filter(assistance__date_joined__range=[start_date, end_date])
                for i in queryset.order_by('assistance__date_joined'):
                    data.append(i.toJSON())
            elif action == 'export_assistences_excel':
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                queryset = AssistanceDetail.objects.all()
                if len(start_date) and len(end_date):
                    queryset = queryset.filter(assistance__date_joined__range=[start_date, end_date])
                headers = {
                    'Fecha de asistencia': 35,
                    'Empleado': 35,
                    'Cedula': 35,
                    'Cargo': 35,
                    'Departamento': 35,
                    'Observación': 55,
                    'Asistencia': 35,
                }
                output = BytesIO()
                workbook = xlsxwriter.Workbook(output)
                worksheet = workbook.add_worksheet('asistencias')
                cell_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
                row_format = workbook.add_format({'align': 'center', 'border': 1})
                index = 0
                for name, width in headers.items():
                    worksheet.set_column(first_col=0, last_col=index, width=width)
                    worksheet.write(0, index, name, cell_format)
                    index += 1
                row = 1
                for i in queryset.order_by('assistance__date_joined'):
                    worksheet.write(row, 0, i.assistance.date_joined_format(), row_format)
                    worksheet.write(row, 1, i.employee.get_full_name(), row_format)
                    worksheet.write(row, 2, i.employee.person.cedula, row_format)
                    worksheet.write(row, 3, i.employee.position.name, row_format)
                    worksheet.write(row, 4, i.employee.department.name, row_format)
                    worksheet.write(row, 5, i.description, row_format)
                    worksheet.write(row, 6, 'Si' if i.state else 'No', row_format)
                    row += 1
                workbook.close()
                output.seek(0)
                response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                print(response)
                response[
                    'Content-Disposition'] = f"attachment; filename='ASISTENCIAS_{datetime.datetime.now().date().strftime('%d_%m_%Y')}.xlsx'"
                return response
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
            print(data['error'])
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Asistencias'
        context['create_url'] = reverse_lazy('erp:asistencia_create')
        context['entity'] = 'Asistencias'
        return context


class AssistanceCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Assistance
    template_name = 'attendance/create.html'
    form_class = AssistanceForm
    success_url = reverse_lazy('erp:asistencia_list')
    permission_required = 'add_assistance'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                with transaction.atomic():
                    date_joined = datetime.datetime.strptime(request.POST['date_joined'], '%Y-%m-%d')
                    assistance = Assistance()
                    assistance.date_joined = date_joined
                    assistance.year = date_joined.year
                    assistance.month = date_joined.month
                    assistance.day = date_joined.day
                    assistance.save()
                    for i in json.loads(request.POST['assistances']):
                        detail = AssistanceDetail()
                        detail.assistance_id = assistance.id
                        detail.employee_id = int(i['id'])
                        detail.description = i['description']
                        detail.state = i['state']
                        detail.save()
            elif action == 'generate_assistance':
                data = []
                for i in Employee.objects.filter(estado='Contratado').order_by('id'):
                    item = i.toJSON()
                    item['state'] = 0
                    item['description'] = ''
                    data.append(item)
            elif action == 'validate_data':
                data = {
                    'valid': not Assistance.objects.filter(date_joined=request.POST['date_joined'].strip()).exists()
                }
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Nuevo registro de una Asistencia'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Asistencias'
        return context


class AssistanceUpdateView(LoginRequiredMixin, FormView):
    template_name = 'attendance/create.html'
    form_class = AssistanceForm
    success_url = reverse_lazy('erp:asistencia_list')
    permission_required = 'change_assistance'

    def get_form(self, form_class=None):
        form = AssistanceForm(initial={'date_joined': self.kwargs['date_joined']})
        form.fields['date_joined'].widget.attrs.update({'disabled': True})
        return form

    def get_object(self):
        # date_joined = datetime.datetime.now()
        queryset = Assistance.objects.filter(date_joined=self.kwargs['date_joined'])
        if queryset.exists():
            return queryset[0]
        return None

    def get(self, request, *args, **kwargs):
        if self.get_object() is not None:
            return super().get(request, *args, **kwargs)
        messages.error(request,
                       f"No se puede editar las asistencia del dia {self.kwargs['date_joined']} porque no existen")
        return HttpResponseRedirect(self.success_url)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                with transaction.atomic():
                    for i in json.loads(request.POST['assistances']):
                        if 'pk' in i:
                            detail = AssistanceDetail.objects.get(pk=i['pk'])
                        else:
                            date_joined = datetime.datetime.strptime(self.kwargs['date_joined'], '%Y-%m-%d')
                            assistance =  Assistance.objects.get_or_create(date_joined=date_joined, year=date_joined.year,
                                                                 month=date_joined.month, day=date_joined.day)[0]
                            detail = AssistanceDetail()
                            detail.assistance_id = assistance.id
                        detail.employee_id = i['id']
                        detail.description = i['description']
                        detail.state = i['state']
                        detail.save()
            elif action == 'generate_assistance':
                data = []
                date_joined = self.kwargs['date_joined']
                for i in Employee.objects.filter(person__isnull=False):
                    item = i.toJSON()
                    item['state'] = 0
                    item['description'] = ''
                    queryset = AssistanceDetail.objects.filter(assistance__date_joined=date_joined, employee_id=i.id)
                    if queryset.exists():
                        assistance_detail = queryset[0]
                        item['pk'] = assistance_detail.id
                        item['state'] = 1 if assistance_detail.state else 0
                        item['description'] = assistance_detail.description
                    data.append(item)
            elif action == 'validate_data':
                data = {'valid': not Assistance.objects.filter(date_joined=request.POST['date_joined']).exclude(
                    date_joined=self.kwargs['date_joined']).exists()}
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Edición de una Asistencia'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context


class AssistanceDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, TemplateView):
    template_name = 'attendance/delete.html'
    success_url = reverse_lazy('erp:asistencia_list')
    permission_required = 'delete_assistance'

    def get(self, request, *args, **kwargs):
        if self.get_object() is not None:
            return super(AssistanceDeleteView, self).get(request, *args, **kwargs)
        messages.error(request, 'No existen asistencias en el rango de fechas ingresadas')
        return HttpResponseRedirect(self.success_url)

    def get_object(self, queryset=None):
        start_date = self.kwargs['start_date']
        end_date = self.kwargs['end_date']
        queryset = Assistance.objects.filter(date_joined__range=[start_date, end_date])
        if queryset.exists():
            return queryset[0]
        return None

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        context['start_date'] = self.kwargs['start_date']
        context['end_date'] = self.kwargs['end_date']
        return context