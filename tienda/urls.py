from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from . import views
from django.conf.urls.static import static

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
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='tienda/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('mis-citas/', views.mis_citas, name='mis_citas'),
    path('mis-citas/<int:cita_id>/cancelar/', views.cancelar_cita, name='cancelar_cita'),
    path('mis-compras/', views.mis_compras, name='mis_compras'),
    path('panel/citas/', views.panel_citas, name='panel_citas'),
    path('panel/citas/<int:cita_id>/responder/', views.responder_cita, name='responder_cita'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/password/', views.cambiar_password, name='cambiar_password'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
