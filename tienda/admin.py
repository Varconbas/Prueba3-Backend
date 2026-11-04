from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Categoria, Cita, ItemPedido, Pedido, Producto, Servicio

admin.site.site_header = 'RG Beauty SPA · Administración'
admin.site.site_title = 'RG Beauty SPA'
admin.site.index_title = 'Gestión interna'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Inventario de la tienda: precio y stock se editan directo en el listado.
    list_display = ('miniatura', 'nombre', 'categoria', 'precio', 'stock')
    list_display_links = ('nombre',)
    list_editable = ('precio', 'stock')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('miniatura',)

    @admin.display(description='Imagen')
    def miniatura(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="height:48px; border-radius:6px;">', obj.imagen.url,
            )
        return '—'

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_minutos')
    search_fields = ('nombre', 'descripcion')
    # M2M con muchos productos: selector de dos cuadros en vez de Ctrl+clic.
    filter_horizontal = ('productos_recomendados',)


@admin.action(description='Aceptar solicitudes en espera (sin mensaje)')
def aceptar_citas(modeladmin, request, queryset):
    pendientes = list(queryset.filter(estado=Cita.PENDIENTE))
    for cita in pendientes:
        cita.aceptar()
    modeladmin.message_user(request, f'{len(pendientes)} solicitud(es) aceptada(s).')


@admin.action(description='Rechazar solicitudes en espera (sin motivo)')
def rechazar_citas(modeladmin, request, queryset):
    pendientes = list(queryset.filter(estado=Cita.PENDIENTE))
    for cita in pendientes:
        cita.rechazar()
    modeladmin.message_user(request, f'{len(pendientes)} solicitud(es) rechazada(s).')


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    # Bandeja de solicitudes: filtra por "En espera" para ver las que faltan por responder.
    list_display = ('fecha', 'hora', 'cliente_nombre', 'usuario', 'servicio',
                    'abono', 'abono_pagado', 'estado')
    list_filter = ('estado', 'servicio', 'fecha')
    search_fields = ('cliente_nombre', 'usuario__username')
    date_hierarchy = 'fecha'
    actions = [aceptar_citas, rechazar_citas]
    readonly_fields = ('creada', 'respondida_el', 'motivo_cancelacion')
    fieldsets = (
        ('Solicitud', {'fields': ('cliente_nombre', 'usuario', 'servicio', 'fecha', 'hora')}),
        ('Abono (simulado)', {'fields': ('abono', 'abono_pagado')}),
        ('Respuesta del salón', {
            'fields': ('estado', 'respuesta_admin'),
            'description': 'Para aceptar o rechazar con mensaje: cambia el estado, '
                           'escribe el mensaje (opcional) y guarda.',
        }),
        ('Cancelación del cliente', {'fields': ('motivo_cancelacion',)}),
        ('Registro', {'fields': ('creada', 'respondida_el')}),
    )

    def save_model(self, request, obj, form, change):
        # Al responder desde el formulario, deja registrado cuándo y marca el abono.
        if change and 'estado' in form.changed_data:
            if obj.estado == Cita.CONFIRMADA:
                obj.abono_pagado = True
            if obj.estado in (Cita.CONFIRMADA, Cita.RECHAZADA):
                obj.respondida_el = timezone.now()
        super().save_model(request, obj, form, change)

class ItemPedidoInline(admin.TabularInline):
    # Se gestiona el "lado muchos" (items) desde el "lado uno" (pedido).
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'usuario', 'creado', 'total', 'pagado')    
    list_filter = ('pagado', 'creado')
    search_fields = ('cliente_nombre',)
    readonly_fields = ('creado',)
    inlines = [ItemPedidoInline]
