from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.erp.forms import CandidateForm
from core.erp.mixins import *
from core.erp.models import *


# Create your views here.

class CandidateListView(LoginRequiredMixin,ValidatePermissionRequiredMixin,ListView):
    model = Candidatos
    template_name = 'candidatos/list.html'
    permission_required = 'view_candidatos'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Candidatos.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listados de Personas'
        context['create_url'] = reverse_lazy('erp:candidatos_create')
        context['list_url'] = reverse_lazy('erp:candidatos_list')
        context['entity'] = 'Personas'
        return context


class CandidateCreateView(LoginRequiredMixin,ValidatePermissionRequiredMixin,CreateView):
    model = Candidatos
    form_class = CandidateForm
    template_name = 'candidatos/create.html'
    success_url = reverse_lazy('erp:candidatos_list')
    permission_required = 'add_candidatos'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de una Persona'
        context['entity'] = 'Candidatos'
        context['list_url'] = reverse_lazy('erp:candidatos_list')
        context['action'] = 'add'
        context['create_url'] = reverse_lazy('erp:candidatos_create')
        return context


class CandidateUpdateView(LoginRequiredMixin,ValidatePermissionRequiredMixin,UpdateView):
    model = Candidatos
    form_class = CandidateForm
    template_name = 'candidatos/create.html'
    success_url = reverse_lazy('erp:candidatos_list')
    permission_required = 'change_candidatos'
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
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de una Persona'
        context['entity'] = 'Candidatos'
        context['list_url'] = reverse_lazy('erp:candidatos_list')
        context['action'] = 'edit'
        context['create_url'] = reverse_lazy('erp:candidatos_create')
        return context


class CandidateDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin,DeleteView):
    model = Candidatos
    form_class = CandidateForm
    template_name = 'candidatos/delete.html'
    success_url = reverse_lazy('erp:candidatos_list')
    permission_required = 'delete_candidatos'

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
        context['title'] = 'Eliminacion de  una Personas'
        context['entity'] = 'Candidatos'
        context['list_url'] = reverse_lazy('erp:candidatos_list')
        context['create_url'] = reverse_lazy('erp:candidatos_create')
        return context
