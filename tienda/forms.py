from datetime import datetime

from django import forms

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
