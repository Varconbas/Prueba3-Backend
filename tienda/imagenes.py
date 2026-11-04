"""Utilidades de imágenes de productos. Solo usan Pillow (además de Django)."""
import textwrap
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont, ImageOps

ANCHO, ALTO = 600, 450   # formato 4:3 para todas las imágenes de producto

# (color superior, color inferior): degradados en morado y rosa
PALETAS = [
    ((123, 63, 160), (244, 169, 200)),
    ((150, 90, 190), (251, 200, 222)),
    ((90, 42, 120), (222, 140, 190)),
    ((170, 110, 205), (244, 169, 200)),
    ((105, 55, 140), (236, 160, 205)),
]


def _fuente(tamano):
    try:
        return ImageFont.load_default(size=tamano)   # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()              # Pillow antiguo: tamaño fijo


def _texto_centrado(draw, texto, centro_x, y, fuente, color):
    caja = draw.textbbox((0, 0), texto, font=fuente)
    ancho, alto = caja[2] - caja[0], caja[3] - caja[1]
    draw.text((centro_x - ancho / 2 - caja[0], y - caja[1]), texto, font=fuente, fill=color)
    return alto


def optimizar_imagen(archivo):
    """Recorta a 4:3, reduce a 600x450 y guarda como JPEG (ahorra espacio y
    deja todas las tarjetas con la misma proporción)."""
    archivo.seek(0)
    with Image.open(archivo) as original:
        imagen = ImageOps.exif_transpose(original).convert('RGB')   # respeta la rotación del celular
    imagen = ImageOps.fit(imagen, (ANCHO, ALTO), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    imagen.save(buffer, format='JPEG', quality=85, optimize=True)
    return ContentFile(buffer.getvalue(), name=f'{Path(archivo.name).stem}.jpg')


def generar_imagen_ejemplo(titulo, indice=0):
    """Crea una imagen de ejemplo (degradado morado/rosa + nombre del producto)."""
    arriba, abajo = PALETAS[indice % len(PALETAS)]
    imagen = Image.new('RGB', (ANCHO, ALTO))
    draw = ImageDraw.Draw(imagen)
    for y in range(ALTO):
        t = y / (ALTO - 1)
        draw.line([(0, y), (ANCHO, y)],
                  fill=tuple(round(arriba[i] + (abajo[i] - arriba[i]) * t) for i in range(3)))

    # Círculos translúcidos decorativos
    capa = Image.new('RGBA', (ANCHO, ALTO), (0, 0, 0, 0))
    deco = ImageDraw.Draw(capa)
    deco.ellipse((-90, -90, 210, 210), fill=(255, 255, 255, 55))
    deco.ellipse((410, 250, 710, 550), fill=(255, 255, 255, 45))
    deco.ellipse((330, -60, 450, 60), fill=(255, 255, 255, 35))
    imagen = Image.alpha_composite(imagen.convert('RGBA'), capa).convert('RGB')

    draw = ImageDraw.Draw(imagen)
    centro = ANCHO / 2
    _texto_centrado(draw, 'RG BEAUTY SPA', centro, 70, _fuente(24), (255, 255, 255))

    draw.rounded_rectangle((50, 125, ANCHO - 50, 325), radius=28, fill=(255, 255, 255))
    fuente = _fuente(36)
    lineas = textwrap.wrap(titulo, width=18)[:3]
    alto_linea = 46
    y = 225 - (len(lineas) * alto_linea) / 2
    for linea in lineas:
        _texto_centrado(draw, linea, centro, y, fuente, (90, 42, 120))
        y += alto_linea

    _texto_centrado(draw, 'Imagen de ejemplo', centro, 372, _fuente(20), (255, 255, 255))

    buffer = BytesIO()
    imagen.save(buffer, format='JPEG', quality=88, optimize=True)
    return ContentFile(buffer.getvalue())