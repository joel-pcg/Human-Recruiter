import json
import logging
from io import BytesIO
import datetime
import xlsxwriter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import *
from core.erp.encoders import CustomJSONEncoder
from core.erp.forms import *
from core.erp.mixins import *
from core.erp.models import *
from core.erp.services.attendance_service import (
    search_attendance,
    create_attendance,
    update_attendance,
    generate_attendance_list_new,
    validate_attendance_date,
)

logger = logging.getLogger(__name__)


class AssistanceListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, FormView):
    form_class = AssistanceForm
    template_name = 'attendance/list.html'
    permission_required = 'view_assistance'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search':
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                data = search_attendance(start_date, end_date)
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
                response[
                    'Content-Disposition'] = f"attachment; filename='ASISTENCIAS_{datetime.datetime.now().date().strftime('%d_%m_%Y')}.xlsx'"
                return response
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            logger.exception("Error in AssistanceListView")
            data['error'] = str(e)
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
                create_attendance(
                    date_str=request.POST['date_joined'],
                    assistances_json=json.loads(request.POST['assistances']),
                )
            elif action == 'generate_assistance':
                data = generate_attendance_list_new()
            elif action == 'validate_data':
                data = {'valid': validate_attendance_date(request.POST['date_joined'])}
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
                update_attendance(
                    date_str=self.kwargs['date_joined'],
                    assistances_json=json.loads(request.POST['assistances']),
                )
            elif action == 'generate_assistance':
                date_joined = self.kwargs['date_joined']
                data = generate_attendance_list_new(date_joined=date_joined)
            elif action == 'validate_data':
                data = {
                    'valid': validate_attendance_date(
                        request.POST['date_joined'],
                        exclude_date=self.kwargs['date_joined'],
                    )
                }
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
