import json
from decimal import Decimal
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from core.erp.forms import *
from core.erp.models import *
from core.erp.mixins import *
from django.core.paginator import Paginator


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)


class SelectListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, TemplateView):
    model = Selection
    template_name = 'seleccionados/list.html'
    permission_required = 'view_selection'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                selection = (
                    Selection.objects.all()
                    .order_by('id')
                    .select_related('person', 'vacants__posicion')
                )
                search_value = request.POST.get('search[value]', '')

                if search_value:
                    selection = selection.filter(
                        Q(person__firstname__icontains=search_value) |
                        Q(person__phone__icontains=search_value) |
                        Q(vacants__posicion__name__icontains=search_value) |
                        Q(vacants__max_salary__icontains=search_value) |
                        Q(vacants__min_salary__icontains=search_value)
                    )

                paginator = Paginator(selection, request.POST.get('length', 10))
                page_number = int(request.POST.get('start', 0)) // int(request.POST.get('length', 10)) + 1
                page = paginator.get_page(page_number)

                data = {
                    'data': [
                        {
                            'id': selection.id,
                            'fullname': selection.get_full_name(),
                            'person__phone': selection.person.phone,
                            'vacants__posicion__name': selection.vacants.posicion.name,
                            'vacants__max_salary': selection.vacants.max_salary,
                            'vacants__min_salary': selection.vacants.min_salary,
                        }
                        for selection in page
                    ],
                    'recordsTotal': selection.count(),
                    'recordsFiltered': paginator.count,
                }

            elif action == 'delete':
                apply = Selection.objects.get(pk=request.POST['id'])
                apply.delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Lista de Candidato'
        context['entity'] = 'Candidato'
        context['list_url'] = reverse_lazy('erp:select_list')
        context['create_url'] = reverse_lazy('erp:select_create')
        context['form'] = SelectionForm()
        return context


class SelectCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Selection
    form_class = SelectionForm
    template_name = 'seleccionados/create.html'
    permission_required = 'add_selection'

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({'success': True, 'redirect_url': self.get_success_url()})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors})

    def get_success_url(self):
        return reverse_lazy('erp:select_list')

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        form = self.get_form()
        if  action =='add':
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Candidato'
        context['entity'] = 'Candidatos'
        context['action'] = 'add'
        context['list_url'] = reverse_lazy('erp:select_list')
        return context


class SelectUpdateView(UpdateView):
    model = Selection
    form_class = SelectionForm
    template_name = 'seleccionados/create.html'
    success_url = reverse_lazy('erp:select_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                data = []
                form = self.get_form()
                data = form.save()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edita a un Candidato'
        context['entity'] = 'Candidato'
        context['action'] = 'edit'
        context['list_url'] = reverse_lazy('erp:select_list')
        context['create_url'] = reverse_lazy('erp:select_create')
        return context


class SelectDeleteView(DeleteView):
    model = Selection
    template_name = 'seleccionados/delete.html'

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
        context['title'] = 'Elimina a un Candidato'
        context['entity'] = 'Candidato'
        context['list_url'] = reverse_lazy('erp:select_list')
        return context
