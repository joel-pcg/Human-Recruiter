from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import *
from core.security.models import *
from core.erp.forms import *
from core.erp.mixins import *


# Create your views here.

class AccessUsersListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, FormView):
    form_class = ReportForm
    template_name = 'access_users/list.html'
    permission_required = 'view_user_access'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search':
                data = []
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                queryset = AccessUser.objects.all()
                if len(start_date) and len(end_date):
                    queryset = queryset.filter(date_joined__range=[start_date, end_date])
                for i in queryset:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listados de Acceso de Usuario'
        context['list_url'] = reverse_lazy('acceso_usuario_list')
        context['entity'] = 'Acceso de Usuario'
        return context


class AccessUsersDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = AccessUser
    template_name = 'delete.html'
    permission_required = 'delete_user_access'
    success_url = reverse_lazy('acceso_usuario_list')

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Alerta de eliminación'
        context['list_url'] = self.success_url
        context['entity'] = 'Acceso de Usuario'
        return context
