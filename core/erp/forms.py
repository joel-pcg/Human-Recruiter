from django.forms import *
from core.erp.models import *


class CompanyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs["class"] = 'form-control'
            form.field.widget.attrs["autocomplete"] = 'off'
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Company
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'description': 'Descripción'
        }
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Ingrese un nombre', }),
            'rnc': TextInput(attrs={'placeholder': 'Ingrese su RNC', }),
            'address': TextInput(attrs={'placeholder': 'Ingrese su Dirección', }),
            'mobile': TextInput(attrs={'placeholder': 'Ingrese su telefono movil', }),
            'phone': TextInput(attrs={'placeholder': 'Ingrese su telefono convencional', }),
            'email': EmailInput(attrs={'placeholder': 'Ingrese su correo empresarial', }),
            'description': Textarea(attrs={'placeholder': 'Ingrese una descripcion', 'rows': 3, 'cols': 3}),
        }
        exclude = ['reminder_sent']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class DepartmentsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs["class"] = 'form-control'
            form.field.widget.attrs["autocomplete"] = 'off'
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Departments
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'description': 'Descripción'
        }
        widgets = {
            'name': TextInput(
                attrs={
                    # 'class': 'form-control',
                    'placeholder': 'Ingrese un nombre',
                    # 'autocomplete': 'off'
                }
            ),
            'description': Textarea(
                attrs={
                    # 'class': 'form-control',
                    'placeholder': 'Ingrese una descripción',
                    # 'autocomplete': 'off',
                    'rows': 3,
                    'cols': 3
                }
            ),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class PositionsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs["class"] = 'form-control'
            form.field.widget.attrs["autocomplete"] = 'off'
        self.fields['name'].widget.attrs['autofocus'] = True
        self.fields['departament'].widget.attrs['class'] = 'form-control select2'

    class Meta:
        model = EmployeePositions
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'description': Textarea(
                attrs={
                    'rows': 3,
                    'cols': 3,
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'departament': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            )
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class EmployeeTurnForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            # form.field.widget.attrs["class"] = 'form-control'
            form.field.widget.attrs["autocomplete"] = 'off'
        self.fields['name'].widget.attrs['autofocus'] = True

    # Forma 2
    #     self.fields['start_turn'].widget.attrs{
    #         'class': 'form-control'
    #     }

    class Meta:
        model = EmployeeTurn
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': 'Nombre de Turno',
                    'autocomplete': 'off',
                    'class': 'form-control'
                }
            ),

            'start_turn': TimeInput(
                format='%I:%M %p',
                attrs={
                    'autocomplete': 'off',
                    'class': 'form-control input-group timepicker-input',
                    'id': 'start_turn',
                    'data-target': '#start_turn',
                    'data-toggle': 'datetimepicker'
                }
            ),
            'end_turn': TimeInput(
                format='%I:%M %p',
                attrs={
                    'autocomplete': 'off',
                    'class': 'form-control input-group timepicker-input',
                    'id': 'end_turn',
                    'data-target': '#end_turn',
                    'data-toggle': 'datetimepicker'
                }
            )

        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class CandidateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs["class"] = 'form-control '
            form.field.widget.attrs["autocomplete"] = 'off'
        self.fields['firstname'].widget.attrs['autofocus'] = True

    class Meta:
        model = Candidatos
        fields = '__all__'
        widgets = {
            'firstname': TextInput(
                attrs={
                    'placeholder': 'Escriba su nombre',
                }
            ),

            'cedula': TextInput(
                attrs={
                    'placeholder': 'Escriba su cedula'
                }
            ),
            'lastname': TextInput(
                attrs={
                    'placeholder': 'Escriba su apellido',
                }
            ),
            'birthdate': DateInput(
                format='%Y-%m-%d',
                attrs={
                    # 'class': 'form-control',
                    # 'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'autocomplete': 'off',
                    'class': ' input-group timepicker-input',
                    'id': 'birthdate',
                    'data-target': '#birthdate',
                    'data-toggle': 'datetimepicker'

                }
            ),
            'gender': Select(
                attrs={
                    'class': 'select2',
                    'style': 'width: 100%'
                }
            ),
            'phone': TextInput(
                attrs={
                    'placeholder': 'Escriba su número telefonico'
                }
            ),
            'email': EmailInput(
                attrs={
                    'placeholder': 'Escriba su email'
                }
            ),
            'address': TextInput(
                attrs={
                    'placeholder': 'Escriba su direccion'
                }
            )
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class VacantsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs["class"] = 'form-control '
            form.field.widget.attrs["autocomplete"] = 'off'
        self.fields['posicion'].widget.attrs['class'] = 'form-control select2'

    class Meta:
        model = Vacants
        fields = '__all__'
        widgets = {

            'description': Textarea(
                attrs={
                    'placeholder': 'Informe de la vacante',
                    'rows': 3,
                    'cols': 3
                }
            ),
            'min_salary': NumberInput(
                attrs={
                    'default': 0.00
                }
            ),
            'max_salary': NumberInput(
                attrs={
                    'default': 0.00
                }
            ),
            'posicion': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            ),

        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class SelectionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['person'].widget.attrs['class'] = 'form-control select2'
        self.fields['vacants'].widget.attrs['class'] = 'form-control select2'

    class Meta:
        model = Selection
        fields = '__all__'
        widgets = {
            'person': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            ),
            'vacants': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            )
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class EmployeForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['person'].widget.attrs['class'] = ' form-control select2 '
        self.fields['person'].widget.attrs['style'] = 'width: 100%'
        # self.fields['person'].widget.attrs['autofocus'] = True

    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'codigo': TextInput(
                attrs={
                    'class': 'form-control ',
                    'placeholder': 'Ingrese el codigo empleado'
                }
            ),
            'person': Select(
                attrs={
                    'class': 'form-control  select2',
                    'style': 'width: 100%'
                }
            ),

            'position': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            ),
            'department': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            ),
            'turn': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            ),
            'estado': Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            ),
            'salary': NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors

        except Exception as e:
            data['error'] = str(e)
        return data


class AssistanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Assistance
        fields = '__all__'
        widgets = {
            'employee': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'date_joined': DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
        }

    date_range = CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }), label='Buscar por rango de fechas')


class DescuentoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True
        self.fields['state'].widget.attrs['class'] = 'form-control form-control-checkbox'
        self.fields['has_quantity'].widget.attrs['class'] = 'form-control form-control-checkbox'

    class Meta:
        model = Headings
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un nombre'}),
            'code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un código de referencia'}),
            'order': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una posición'}),
            'type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
        }
        exclude = ['code']

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class SalaryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Salary
        fields = '__all__'
        widgets = {
            'year': TextInput(attrs={
                'class': 'form-control datetimepicker-input',
                'data-toggle': 'datetimepicker',
                'data-target': '#year',
                'value': datetime.datetime.now().year
            }),
            'month': Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;'
            }),
        }

    year_month = CharField(widget=TextInput(
        attrs={
            'autocomplete': 'off',
            'placeholder': 'MM / AA',
            'class': 'form-control datetimepicker-input',
            'id': 'year_month',
            'data-toggle': 'datetimepicker',
            'data-target': '#year_month',
        }
    ), label='Año/Mes')
    employee = ChoiceField(widget=SelectMultiple(attrs={
        'class': 'form-control select2',
        'multiple': 'multiple',
        'style': 'width: 100%;'
    }), label='Empleado')

class ReportForm(forms.Form):
    date_range = CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }), label='Buscar por rango de fechas')

class VacationsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs["class"] = 'form-control '
            form.field.widget.attrs["autocomplete"] = 'off'
        self.fields['empleado'].widget.attrs['class'] = ' form-control select2 '
        self.fields['state_vacations'].widget.attrs['class'] = ' form-control select2 '
        self.fields['empleado'].queryset = Employee.objects.filter(estado__in=['Contratado','Vacaciones'])

    class Meta:
        model = Vacations
        fields = '__all__'
        widgets = {
            'empleado': Select(
                attrs={

                    'style': 'width: 100%'
                }
            ),
            'start_date': TimeInput(
                format='%Y-%m-%d',
                attrs={
                    'autocomplete': 'off',
                    'class': 'input-group timepicker-input',
                    'id': 'start_date',
                    'data-target': '#start_date',
                    'data-toggle': 'datetimepicker'
                }
            ),
            'end_date': TimeInput(
                format='%Y-%m-%d',
                attrs={
                    'autocomplete': 'off',
                    'class': 'input-group timepicker-input',
                    'id': 'end_date',
                    'data-target': '#end_date',
                    'data-toggle': 'datetimepicker'
                }
            ),
            'motivo':TextInput(
                 attrs={
                     'placeholder': 'Motivo de vacaciones',
                 }
            ),
            'observaciones': Textarea(
                attrs={
                    'placeholder': 'Observaciones extras',
                    'rows': 3,
                    'cols': 3

                }
            ),
            'state_vacations':Select(
                attrs={
                    'class':'form-control select2',
                     'style': 'width: 100%'

                }
            )
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data



class ApplicationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        selected_vacant_id = kwargs.pop('selected_vacant_id', None)
        super().__init__(*args, **kwargs)

        if selected_vacant_id is not None:
            self.fields['selected_vacant_id'] = IntegerField(widget=HiddenInput(), initial=int(selected_vacant_id))

        for form in self.visible_fields():
            form.field.widget.attrs["class"] = 'form-control'
            form.field.widget.attrs["autocomplete"] = 'off'

        self.fields['firstname'].widget.attrs['autofocus'] = True
    class Meta:
        model = Candidatos
        fields = ['cedula', 'firstname', 'lastname', 'birthdate', 'gender', 'phone', 'email', 'address']
        widgets = {
            'firstname': TextInput(
                attrs={
                    'placeholder': 'Escriba su nombre',
                }
            ),

            'cedula': TextInput(
                attrs={
                    'placeholder': 'Escriba su cedula'
                }
            ),
            'lastname': TextInput(
                attrs={
                    'placeholder': 'Escriba su apellido',
                }
            ),
            'birthdate': DateInput(
                format='%Y-%m-%d',
                attrs={
                    # 'class': 'form-control',
                    # 'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'autocomplete': 'off',
                    'class': ' input-group timepicker-input',
                    'id': 'birthdate',
                    'data-target': '#birthdate',
                    'data-toggle': 'datetimepicker'

                }
            ),
            'gender': Select(
                attrs={
                    'class': 'select2',
                    'style': 'width: 100%'
                }
            ),
            'phone': TextInput(
                attrs={
                    'placeholder': 'Escriba su número telefonico'
                }
            ),
            'email': EmailInput(
                attrs={
                    'placeholder': 'Escriba su email'
                }
            ),
            'address': TextInput(
                attrs={
                    'placeholder': 'Escriba su direccion'
                }
            )
        }



    def save(self, commit=True):
        instance = super().save(commit=False)
        vacante_id = self.cleaned_data['selected_vacant_id']
        instance.vacante = Vacants.objects.get(pk=vacante_id)
        if commit:
            instance.save()
            Selection.objects.create(person=instance, vacants=instance.vacante)
        return instance