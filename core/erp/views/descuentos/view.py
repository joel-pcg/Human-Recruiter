import json
from decimal import Decimal
from datetime import date
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from core.erp.encoders import CustomJSONEncoder
from core.erp.mixins import *
from core.erp.forms import *
from django.contrib.auth.mixins import LoginRequiredMixin


class DescuentosListView(LoginRequiredMixin,ValidatePermissionRequiredMixin,TemplateView):
    template_name = 'descuentos/list.html'
    permission_required = 'view_headings'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                for i in Headings.objects.all().order_by('type', 'order'):
                    data.append(i.toJSON())
            else:
                data['error'] = 'No se ha seleccionado ninguna opcion'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super(DescuentosListView, self).get_context_data()
        context['title'] = 'Listado de items de descuentos'
        context['entity'] = 'Items'
        context['create_url'] = reverse_lazy('erp:descuento_create')
        return context


class DescuentosCreateView(LoginRequiredMixin,CreateView):
    model = Headings
    form_class = DescuentoForm
    template_name = 'descuentos/create.html'
    success_url = reverse_lazy('erp:descuento_list')
    permission_required = 'add_headings'
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                data = self.get_form().save()
            elif action == 'validate_data':
                data = {'valid': True}
                queryset = Headings.objects.all()
                pattern = request.POST['pattern']
                parameter = request.POST['parameter'].strip()
                if pattern == 'name':
                    data['valid'] = not queryset.filter(name__iexact=parameter).exists()
                elif pattern == 'code':
                    data['valid'] = not queryset.filter(code__iexact=parameter).exists()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super(DescuentosCreateView, self).get_context_data()
        context['entity'] = 'Items'
        context['title'] = 'Registro de un nuevo Items'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context


class DescuentosUpdateView(LoginRequiredMixin,UpdateView):
    model = Headings
    form_class = DescuentoForm
    template_name = 'descuentos/create.html'
    success_url = reverse_lazy('erp:descuento_list')
    permission_required = 'change_headings'
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                data = self.get_form().save()
            elif action == 'validate_data':
                data = {'valid': True}
                queryset = Headings.objects.all().include(id=self.object.id)
                pattern = request.POST['pattern']
                parameter = request.POST['parameter'].strip()
                if pattern == 'name':
                    data['valid'] = not queryset.filter(name__iexact=parameter).exists()
                elif pattern == 'code':
                    data['valid'] = not queryset.filter(code__iexact=parameter).exists()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super(DescuentosUpdateView, self).get_context_data()
        context['entity'] = 'Items'
        context['title'] = 'Edición de un Items'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context


class DescuentoDeleteView(LoginRequiredMixin,DeleteView):
    model = Headings
    template_name = 'delete.html'
    success_url = reverse_lazy('erp:descuento_list')
    permission_required = 'delete_headings'
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        serialized_data = json.dumps(data, cls=CustomJSONEncoder)
        return HttpResponse(serialized_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
