import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from core.erp.forms import CompanyForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Company

logger = logging.getLogger(__name__)


class CompanyUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    form_class = CompanyForm
    template_name = 'company/create.html'
    success_url = reverse_lazy('dashboard')
    permission_required = 'view_company'

    def get_object(self, queryset=None):
        company = Company.objects.all()
        if company.exists():
            return company[0]
        return Company()


    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
               instance = self.get_object()
               if instance.pk is not None:
                   form = CompanyForm(request.POST, request.FILES, instance=instance)
                   data = form.save()
               else:
                   form = CompanyForm(request.POST, request.FILES)
                   data = form.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Compañia'
        context['entity'] = 'Compañia'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['company'] = Company.objects.first()
        return context
