import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.generic import *
from core.erp.mixins import *
from core.erp.forms import *

logger = logging.getLogger(__name__)


class PositionsJobListView(LoginRequiredMixin,ValidatePermissionRequiredMixin,ListView):
    model = EmployeePositions
    template_name = 'positions/list.html'
    permission_required = 'view_employeepositions'
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in EmployeePositions.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Posiciones'
        context['entity'] = 'Posiciones'
        context['create_url'] = reverse_lazy('erp:position_create')
        context['list_url'] = reverse_lazy('erp:position_list')
        return context


class PositionsJobCreateView(LoginRequiredMixin,ValidatePermissionRequiredMixin,CreateView):
    model = EmployeePositions
    form_class = PositionsForm
    template_name = 'positions/create.html'
    success_url = reverse_lazy('erp:position_list')
    permission_required = 'add_employeepositions'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crea una Posicion'
        context['list_url'] = self.success_url
        context['entity'] = 'Posicion'
        context['action'] = 'add'
        return context


class PositionsJobUpdateView(LoginRequiredMixin,ValidatePermissionRequiredMixin,UpdateView):
    model = EmployeePositions
    form_class = PositionsForm
    template_name = 'positions/create.html'
    success_url = reverse_lazy('erp:position_list')
    permission_required = 'change_employeepositions'

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
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edita una Posicion'
        context['list_url'] = self.success_url
        context['entity'] = 'Posicion'
        context['action'] = 'edit'
        return context


class PositionsJobDeleteView(LoginRequiredMixin,ValidatePermissionRequiredMixin,DeleteView):
    model = EmployeePositions
    template_name = 'positions/delete.html'
    success_url = reverse_lazy('erp:position_list')
    permission_required = 'delete_employeepositions'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()

        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Posicion'
        context['entity'] = 'Posiciones'
        context['list_url'] = self.success_url
        return context
