from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import HORARIOS, Cita


def _a_hora(texto):
    return datetime.strptime(texto, '%H:%M').time()


class CitaForm(forms.ModelForm):
    # La hora llega como texto ("10:00") y se convierte a time.
    hora = forms.TypedChoiceField(
        choices=[(h, h) for h in HORARIOS], coerce=_a_hora, label='Hora',
    )

    class Meta:
        model = Cita
        fields = ['cliente_nombre', 'servicio', 'fecha', 'hora']
        labels = {'cliente_nombre': 'Tu nombre', 'servicio': 'Servicio a realizar'}
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'placeholder': 'Ej: Camila Rojas'}),
        }


class PagoForm(forms.Form):
    cliente_nombre = forms.CharField(
        max_length=100, label='Nombre del comprador',
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Camila Rojas'}),
    )

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label='Nombre')
    email = forms.EmailField(label='Correo electrónico')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'email')
        labels = {'username': 'Nombre de usuario'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado en otra cuenta.')
        return email

class CancelacionForm(forms.Form):
    motivo = forms.CharField(max_length=300, required=False)

class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label='Nombre')
    email = forms.EmailField(label='Correo electrónico')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {'last_name': 'Apellido'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        # Se excluye al propio usuario: puede guardar su mismo correo sin error.
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo ya pertenece a otra cuenta.')
        return email
