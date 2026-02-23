import datetime
import json
import logging

from django.db import transaction

from core.erp.models import Assistance, AssistanceDetail, Employee

logger = logging.getLogger(__name__)


def search_attendance(start_date, end_date):
    queryset = AssistanceDetail.objects.all()
    if len(start_date) and len(end_date):
        queryset = queryset.filter(assistance__date_joined__range=[start_date, end_date])
    return [i.toJSON() for i in queryset.order_by('assistance__date_joined')]


def create_attendance(date_str, assistances_json):
    with transaction.atomic():
        date_joined = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        assistance = Assistance()
        assistance.date_joined = date_joined
        assistance.year = date_joined.year
        assistance.month = date_joined.month
        assistance.day = date_joined.day
        assistance.save()
        for i in assistances_json:
            detail = AssistanceDetail()
            detail.assistance_id = assistance.id
            detail.employee_id = int(i['id'])
            detail.description = i['description']
            detail.state = i['state']
            detail.save()


def update_attendance(date_str, assistances_json):
    with transaction.atomic():
        for i in assistances_json:
            if 'pk' in i:
                detail = AssistanceDetail.objects.get(pk=i['pk'])
            else:
                date_joined = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                assistance = Assistance.objects.get_or_create(
                    date_joined=date_joined,
                    year=date_joined.year,
                    month=date_joined.month,
                    day=date_joined.day,
                )[0]
                detail = AssistanceDetail()
                detail.assistance_id = assistance.id
            detail.employee_id = i['id']
            detail.description = i['description']
            detail.state = i['state']
            detail.save()


def generate_attendance_list_new(date_joined=None):
    data = []
    if date_joined is None:
        for emp in Employee.objects.filter(estado='Contratado').order_by('id'):
            item = emp.toJSON()
            item['state'] = 0
            item['description'] = ''
            data.append(item)
    else:
        for emp in Employee.objects.filter(person__isnull=False):
            item = emp.toJSON()
            item['state'] = 0
            item['description'] = ''
            queryset = AssistanceDetail.objects.filter(
                assistance__date_joined=date_joined, employee_id=emp.id
            )
            if queryset.exists():
                assistance_detail = queryset[0]
                item['pk'] = assistance_detail.id
                item['state'] = 1 if assistance_detail.state else 0
                item['description'] = assistance_detail.description
            data.append(item)
    return data


def validate_attendance_date(date_str, exclude_date=None):
    queryset = Assistance.objects.filter(date_joined=date_str.strip())
    if exclude_date is not None:
        queryset = queryset.exclude(date_joined=exclude_date)
    return not queryset.exists()
