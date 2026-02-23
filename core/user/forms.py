import logging

from django.forms import *
from datetime import datetime
from core.user.models import *

logger = logging.getLogger(__name__)


class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['autofocus'] = True
        self.fields['username'].widget.attrs['autocomplete'] = 'off'
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['employee'].queryset = Employee.objects.filter(estado='Contratado')

    class Meta:
        model = User
        fields = 'username', 'password', 'image', 'groups','employee'
        labels = {
            'groups': 'Perfil de usuario'
        }
        queryset = Employee.objects.filter(estado='Contratado'),
        widgets = {
            'username': TextInput(
                attrs={
                    'placeholder': 'Crea un Nombre de Usuario',
                    'class': 'form-control',
                }
            ),

            'password': PasswordInput(
                render_value=True,
                attrs={
                    'placeholder': 'Crea una Contraseña',
                    'class': 'form-control',
                }),

            'employee': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            ),

            'groups': SelectMultiple(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%',
                "multiple": "multiple",

            }),
        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser', 'is_active', 'is_staff']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                password_cleaned = self.cleaned_data['password']
                user_created = form.save(commit=False)
                if user_created.pk is None:
                    user_created.set_password(password_cleaned)
                else:
                    user = User.objects.get(pk=user_created.pk)
                    if user.password != password_cleaned:
                        user_created.set_password(password_cleaned)
                user_created.save()
                user_created.groups.clear()
                for group in self.cleaned_data['groups']:
                    user_created.groups.add(group)
            else:
                data['error'] = form.errors
        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return data


class UserProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs['autofocus'] = True
        self.fields['image'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'email', 'username', 'password', 'image'
        labels = {
            'groups': 'Perfil de usuario'
        }
        widgets = {
            'first_name': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus nombre',
                    'class': 'form-control',
                }
            ),
            'email': TextInput(
                attrs={
                    'placeholder': 'Ingrese su Email',
                    'class': 'form-control',

                }
            ),

            'username': TextInput(
                attrs={
                    'placeholder': 'Crea un Nombre de Usuario',
                    'class': 'form-control',
                }
            ),

        }
        exclude = ['user_permissions', 'password', 'last_name', 'last_login', 'date_joined', 'is_superuser',
                   'is_active', 'is_staff', 'groups']

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            data['error'] = 'Ha ocurrido un error.'
        return data
