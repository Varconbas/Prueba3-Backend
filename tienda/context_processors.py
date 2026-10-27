def carrito(request):
    """Deja disponible `carrito_cantidad` en todas las plantillas (menú)."""
    carrito = request.session.get('carrito', {})
    return {'carrito_cantidad': sum(carrito.values())}
