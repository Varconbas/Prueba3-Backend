from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import HORARIOS, Categoria, Cita, Producto, Servicio

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

class ProductoForm(forms.ModelForm):
    precio = forms.IntegerField(
        min_value=1, label='Precio (CLP)',
        help_text='En pesos chilenos, sin puntos ni signo $.',
    )
    nueva_categoria = forms.CharField(
        max_length=50, required=False, label='…o crea una categoría nueva',
        help_text='Déjalo vacío si elegiste una categoría de la lista.',
    )

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'imagen', 'precio', 'stock', 'categoria']
        labels = {
            'descripcion': 'Descripción',
            'imagen': 'Imagen',
            'stock': 'Stock (unidades)',
            'categoria': 'Categoría',
        }
        help_texts = {'imagen': 'JPG o PNG, máximo 2 MB. Es opcional.'}
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if Producto.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe un producto con ese nombre.')
        return nombre

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen and imagen.size > 2 * 1024 * 1024:
            raise forms.ValidationError('La imagen pesa más de 2 MB.')
        return imagen

    def save(self, commit=True):
        producto = super().save(commit=False)
        nueva = self.cleaned_data.get('nueva_categoria', '').strip()
        if nueva:
            # Reutiliza la categoría si ya existe (sin distinguir mayúsculas).
            categoria, _ = Categoria.objects.get_or_create(
                nombre__iexact=nueva, defaults={'nombre': nueva},
            )
            producto.categoria = categoria
        if commit:
            producto.save()
        return producto


class ServicioForm(forms.ModelForm):
    precio = forms.IntegerField(
        min_value=1, label='Precio total (CLP)',
        help_text='El abono se calcula automáticamente (30%).',
    )
    duracion_minutos = forms.IntegerField(min_value=5, initial=60, label='Duración (minutos)')

    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'duracion_minutos', 'productos_recomendados']
        labels = {
            'descripcion': 'Descripción',
            'productos_recomendados': 'Productos recomendados (opcional)',
        }
        help_texts = {
            'productos_recomendados': 'Se le sugieren al cliente cuando reserva este servicio.',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'productos_recomendados': forms.CheckboxSelectMultiple,
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if Servicio.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe un servicio con ese nombre.')
        return nombre