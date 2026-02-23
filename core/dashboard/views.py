import datetime
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.views.generic import TemplateView
from core.erp.models import *
from core.erp.services.vacation_service import process_vacation_transitions


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            process_vacation_transitions()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        request.user.get_group_session()
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
            data['error'] = str(e)
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
