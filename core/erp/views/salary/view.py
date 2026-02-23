import json
import logging
from datetime import date
from datetime import datetime
from decimal import Decimal
from io import BytesIO

logger = logging.getLogger(__name__)

# import openpyxl
import xlsxwriter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum, Q, DecimalField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import *
from core.erp.encoders import CustomJSONEncoder
from core.erp.forms import SalaryForm
from core.erp.models import Salary, SalaryDetail, Employee, Headings, SalaryHeadings
from core.erp.mixins import *


class SalaryListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, FormView):
    form_class = SalaryForm
    template_name = 'salary/list.html'
    permission_required = 'view_salary'

    def get_form(self, form_class=None):
        form = SalaryForm()
        form.fields['year'].initial = datetime.now().date().year
        return form

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search':
                data = []
                year = request.POST['year']
                month = request.POST['month']
                pks = json.loads(request.POST['pks'])
                queryset = SalaryDetail.objects.filter()
                if len(year):
                    queryset = SalaryDetail.objects.filter(salary__year=year)
                if len(month):
                    queryset = SalaryDetail.objects.filter(salary__month=month)
                if len(pks):
                    queryset = SalaryDetail.objects.filter(employee__id__in=pks)
                if len(month) and len(pks):
                    queryset = SalaryDetail.objects.filter(employee__id__in=pks, salary__month=month)
                for i in queryset:
                    data.append(i.toJSON())
            elif action == 'search_employee':
                data = []
                term = request.POST['term']
                for i in Employee.objects.filter(
                        Q(person__firstname__icontains=term) | Q(person__cedula__icontains=term) | Q(
                            codigo__icontains=term), estado='Contratado').order_by('person__employee')[0:5]:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)
            elif action == 'search_detail_headings':
                data = []
                detail = SalaryDetail.objects.get(pk=request.POST['id'])
                for i in detail.salaryheadings_set.filter(headings__type='remuneracion', valor__gt=0).order_by(
                        'headings__order'):
                    data.append([i.headings.name, i.get_cant(), i.get_valor_format(), '---'])
                for i in detail.salaryheadings_set.filter(headings__type='descuentos', valor__gt=0).order_by(
                        'headings__order'):
                    data.append([i.headings.name, i.get_cant(), '---', i.get_valor_format()])
                data.append(['     ', '     ', '     ', '     '])
                data.append(['Subtotal de Ingresos', '---', f'${detail.get_income_format()}', '-----'])
                data.append(['Subtotal de Descuentos', '---', '---', detail.get_expenses_format()])
                data.append(['Total a recibir', '---', '---', detail.get_total_amount_format()])
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
                with transaction.atomic():
                    salary = \
                    Salary.objects.get_or_create(year=int(request.POST['year']), month=int(request.POST['month']))[0]
                    for i in json.loads(request.POST['headings']):
                        heading = i
                        employee = Employee.objects.get(pk=int(heading['employee']['id']))
                        salary_detail = SalaryDetail()
                        queryset = salary.salarydetail_set.filter(employee=employee)
                        if queryset.exists():
                            salary_detail = queryset[0]
                            salary_detail.salaryheadings_set.all().delete()
                        else:
                            salary_detail.salary_id = salary.id
                            salary_detail.employee_id = employee.id
                            salary_detail.save()
                        del heading['employee']
                        del heading['total_discounts']
                        del heading['total_charge']
                        del heading['total_assets']
                        for key, value in heading.items():
                            detail = SalaryHeadings()
                            detail.salary_detail_id = salary_detail.id
                            detail.headings_id = int(value['id'])
                            detail.cant = int(value['cant'])
                            detail.valor = int(value['amount'])
                            detail.save()
                        salary_detail.income = salary_detail.salaryheadings_set.filter(
                            headings__type='remuneracion').aggregate(
                            result=Coalesce(Sum('valor', ), 0.00, output_field=DecimalField())).get('result')
                        salary_detail.expenses = salary_detail.salaryheadings_set.filter(
                            headings__type='descuentos').aggregate(
                            result=Coalesce(Sum('valor', default=0.00), 0.00, output_field=DecimalField())).get(
                            'result')
                        salary_detail.total_amount = float(salary_detail.income) - float(salary_detail.expenses)
                        salary_detail.save()
            elif action == 'search_employee':
                data = []
                term = request.POST['term']
                for i in Employee.objects.filter(
                        Q(person__firstname__icontains=term) | Q(person__cedula__icontains=term) | Q(
                            codigo__icontains=term), estado='Contratado').order_by('person__employee')[0:10]:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)
            elif action == 'search_employees':
                detail = []
                year = int(request.POST['year'])
                month = int(request.POST['month'])
                employees_ids = json.loads(request.POST['employees_ids'])
                employees = Employee.objects.filter(estado='Contratado')
                if len(employees_ids):
                    employees = employees.filter(id__in=employees_ids)
                    logger.debug("Filtering employees: %s", employees_ids)
                columns = [{'data': 'employees.person.first_name'}]

                headings = Headings.objects.filter(state=True)
                for i in headings.filter(type='remuneracion').order_by('type', 'order', 'has_quantity'):
                    if i.has_quantity:
                        columns.append({'data': f'{i.code}.cant'})
                    columns.append({'data': i.code})
                columns.append({'data': 'total_assets'})
                for i in headings.filter(type='descuentos').order_by('type', 'order'):
                    if i.has_quantity:
                        columns.append({'data': f'{i.code}.cant'})
                    columns.append({'data': i.code})
                columns.append({'data': 'total_discounts'})
                columns.append({'data': 'total_charge'})
                for employee in employees:
                    heading = {}
                    for d in headings.filter(type='remuneracion').order_by('order'):
                        item = d.toJSON()
                        item['cant'] = 0
                        item['amount'] = 0.00
                        if d.code == 'salario':
                            item['amount'] = float(employee.salary)
                            item['cant'] = employee.get_amount_of_assists(year, month)
                        queryset = d.get_amount_detail_salary(employee=employee.id, year=year, month=month)
                        if queryset is not None:
                            item['amount'] = float(queryset.valor)
                            item['cant'] = queryset.cant
                        heading[d.code] = item
                    for d in headings.filter(type='descuentos').order_by('order'):
                        item = d.toJSON()
                        item['cant'] = 0
                        item['amount'] = 0.00
                        queryset = d.get_amount_detail_salary(employee=employee.id, year=year, month=month)
                        if queryset is not None:
                            item['amount'] = float(queryset.valor)
                            item['cant'] = queryset.cant
                        heading[d.code] = item
                    salary_detail = SalaryDetail.objects.filter(employee_id=employee.id, salary__year=year,salary__month=month)
                    if salary_detail.exists():
                        salary_detail = salary_detail[0]
                        heading['total_assets'] = {'code': 'total_assets', 'amount': float(salary_detail.income)}
                        heading['total_discounts'] = {'code': 'total_discounts','amount': float(salary_detail.expenses)}
                        heading['total_charge'] = {'code': 'total_charge', 'amount': float(salary_detail.total_amount)}
                    else:
                        heading['total_assets'] = {'code': 'total_assets', 'amount': 0.00}
                        heading['total_discounts'] = {'code': 'total_discounts', 'amount': 0.00}
                        heading['total_charge'] = {'code': 'total_charge', 'amount': float(employee.salary)}
                    heading['employee'] = employee.toJSON()
                    detail.append(heading)
                data = {'detail': detail, 'columns': columns}
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
