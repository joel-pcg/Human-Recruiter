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

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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

# class DepartamentCreateView(CreateView):
#     model = Departments
#     form_class = DepartmentsForm
#     template_name = 'departaments/create.html'
#     success_url = reverse_lazy('erp:departaments_list')
#
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'add':
#                 form = self.get_form()
#                 data = form.save()
#
#             else:
#                 data['error'] = 'No ha ingresado a ninguna opción'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data)
#
#     # def post(self, request, *args, **kwargs):
#     #     print(request.POST)
#     #     form = DepartmentsForm(request.POST)
#     #     if form.is_valid():
#     #         form.save()
#     #         return HttpResponseRedirect(self.success_url)
#     #     self.object = None
#     #     context = self.get_context_data(**kwargs)
#     #     context['form'] = form
#     #     return render(request, self.template_name, context)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Crea un Departamento'
#         context['create_url'] = reverse_lazy('erp:departaments_create')
#         context['list_url'] = reverse_lazy('erp:departaments_list')
#         context['entity'] = 'Departamentos'
#         context['action'] = 'add'
#         return context
#
#
# class DepartamentUpdateView(UpdateView):
#     model = Departments
#     form_class = DepartmentsForm
#     template_name = 'departaments/create.html'
#     success_url = reverse_lazy('erp:departaments_list')
#
#     def dispatch(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'edit':
#                 form = self.get_form()
#                 data = form.save()
#
#             else:
#                 data['error'] = 'No ha ingresado a ninguna opción'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Edicion de un Departamento'
#         context['create_url'] = reverse_lazy('erp:departaments_create')
#         context['list_url'] = reverse_lazy('erp:departaments_list')
#         context['entity'] = 'Departamentos'
#         context['action'] = 'edit'
#         return context
#
#
# class DepartamentDeleteView(DeleteView):
#     model = Departments
#     template_name = 'departaments/delete.html'
#     success_url = reverse_lazy('erp:departaments_list')
#
#     def dispatch(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             self.object.delete()
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Eliminación de un Departamento'
#         context['entity'] = 'Departamentos'
#         context['list_url'] = self.success_url
#         return context
