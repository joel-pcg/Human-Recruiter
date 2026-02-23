import datetime
import json
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from core.erp.models import *
from django.utils import timezone
from core.erp.views.Vacations.views import send_email_vacation_finished, send_reminder_vacation_ending

logger = logging.getLogger(__name__)

# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            today = timezone.now().date()
            tomorrow = today + datetime.timedelta(days=1)
            vacations_to_complete = Vacations.objects.filter(end_date=today)
            vacations_to_remind = Vacations.objects.filter(end_date=tomorrow, state_vacations='Acceptada')
            for vacations in vacations_to_remind:
                if  not vacations.reminder_sent:
                    send_reminder_vacation_ending(vacations)
                    vacations.reminder_sent = True
                    vacations.save()
            for vacations in vacations_to_complete:
                if vacations.state_vacations != 'Finalizada':
                    vacations.state_vacations = 'Finalizada'
                    vacations.save()
                    send_email_vacation_finished(vacations)
                employee = vacations.empleado
                if vacations.end_date == today:
                    employee.estado = 'Contratado'
                    employee.save()
                
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        request.user.get_group_session()
        # 
        # print('se envio')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'get_graph_salaries_by_year':
                data = []
                year = datetime.datetime.now().year
                for month in range(1, 13):
                    result = SalaryDetail.objects.filter(salary__month=month, salary__year=year).aggregate(
                        result=Coalesce(Sum('total_amount'), 0.00, output_field=FloatField())).get('result')
                    data.append(float(result))
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            logger.error("Error in DashboardView: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Panel de administración'
        context['salaries'] = SalaryDetail.objects.filter().order_by('-id')[0:10]
        context['year'] = datetime.datetime.now().year
        context['month'] = MONTHS[datetime.datetime.now().month][1]
        context['asistance'] = AssistanceDetail.objects.filter().order_by('-id')[0:10]
        context['positions'] = EmployeePositions.objects.all().count()
        context['areas'] = Departments.objects.all().count()
        context['headings'] = Headings.objects.all().count()
        context['employees'] = Employee.objects.all().count()
        return context
