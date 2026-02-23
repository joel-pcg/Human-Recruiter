from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView
from core.erp.forms import DepartmentsForm
from core.erp.mixins import *
from core.erp.models import *


# Create your views here.

class DepartamentListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, TemplateView):
    model = Departments
    template_name = 'departaments/list.html'
    permission_required = 'view_departments'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Departments.objects.all():
                    data.append(i.toJSON())
            elif action == 'add':
                depart = Departments()
                depart.name = request.POST['name']
                depart.description = request.POST['description']
                depart.save()
            elif action == 'edit':
                depart = Departments.objects.get(pk=request.POST['id'])
                depart.name = request.POST['name']
                depart.description = request.POST['description']
                depart.save()
            elif action == 'delete':
                depart = Departments.objects.get(pk=request.POST['id'])
                depart.delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listados de Departamentos'
        context['form'] = DepartmentsForm()
        context['list_url'] = reverse_lazy('erp:departaments_list')
        context['entity'] = 'Departamentos'
        return context
