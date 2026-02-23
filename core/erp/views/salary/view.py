import json
import logging
from datetime import datetime
from io import BytesIO

logger = logging.getLogger(__name__)

import xlsxwriter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import *
from core.erp.encoders import CustomJSONEncoder
from core.erp.forms import SalaryForm
from core.erp.models import Salary, SalaryDetail, Headings
from core.erp.mixins import *
from core.erp.services.salary_service import (
    search_salary_details,
    search_employees_by_term,
    get_salary_heading_details,
    create_or_update_salary,
    build_salary_worksheet_data,
)


class SalaryListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, FormView):
    form_class = SalaryForm
    template_name = 'salary/list.html'
    permission_required = 'view_salary'

    def get_form(self, form_class=None):
        form = SalaryForm()
        form.fields['year'].initial = datetime.now().date().year
        return form

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search':
                year = request.POST['year']
                month = request.POST['month']
                pks = json.loads(request.POST['pks'])
                data = search_salary_details(year, month, pks)
            elif action == 'search_employee':
                term = request.POST['term']
                data = search_employees_by_term(term, limit=5)
            elif action == 'search_detail_headings':
                data = get_salary_heading_details(request.POST['id'])
            elif action == 'export_salaries_excel':
                year = request.POST['year']
                month = request.POST['month']
                pks = json.loads(request.POST['pks'])
                queryset = SalaryDetail.objects.filter(salary__year=year)
                if len(month):
                    queryset = queryset.filter(salary__month=month)
                if len(pks):
                    queryset = queryset.filter(employee_id__in=pks)
                headers = {
                    'Fecha de ingreso': 35,
                    'Código': 15,
                    'Empleado': 35,
                    'Número de documento': 35,
                    'Total a cobrar': 35
                }
                output = BytesIO()
                workbook = xlsxwriter.Workbook(output)
                worksheet = workbook.add_worksheet('planilla')
                cell_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
                row_format = workbook.add_format({'align': 'center', 'border': 1})
                index = 0
                for name, width in headers.items():
                    worksheet.set_column(first_col=0, last_col=index, width=width)
                    worksheet.write(0, index, name, cell_format)
                    index += 1
                row = 1
                for salary_detail in queryset.order_by('employee'):
                    worksheet.write(row, 0, salary_detail.employee.hiring_date_format(), row_format)
                    worksheet.write(row, 1, salary_detail.employee.codigo, row_format)
                    worksheet.write(row, 2, salary_detail.employee.get_full_name(), row_format)
                    worksheet.write(row, 3, salary_detail.employee.person.cedula, row_format)
                    worksheet.write(row, 4, salary_detail.get_total_amount_format(), row_format)
                    row += 1
                workbook.close()
                output.seek(0)
                response = HttpResponse(output,
                                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response[
                    'Content-Disposition'] = f"attachment; filename='PLANILLA_{datetime.now().date().strftime('%d_%m_%Y')}.xlsx'"
                return response
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super(SalaryListView, self).get_context_data()
        context['title'] = 'Listado de Nomina'
        context['entity'] = 'Nomina'
        context['create_url'] = reverse_lazy('erp:salary_create')
        return context


class SalaryCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Salary
    template_name = 'salary/create.html'
    form_class = SalaryForm
    success_url = reverse_lazy('erp:salary_list')
    permission_required = 'add_salary'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']

        data = {}
        try:
            if action == 'add':
                create_or_update_salary(
                    year=request.POST['year'],
                    month=request.POST['month'],
                    headings_data=json.loads(request.POST['headings']),
                )
            elif action == 'search_employee':
                term = request.POST['term']
                data = search_employees_by_term(term, limit=10)
            elif action == 'search_employees':
                year = int(request.POST['year'])
                month = int(request.POST['month'])
                employees_ids = json.loads(request.POST['employees_ids'])
                data = build_salary_worksheet_data(year, month, employees_ids)
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Generar nueva nomina'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Nomina'
        context['assets'] = Headings.objects.filter(state=True, type='remuneracion').order_by('id')
        context['discounts'] = Headings.objects.filter(state=True, type='descuentos').order_by('id')
        return context
