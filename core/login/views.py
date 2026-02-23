import logging

from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import RedirectView, FormView
import config.settings as setting
from config import settings
from core.user.models import User
from .form import ResetPasswordForm, ChangePasswordForm
from ..security.models import AccessUser

logger = logging.getLogger(__name__)


class LoginHumanRecruiterView(FormView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    success_url = settings.LOGIN_REDIRECT_URL

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, user=form.get_user())
        AccessUser(user=self.request.user).save()
        return super(LoginHumanRecruiterView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar sesión'
        return context


class LogoutHumanRecruiterView(RedirectView):
    pattern_name = 'login'

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)


class LoginResetPasswordView(FormView):
    template_name = 'reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy(setting.LOGIN_REDIRECT_URL)

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def send_email_reset_password(self, user):
        data = {}
        try:
            url = settings.DOMAIN if not setting.DEBUG else self.request.META['HTTP_HOST']
            user.generate_reset_token()
            email_to = user.employee.person.email
            content = render_to_string('login/send_email.html', {
                'user': user,
                'link_resetpwd': f'http://{url}/login/change/password/{str(user.token)}/',
                'link_home': f'http://{url}'
            })
            send_mail(
                subject="Solicitud de cambio de contraseña",
                message='',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email_to],
                html_message=content,
            )
        except Exception as e:
            logger.error("Error sending password reset email: %s", e, exc_info=True)
            data['error'] = 'Error al enviar el correo de recuperación.'
        return data

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                user = form.get_user()
                data = self.send_email_reset_password(user)
            else:
                data['error'] = form.errors
        except Exception as e:
            logger.error("Error in password reset: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error al procesar la solicitud.'
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reseteo de contraseña'
        return context


class ChangePasswordView(FormView):
    template_name = 'change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy(setting.LOGIN_REDIRECT_URL)

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = self.kwargs['token']
        try:
            user = User.objects.get(token=token)
            if not user.is_token_valid():
                return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
        except User.DoesNotExist:
            return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                user = User.objects.get(token=self.kwargs['token'])
                if not user.is_token_valid():
                    data['error'] = 'El enlace de recuperación ha expirado.'
                else:
                    user.set_password(request.POST['password'])
                    user.token = None
                    user.token_created_at = None
                    user.save()
            else:
                data['error'] = form.errors
        except User.DoesNotExist:
            data['error'] = 'Token inválido.'
        except Exception as e:
            logger.error("Error changing password: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error al cambiar la contraseña.'
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cambio de contraseña'
        return context
