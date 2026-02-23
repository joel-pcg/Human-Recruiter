import json
import logging
from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.generic import *

from core.erp.forms import *
from core.erp.mixins import *
from core.erp.models import *

logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)


class VacantsListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Vacants
    template_name = 'vacante/list.html'
    permission_required = 'view_vacants'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                queryset = Vacants.objects.all().order_by('id')
                search_value = request.POST.get('search[value]', '')
                if search_value:
                    queryset = queryset.filter(
                        Q(posicion__name__contains=search_value) |
                        Q(description__contains=search_value) |
                        Q(min_salary__contains=search_value) |
                        Q(max_salary__contains=search_value)
                    ).order_by('id')

                paginator = Paginator(queryset, request.POST.get('length', 10))
                page_number = int(request.POST.get('start', 0)) // int(request.POST.get('length', 10)) + 1
                page = paginator.get_page(page_number)
                data = {
                    'data': [item.toJSON() for item in page],
                    'recordsTotal': queryset.count(),
                    'recordsFiltered': paginator.count,
                }

            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            logger.error("Error in VacantsListView: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url = settings.DOMAIN if not settings.DEBUG else self.request.META['HTTP_HOST']
        form_url = f'http://{url}/erp/vacante/apply/{1}/'
        context['title'] = 'Listados de Vacantes'
        context['create_url'] = reverse_lazy('erp:vacante_create')
        context['list_url'] = reverse_lazy('erp:vacante_list')
        context['entity'] = 'Vacantes'
        return context


class VacantsCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Vacants
    form_class = VacantsForm
    template_name = 'vacante/create.html'
    permission_required = 'add_vacants'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
        except Exception as e:
            logger.error("Error in VacantsCreateView: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crea una Vacantes'
        context['entity'] = 'Vacantes'
        context['action'] = 'add'
        context['list_url'] = reverse_lazy('erp:vacante_list')
        context['create_url'] = reverse_lazy('erp:vacante_create')
        return context


class VacantsUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Vacants
    form_class = VacantsForm
    template_name = 'vacante/create.html'
    permission_required = 'change_vacants'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()

        except Exception as e:
            logger.error("Error in VacantsUpdateView: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edita una Vacantes'
        context['entity'] = 'Vacantes'
        context['action'] = 'edit'
        context['list_url'] = reverse_lazy('erp:vacante_list')
        context['create_url'] = reverse_lazy('erp:vacante_create')
        return context


class VacantsDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Vacants
    template_name = 'vacante/delete.html'
    permission_required = 'delete_vacants'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            logger.error("Error in VacantsDeleteView: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Elimina una Vacante'
        context['entity'] = 'Vacantes'
        context['list_url'] = reverse_lazy('erp:vacante_list')
        context['create_url'] = reverse_lazy('erp:vacante_create')
        return context


class ApplyVacants(CreateView):
    model = Candidatos
    template_name = 'vacante/apply_form.html'
    form_class = ApplicationForm
    success_url = reverse_lazy('erp:page_thanks')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['selected_vacant_id'] = self.kwargs['vacant_id']
        return kwargs

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'apply':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    return  redirect('erp:page_thanks')
                else:
                    logger.warning("Invalid form submission in ApplyVacants: %s", form.errors)
                    data['error'] = 'Formulario no válido.'
        except Exception as e:
            logger.error("Error in ApplyVacants: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'apply'
        context['selected_vacant_id'] = int(self.kwargs['vacant_id'])
        context['list_url'] = self.success_url
        return context


def page_thanks(request):
    return render(request, 'thanks_page.html')
