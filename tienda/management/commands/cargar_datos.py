from django.core.management.base import BaseCommand
from django.utils.text import slugify

from tienda.models import Categoria, Producto, Servicio
from tienda.imagenes import generar_imagen_ejemplo


class Command(BaseCommand):
    help = 'Carga categorías, productos y servicios de ejemplo (se puede repetir sin duplicar).'

    def handle(self, *args, **options):
        cuidado, _ = Categoria.objects.get_or_create(nombre='Cuidado capilar')
        color, _ = Categoria.objects.get_or_create(nombre='Color y brillo')
        piel, _ = Categoria.objects.get_or_create(nombre='Cuidado de la piel')

        productos = [
            ('Shampoo Reparador', 'Limpieza suave para cabello dañado.', 12990, 15, cuidado),
            ('Mascarilla Nutritiva', 'Tratamiento intensivo de hidratación.', 15990, 10, cuidado),
            ('Sérum de Brillo', 'Control del frizz y brillo duradero.', 18990, 8, color),
            ('Protector de Color', 'Cuida el tono después de tu servicio.', 14990, 12, color),
            ('Crema Hidratante Facial', 'Hidratación diaria para todo tipo de piel.', 19990, 6, piel),
        ]
        obj = {}
        for indice, (nombre, desc, precio, stock, categoria) in enumerate(productos):
            p, creado = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc, 'precio': precio, 'stock': stock, 'categoria': categoria},
            )
            # Imagen de ejemplo generada con Pillow, solo si el producto no tiene una.
            if not p.imagen:
                p.imagen.save(f'{slugify(nombre)}.jpg', generar_imagen_ejemplo(nombre, indice), save=True)
            obj[nombre] = p
            
        servicios = [
            ('Corte y peinado', 'Corte personalizado con peinado final.', 25000, 60,
             ['Shampoo Reparador', 'Sérum de Brillo']),
            ('Tintura completa', 'Coloración profesional de raíz a puntas.', 55000, 150,
             ['Protector de Color', 'Mascarilla Nutritiva']),
            ('Tratamiento facial', 'Limpieza e hidratación profunda.', 35000, 75,
             ['Crema Hidratante Facial']),
        ]
        for nombre, desc, precio, duracion, recomendados in servicios:
            s, _ = Servicio.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc, 'precio': precio, 'duracion_minutos': duracion},
            )
            s.productos_recomendados.add(*[obj[n] for n in recomendados])

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados.'))
