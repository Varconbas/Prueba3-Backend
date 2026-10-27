from django.urls import path

from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('carrito/', views.ver_carrito, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/quitar/<int:producto_id>/', views.quitar_del_carrito, name='quitar_del_carrito'),
    path('carrito/pagar/', views.pagar, name='pagar'),
    path('pedido/confirmado/', views.pedido_confirmado, name='pedido_confirmado'),

    path('agendar/', views.agendar, name='agendar'),
    path('agendar/confirmada/', views.cita_confirmada, name='cita_confirmada'),
]
