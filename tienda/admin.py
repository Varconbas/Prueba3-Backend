from django.contrib import admin

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
    list_display = ('nombre', 'categoria', 'precio', 'stock')
    list_editable = ('precio', 'stock')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'descripcion')


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_minutos')
    search_fields = ('nombre', 'descripcion')
    # M2M con muchos productos: selector de dos cuadros en vez de Ctrl+clic.
    filter_horizontal = ('productos_recomendados',)


@admin.action(description='Marcar citas seleccionadas como confirmadas')
def confirmar_citas(modeladmin, request, queryset):
    queryset.update(estado=Cita.CONFIRMADA)


@admin.action(description='Cancelar citas seleccionadas (libera la hora)')
def cancelar_citas(modeladmin, request, queryset):
    queryset.update(estado=Cita.CANCELADA)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    # Es la "Agenda de Citas" del panel original.
    list_display = ('fecha', 'hora', 'cliente_nombre', 'usuario', 'servicio', 'abono', 'abono_pagado', 'estado')    
    list_filter = ('estado', 'servicio', 'fecha')
    search_fields = ('cliente_nombre',)
    date_hierarchy = 'fecha'
    actions = [confirmar_citas, cancelar_citas]


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
