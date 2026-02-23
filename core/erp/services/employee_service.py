import logging

from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.db.models.functions import Concat

from core.erp.models import Employee

logger = logging.getLogger(__name__)


def search_employees(search_value, start, length):
    employees = Employee.objects.annotate(
        full_name=Concat('person__firstname', Value(' '), 'person__lastname')
    ).filter(
        Q(id__icontains=search_value) |
        Q(hiring_date__icontains=search_value) |
        Q(codigo__icontains=search_value) |
        Q(full_name__icontains=search_value) |
        Q(department__name__icontains=search_value) |
        Q(position__name__icontains=search_value) |
        Q(turn__name__icontains=search_value) |
        Q(salary__icontains=search_value) |
        Q(estado__icontains=search_value)
    ).order_by('id')

    total_count = Employee.objects.all().count()
    paginator = Paginator(employees, length if length else total_count)
    page_number = start // length + 1 if length else 1
    page = paginator.get_page(page_number)

    return {
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


def deactivate_employee(employee_id):
    employee = Employee.objects.get(pk=employee_id)
    if employee.estado in ('Contratado', 'Vacaciones', 'Licencia'):
        employee.estado = 'Despedido'
    employee.save()


def activate_employee(employee_id):
    employee = Employee.objects.get(pk=employee_id)
    if employee.estado in ('Despedido', 'Vacaciones', 'Licencia'):
        employee.estado = 'Contratado'
    employee.save()
