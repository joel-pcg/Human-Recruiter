from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.generic import *
from core.erp.mixins import *
from core.erp.forms import *


class TurnJobListView(LoginRequiredMixin,ValidatePermissionRequiredMixin,ListView):
    model = EmployeeTurn
    template_name = 'turnos_trabajo/list.html'
    permission_required = 'view_employeeturn'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in EmployeeTurn.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Turnos'
        context['create_url'] = reverse_lazy('erp:turno_trabajo_create')
        context['list_url'] = reverse_lazy('erp:turno_trabajo_list')
        context['entity'] = 'Horarios'
        return context


class TurnJobCreateView(LoginRequiredMixin,ValidatePermissionRequiredMixin,CreateView):
    model = EmployeeTurn
    form_class = EmployeeTurnForm
    template_name = 'turnos_trabajo/create.html'
    permission_required = 'view_employeeturn'
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
                # print(form)
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creacion de un turno'
        context['entity'] = 'Horarios'
        context['list_url'] = reverse_lazy('erp:turno_trabajo_list')
        context['action'] = 'add'
        return context


class TurnJobUpdateView(LoginRequiredMixin,ValidatePermissionRequiredMixin,UpdateView):
    model = EmployeeTurn
    form_class = EmployeeTurnForm
    template_name = 'turnos_trabajo/create.html'
    permission_required = 'view_employeeturn'
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
                # print(form)
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edita un turno'
        context['entity'] = 'Horarios'
        context['list_url'] = reverse_lazy('erp:turno_trabajo_list')
        context['action'] = 'edit'
        return context


class TurnJobDeleteView(LoginRequiredMixin,ValidatePermissionRequiredMixin,DeleteView):
    model = EmployeeTurn
    template_name = 'turnos_trabajo/delete.html'
    success_url = reverse_lazy("erp:turno_trabajo_list")
    permission_required = 'view_employeeturn'
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminacion de un turno'
        context['entity'] = 'Horarios'
        context['list_url'] = self.success_url
        return context