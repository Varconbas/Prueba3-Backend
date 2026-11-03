from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CancelacionForm, CitaForm, PagoForm, RegistroForm

from .forms import CitaForm, PagoForm, RegistroForm
from .models import (
    HORARIOS, PORCENTAJE_ABONO, Categoria, Cita, ItemPedido, Pedido, Producto,
)


class StockInsuficiente(Exception):
    pass

def _nombre_de(usuario):
    """Nombre para prellenar formularios."""
    return usuario.get_full_name() or usuario.username


# ----------------------------------------------------------------- Tienda ---
def inicio(request):
    productos = Producto.objects.select_related('categoria')
    categorias = Categoria.objects.all()
    categoria_id = request.GET.get('categoria')
    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))
    return render(request, 'tienda/tienda.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_activa': int(categoria_id) if categoria_id and categoria_id.isdigit() else None,
    })


# ---------------------------------------------------------------- Carrito ---
# El carrito vive en la sesión: {"<id_producto>": cantidad}
def _detalle_carrito(request):
    carrito = request.session.get('carrito', {})
    productos = Producto.objects.in_bulk([int(pk) for pk in carrito])
    items, total = [], 0
    for pk, cantidad in carrito.items():
        producto = productos.get(int(pk))
        if producto is None:      # el producto fue eliminado
            continue
        subtotal = producto.precio * cantidad
        items.append({'producto': producto, 'cantidad': cantidad, 'subtotal': subtotal})
        total += subtotal
    return items, total


def ver_carrito(request):
    items, total = _detalle_carrito(request)
    if request.user.is_authenticated:
        form = PagoForm(initial={'cliente_nombre': _nombre_de(request.user)})
    else:
        form = PagoForm()
    return render(request, 'tienda/carrito.html', {
        'items': items, 'total': total, 'form': form,
    })


@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    clave = str(producto.pk)
    nueva_cantidad = carrito.get(clave, 0) + 1
    if nueva_cantidad > producto.stock:
        messages.warning(request, f'No hay más stock de «{producto.nombre}».')
    else:
        carrito[clave] = nueva_cantidad
        request.session['carrito'] = carrito
        messages.success(request, f'«{producto.nombre}» agregado al carrito.')
    return redirect('tienda:inicio')


@require_POST
def actualizar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except ValueError:
        cantidad = 1
    if cantidad <= 0:
        carrito.pop(str(producto.pk), None)
    else:
        if cantidad > producto.stock:
            cantidad = producto.stock
            messages.warning(request, f'Solo quedan {producto.stock} unidades de «{producto.nombre}».')
        carrito[str(producto.pk)] = cantidad
    request.session['carrito'] = carrito
    return redirect('tienda:carrito')


@require_POST
def quitar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    request.session['carrito'] = carrito
    return redirect('tienda:carrito')

@login_required
@require_POST
def pagar(request):
    """Pago SIMULADO: crea el pedido, descuenta stock y vacía el carrito."""
    items, total = _detalle_carrito(request)
    if not items:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('tienda:carrito')

    form = PagoForm(request.POST)
    if not form.is_valid():
        return render(request, 'tienda/carrito.html', {'items': items, 'total': total, 'form': form})

    try:
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                cliente_nombre=form.cleaned_data['cliente_nombre'], pagado=True,
            )            
            total_pedido = 0
            for item in items:
                # select_for_update bloquea la fila mientras se descuenta el stock
                producto = Producto.objects.select_for_update().get(pk=item['producto'].pk)
                if item['cantidad'] > producto.stock:
                    raise StockInsuficiente(f'Stock insuficiente de «{producto.nombre}».')
                ItemPedido.objects.create(
                    pedido=pedido, producto=producto,
                    cantidad=item['cantidad'], precio_unitario=producto.precio,
                )
                producto.stock -= item['cantidad']
                producto.save(update_fields=['stock'])
                total_pedido += producto.precio * item['cantidad']
            pedido.total = total_pedido
            pedido.save(update_fields=['total'])
    except StockInsuficiente as error:
        messages.error(request, str(error))
        return redirect('tienda:carrito')

    request.session['carrito'] = {}
    request.session['ultimo_pedido'] = pedido.pk
    return redirect('tienda:pedido_confirmado')


def pedido_confirmado(request):
    pedido_id = request.session.get('ultimo_pedido')
    if not pedido_id:
        return redirect('tienda:inicio')
    pedido = get_object_or_404(Pedido.objects.prefetch_related('items__producto'), pk=pedido_id)
    return render(request, 'tienda/pedido_confirmado.html', {'pedido': pedido})


# ---------------------------------------------------------------- Agenda ----
def _parsear_fecha(texto):
    try:
        fecha = date.fromisoformat(texto or '')
    except ValueError:
        return None
    return fecha if fecha >= timezone.localdate() else None


def _horarios(fecha):
    """Devuelve [(hora, disponible), ...] para la fecha dada."""
    ocupadas = {
        hora.strftime('%H:%M')
        for hora in Cita.objects.filter(fecha=fecha)
        .exclude(estado__in=Cita.ESTADOS_QUE_LIBERAN).values_list('hora', flat=True)    }
    return [(hora, hora not in ocupadas) for hora in HORARIOS]

@login_required
def agendar(request):
    if request.method == 'POST':
        print("Por aqui paso algo")
        fecha = _parsear_fecha(request.POST.get('fecha'))
        #form = CitaForm(initial={'cliente_nombre': _nombre_de(request.user)})
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.usuario = request.user
            cita.abono = cita.servicio.abono     # monto a abonar (simulado)
            cita.abono_pagado = False            # se da por pagado cuando el salón la acepta
            cita.estado = Cita.PENDIENTE         # queda en espera de respuesta
            cita.save()
            form.save()
            request.session['ultima_cita'] = cita.pk
            return redirect('tienda:cita_confirmada')
    else:
        print("Por aqui no deberia pasar")
        fecha = _parsear_fecha(request.GET.get('fecha'))
        form = CitaForm()

    return render(request, 'tienda/agendar.html', {
        'form': form,
        'fecha': fecha,
        'hoy': timezone.localdate(),
        'horarios': _horarios(fecha) if fecha else [],
        'porcentaje_abono': PORCENTAJE_ABONO,
    })


def cita_confirmada(request):
    cita_id = request.session.get('ultima_cita')
    if not cita_id:
        return redirect('tienda:agendar')
    cita = get_object_or_404(
        Cita.objects.select_related('servicio').prefetch_related('servicio__productos_recomendados'),
        pk=cita_id,
    )
    return render(request, 'tienda/cita_confirmada.html', {'cita': cita})

# ---------------------------------------------------------------- Cuentas ---
def registro(request):
    if request.user.is_authenticated:
        return redirect('tienda:inicio')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)   # inicia sesión de inmediato
            messages.success(request, f'¡Bienvenido/a, {usuario.first_name}!')
            return redirect('tienda:inicio')
    else:
        form = RegistroForm()
    return render(request, 'tienda/registro.html', {'form': form})


@login_required
@login_required
def mis_citas(request):
    hoy = timezone.localdate()
    # Siempre se filtra por request.user: nadie ve citas ajenas.
    citas = Cita.objects.filter(usuario=request.user).select_related('servicio')
    proximas = citas.filter(
        fecha__gte=hoy, estado__in=[Cita.PENDIENTE, Cita.CONFIRMADA],
    )
    pasadas = citas.filter(
        Q(fecha__lt=hoy) | Q(estado__in=Cita.ESTADOS_QUE_LIBERAN)
    ).order_by('-fecha', '-hora')
    return render(request, 'tienda/mis_citas.html', {
        'proximas': proximas, 'pasadas': pasadas,
    })

@login_required
def mis_compras(request):
    pedidos = (
        Pedido.objects.filter(usuario=request.user)
        .prefetch_related('items__producto')
    )
    return render(request, 'tienda/mis_compras.html', {'pedidos': pedidos})

@login_required
@require_POST
def cancelar_cita(request, cita_id):
    # Con usuario=request.user, nadie puede cancelar citas de otra persona.
    cita = get_object_or_404(Cita, pk=cita_id, usuario=request.user)
    form = CancelacionForm(request.POST)
    if not cita.puede_cancelarse:
        messages.error(request, 'Esta cita ya no se puede cancelar.')
    elif form.is_valid():
        cita.cancelar(form.cleaned_data['motivo'])
        messages.success(request, 'Tu cita fue cancelada.')
    return redirect('tienda:mis_citas')