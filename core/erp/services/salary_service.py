import json
import logging

from django.db import transaction
from django.db.models import Sum, Q, DecimalField
from django.db.models.functions import Coalesce

from core.erp.models import Salary, SalaryDetail, Employee, Headings, SalaryHeadings

logger = logging.getLogger(__name__)


def search_salary_details(year, month, employee_pks):
    queryset = SalaryDetail.objects.filter()
    if len(year):
        queryset = SalaryDetail.objects.filter(salary__year=year)
    if len(month):
        queryset = SalaryDetail.objects.filter(salary__month=month)
    if len(employee_pks):
        queryset = SalaryDetail.objects.filter(employee__id__in=employee_pks)
    if len(month) and len(employee_pks):
        queryset = SalaryDetail.objects.filter(employee__id__in=employee_pks, salary__month=month)
    return [i.toJSON() for i in queryset]


def search_employees_by_term(term, limit=10):
    employees = Employee.objects.filter(
        Q(person__firstname__icontains=term) |
        Q(person__cedula__icontains=term) |
        Q(codigo__icontains=term),
        estado='Contratado'
    ).order_by('person__employee')[:limit]
    data = []
    for emp in employees:
        item = emp.toJSON()
        item['text'] = emp.get_full_name()
        data.append(item)
    return data


def get_salary_heading_details(salary_detail_id):
    detail = SalaryDetail.objects.get(pk=salary_detail_id)
    data = []
    for i in detail.salaryheadings_set.filter(
        headings__type='remuneracion', valor__gt=0
    ).order_by('headings__order'):
        data.append([i.headings.name, i.get_cant(), i.get_valor_format(), '---'])
    for i in detail.salaryheadings_set.filter(
        headings__type='descuentos', valor__gt=0
    ).order_by('headings__order'):
        data.append([i.headings.name, i.get_cant(), '---', i.get_valor_format()])
    data.append(['     ', '     ', '     ', '     '])
    data.append(['Subtotal de Ingresos', '---', f'${detail.get_income_format()}', '-----'])
    data.append(['Subtotal de Descuentos', '---', '---', detail.get_expenses_format()])
    data.append(['Total a recibir', '---', '---', detail.get_total_amount_format()])
    return data


def create_or_update_salary(year, month, headings_data):
    with transaction.atomic():
        salary = Salary.objects.get_or_create(year=int(year), month=int(month))[0]
        for heading in headings_data:
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
                sh = SalaryHeadings()
                sh.salary_detail_id = salary_detail.id
                sh.headings_id = int(value['id'])
                sh.cant = int(value['cant'])
                sh.valor = int(value['amount'])
                sh.save()
            salary_detail.income = salary_detail.salaryheadings_set.filter(
                headings__type='remuneracion'
            ).aggregate(
                result=Coalesce(Sum('valor'), 0.00, output_field=DecimalField())
            ).get('result')
            salary_detail.expenses = salary_detail.salaryheadings_set.filter(
                headings__type='descuentos'
            ).aggregate(
                result=Coalesce(Sum('valor', default=0.00), 0.00, output_field=DecimalField())
            ).get('result')
            salary_detail.total_amount = float(salary_detail.income) - float(salary_detail.expenses)
            salary_detail.save()


def build_salary_worksheet_data(year, month, employee_ids):
    employees = Employee.objects.filter(estado='Contratado')
    if len(employee_ids):
        employees = employees.filter(id__in=employee_ids)
        logger.debug("Filtering employees: %s", employee_ids)
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

    detail = []
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
        salary_detail = SalaryDetail.objects.filter(
            employee_id=employee.id, salary__year=year, salary__month=month
        )
        if salary_detail.exists():
            salary_detail = salary_detail[0]
            heading['total_assets'] = {'code': 'total_assets', 'amount': float(salary_detail.income)}
            heading['total_discounts'] = {'code': 'total_discounts', 'amount': float(salary_detail.expenses)}
            heading['total_charge'] = {'code': 'total_charge', 'amount': float(salary_detail.total_amount)}
        else:
            heading['total_assets'] = {'code': 'total_assets', 'amount': 0.00}
            heading['total_discounts'] = {'code': 'total_discounts', 'amount': 0.00}
            heading['total_charge'] = {'code': 'total_charge', 'amount': float(employee.salary)}
        heading['employee'] = employee.toJSON()
        detail.append(heading)
    return {'detail': detail, 'columns': columns}
