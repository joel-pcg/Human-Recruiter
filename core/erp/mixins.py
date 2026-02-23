from django.contrib.auth.models import Group
from django.shortcuts import redirect
from datetime import datetime
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from crum import get_current_request


class IsSuperuserMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return redirect('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_now'] = datetime.now()
        return context

class ValidatePermissionRequiredMixin(object):
    permission_required = ''
    url_redirect = None
    def get_perms(self):
        perms = []
        if isinstance(self.permission_required, str):
            perms.append(self.permission_required, )
        else:
            perms = list(self.permission_required)
        return perms

    def get_url_redirect(self):
        if self.url_redirect is None:
            return reverse_lazy('dashboard')
        return  self.url_redirect
    def dispatch(self, request, *args, **kwargs):
        request = get_current_request()
        if 'group'  in request.session:
            group = request.session['group']
            # group = Group.objects.get(pk=1)
            if group.permissions.filter(codename=self.permission_required).exists():
                return super().dispatch(request, *args, **kwargs)
        messages.error(request,'No tienes permiso para ingresar a este modulo')
        return redirect(self.get_url_redirect())
