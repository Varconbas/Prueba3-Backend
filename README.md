Bastian Varas Contreras

# RG Beauty SPA — versión Django

Adaptación del `index.html` (tienda, agendar hora, carrito, admin) a Django, con **una sola app: `tienda`**.
Stock y pagos están **simulados**; el CSS es un placeholder (blanco, morado y rosa).

## Puesta en marcha (mismo flujo de las Clases 8 a 11)

1. Crear la base en MySQL:
   `CREATE DATABASE rgbeauty_db CHARACTER SET utf8mb4;`
2. Entorno e instalación:
   `pip install -r requirements.txt`
3. Credenciales: editar el bloque `DATABASES` de `rgbeauty/settings.py`
   o definir las variables de entorno `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
   (Para probar sin MySQL: `USAR_SQLITE=1`.)
4. Migraciones:
   `python manage.py makemigrations tienda`
   `python manage.py migrate`
5. Superusuario y datos de ejemplo:
   `python manage.py createsuperuser`
   `python manage.py cargar_datos`
6. `python manage.py runserver` → http://127.0.0.1:8000/ y http://127.0.0.1:8000/admin/

## Equivalencias con el index.html

| index.html | Django |
|---|---|
| Vista Tienda (`contenedor-productos`) | `views.inicio` + `tienda.html` (filtro por categoría) |
| Vista Carrito (JS) | carrito en sesión: `views.ver_carrito`, `agregar_al_carrito`, `actualizar_carrito`, `quitar_del_carrito`, `pagar` |
| Vista Agendar | `views.agendar` + `CitaForm` (horarios ocupados deshabilitados) |
| Panel Admin: inventario | `ProductoAdmin` (precio y stock editables en el listado) |
| Panel Admin: agenda de citas | `CitaAdmin` (filtros, búsqueda, acciones confirmar/cancelar) |

## Modelos y relaciones

- `Categoria` 1:N `Producto` (FK, `related_name='productos'`)
- `Servicio` N:M `Producto` (`productos_recomendados`, `related_name='servicios'`)
- `Servicio` 1:N `Cita` (FK, `related_name='citas'`)
- `Pedido` 1:N `ItemPedido` (FK, `related_name='items'`) y `Producto` 1:N `ItemPedido`

## Por hacer:
X Roles (Usuario, Admin)
| Mejorar el agendamiento de las citas (Que un usuario pida una cita, quede en espera, que el admin pueda aceptar o no esa cita, y el usuario pueda cancelar en cualquier momento.)
| En el apartado de usuarios, uno pueda ver las citas agendadas actuales y con anterioridad
- Agregar imagenes
- Arreglar las citas 