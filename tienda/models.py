from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Horarios fijos de atención (los mismos botones del index.html original).
HORARIOS = ['10:00', '11:30', '13:00', '15:00', '16:30', '18:00']
PORCENTAJE_ABONO = 30


# ---------------------------------------------------------------- Tienda ----
class Categoria(models.Model):
    """Agrupa los productos de la tienda (relación 1:N con Producto)."""
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    imagen_url = models.URLField(blank=True)
    precio = models.PositiveIntegerField(help_text='Precio en pesos chilenos.')
    stock = models.PositiveIntegerField(default=0)
    # SET_NULL: si se borra una categoría, los productos NO se borran.
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL,
        related_name='productos', null=True, blank=True,
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# -------------------------------------------------------------- Servicios ---
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.PositiveIntegerField(help_text='Precio total en pesos chilenos.')
    duracion_minutos = models.PositiveIntegerField(default=60)
    # N:M — un servicio recomienda varios productos y un producto se recomienda
    # en varios servicios ("continúa tu tratamiento en casa").
    productos_recomendados = models.ManyToManyField(
        Producto, related_name='servicios', blank=True,
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def abono(self):
        """30% del precio (el pago real se simula)."""
        return round(self.precio * PORCENTAJE_ABONO / 100)


class Cita(models.Model):
    PENDIENTE = 'PENDIENTE'
    CONFIRMADA = 'CONFIRMADA'
    CANCELADA = 'CANCELADA'
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (CONFIRMADA, 'Confirmada'),
        (CANCELADA, 'Cancelada'),
    ]

    cliente_nombre = models.CharField(max_length=100)
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name='citas')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='citas', null=True, blank=True,
    )    
    fecha = models.DateField()
    hora = models.TimeField()
    abono = models.PositiveIntegerField(default=0)
    abono_pagado = models.BooleanField(default=False)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=PENDIENTE)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f'{self.cliente_nombre} · {self.servicio} · {self.fecha:%d-%m-%Y} {self.hora:%H:%M}'

    def clean(self):
        """Validaciones que aplican tanto al formulario público como al Admin."""
        if not (self.fecha and self.hora):
            return
        if self._state.adding and self.fecha < timezone.localdate():
            raise ValidationError({'fecha': 'No puedes agendar en una fecha pasada.'})
        if self.estado != self.CANCELADA:
            ocupada = (
                Cita.objects.filter(fecha=self.fecha, hora=self.hora)
                .exclude(estado=self.CANCELADA)
                .exclude(pk=self.pk)
            )
            if ocupada.exists():
                raise ValidationError('Esa hora ya está reservada. Elige otro horario.')


# ---------------------------------------------------------------- Pedidos ---
class Pedido(models.Model):
    cliente_nombre = models.CharField(max_length=100)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='pedidos', null=True, blank=True,
    )
    creado = models.DateTimeField(auto_now_add=True)
    total = models.PositiveIntegerField(default=0)
    pagado = models.BooleanField(default=False)   # pago simulado

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f'Pedido #{self.pk} · {self.cliente_nombre}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='items_pedido')
    cantidad = models.PositiveIntegerField(default=1)
    # Se guarda el precio del momento: si el precio cambia después, el pedido no cambia.
    precio_unitario = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.cantidad} x {self.producto}'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
