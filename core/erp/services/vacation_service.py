import datetime
import logging

from django.utils import timezone

from core.erp.models import Vacations
from core.erp.services.email_service import send_vacation_finished_email, send_vacation_reminder_email

logger = logging.getLogger(__name__)


def process_vacation_transitions():
    today = timezone.now().date()
    tomorrow = today + datetime.timedelta(days=1)

    vacations_to_remind = Vacations.objects.filter(end_date=tomorrow, state_vacations='Acceptada')
    for vacation in vacations_to_remind:
        if not vacation.reminder_sent:
            send_vacation_reminder_email(vacation)
            vacation.reminder_sent = True
            vacation.save()

    vacations_to_complete = Vacations.objects.filter(end_date=today)
    for vacation in vacations_to_complete:
        if vacation.state_vacations != 'Finalizada':
            vacation.state_vacations = 'Finalizada'
            vacation.save()
            send_vacation_finished_email(vacation)
        employee = vacation.empleado
        if vacation.end_date == today:
            employee.estado = 'Contratado'
            employee.save()
