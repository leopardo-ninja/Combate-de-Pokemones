# ----------------- FICHA DE POKÉMON (la misma en la Pokédex y en las estadísticas del equipo) -----------------
import pygame

from config import (
    BLANCO, AZUL_DS, COLORES_TIPO, FUENTE, FUENTE_CHICA, FUENTE_GRANDE
)
from pokemons import CATALOGO_POKEMONS
from .utilidades import separar_texto_en_lineas
from .recursos import obtener_pokemon

STAT_MAX = 130                      # valor que llena la barra de estadística
MARGEN_SUP = 12                     # espacio sobre la imagen
SEP_IMAGEN = 6                      # espacio entre la imagen y el nombre
MARGEN_INF = 14                     # espacio libre al final de la ficha
TAM_IMAGEN_MIN = 80
TAM_IMAGEN_MAX = 200
ESTADISTICAS = (("Ataque", "ataque"), ("Defensa", "defensa"), ("At. Esp.", "atk_esp"),
                ("Def. Esp.", "def_esp"), ("Velocidad", "velocidad"))

# Plan ya calculado para cada tamaño de ficha: (ancho, alto) -> (factor, lado de la imagen)
_CACHE_PLAN = {}
# Fichas que hubo que reducir para que cupieran: (nombre, ancho, alto) -> superficie ya escalada
_CACHE_FICHAS = {}


# Estadística con su barra (el relleno es proporcional al valor)
def _dibujar_barra(pantalla, x, y, derecha, etiqueta, valor, color):
    pantalla.blit(FUENTE_CHICA.render(etiqueta, True, (200, 220, 250)), (x, y))
    barra = pygame.Rect(x + 170, y + 4, 220, 18)
    pygame.draw.rect(pantalla, (25, 28, 40), barra, border_radius=9)
    ancho = int(barra.width * min(valor, STAT_MAX) / STAT_MAX)
    if ancho > 0:
        pygame.draw.rect(pantalla, color, (barra.x, barra.y, ancho, barra.height), border_radius=9)
    pygame.draw.rect(pantalla, (90, 105, 140), barra, 2, border_radius=9)
    num = FUENTE_CHICA.render(str(valor), True, BLANCO)
    pantalla.blit(num, num.get_rect(midright=(derecha, y + 13)))


# Todo lo que va debajo de la imagen: nombre, tipo, estadísticas, descripción y habilidades.
# Si pantalla es None no dibuja nada y solo mide: así se calcula cuánto espacio queda para la imagen.
# Devuelve la posición y donde termina el contenido.
def _contenido(pantalla, rect, nombre, datos, y, color_tipo):
    centro = rect.centerx
    x = rect.x + 30

    if pantalla is not None:
        txt = FUENTE_GRANDE.render(nombre.upper(), True, color_tipo)
        pantalla.blit(txt, txt.get_rect(midtop=(centro, y)))
    y += FUENTE_GRANDE.get_height() + 2

    if pantalla is not None:
        txt = FUENTE.render(f"Tipo: {datos['tipo']} | HP: {datos['hp']}", True, color_tipo)
        pantalla.blit(txt, txt.get_rect(midtop=(centro, y)))
    y += FUENTE.get_height() + 10

    # Estadísticas con barra
    for etiqueta, clave in ESTADISTICAS:
        if pantalla is not None:
            _dibujar_barra(pantalla, x, y, rect.right - 30, etiqueta, datos[clave], color_tipo)
        y += FUENTE_CHICA.get_linesize() + 4
    y += 6

    # Descripción
    for linea in separar_texto_en_lineas(datos["desc"], FUENTE_CHICA, rect.width - 60):
        if pantalla is not None:
            pantalla.blit(FUENTE_CHICA.render(linea.strip(), True, BLANCO), (x, y))
        y += FUENTE_CHICA.get_linesize()
    y += 8

    # Habilidades
    if pantalla is not None:
        pantalla.blit(FUENTE.render("Habilidades:", True, (200, 220, 250)), (x, y))
    y += FUENTE.get_linesize()
    for nombre_hab, potencia, tipo_hab in datos["habilidades"]:
        if pantalla is not None:
            detalle = "Estado" if potencia == 0 else f"{tipo_hab} - Pot. {potencia}"
            pantalla.blit(FUENTE_CHICA.render(f"• {nombre_hab} ({detalle})", True, BLANCO), (x, y))
        y += FUENTE_CHICA.get_linesize()
    return y


# Calcula cómo dibujar la ficha para que quepa en rect. Devuelve (factor, lado de la imagen):
# - La imagen ocupa lo que sobra después del texto del pokémon que más espacio necesita, así mide lo mismo para todos.
# - Si ni con la imagen al mínimo cabe el texto (fuentes grandes o tarjeta pequeña), factor sube por encima de 1:
#   la ficha se dibuja en un lienzo "factor" veces mayor y luego se reduce al tamaño de rect
def _plan(rect):
    clave = (rect.width, rect.height)
    if clave not in _CACHE_PLAN:
        factor = 1.0
        while True:
            grande = pygame.Rect(0, 0, round(rect.width * factor), round(rect.height * factor))
            texto_max = 0
            for nombre, datos in CATALOGO_POKEMONS.items():
                texto_max = max(texto_max, _contenido(None, grande, nombre, datos, 0, None))
            libre = grande.height - MARGEN_SUP - SEP_IMAGEN - texto_max - MARGEN_INF
            if libre >= TAM_IMAGEN_MIN * factor or factor >= 2.5:
                break
            factor = round(factor + 0.05, 2)
        lado = int(max(TAM_IMAGEN_MIN * factor, min(TAM_IMAGEN_MAX * factor, libre, grande.width - 60)))
        _CACHE_PLAN[clave] = (factor, lado)
    return _CACHE_PLAN[clave]


# Imagen del pokémon más todo su texto, dibujados sobre "superficie" dentro de rect
def _dibujar_contenido(superficie, rect, nombre, datos, color_tipo, lado):
    imagen = obtener_pokemon(nombre, "frente", (lado, lado))
    if imagen:
        superficie.blit(imagen, imagen.get_rect(midtop=(rect.centerx, rect.y + MARGEN_SUP)))
    _contenido(superficie, rect, nombre, datos, rect.y + MARGEN_SUP + lado + SEP_IMAGEN, color_tipo)


# Dibuja la ficha completa del pokémon dentro de rect: fondo, borde del color de su tipo,
# imagen, nombre, tipo, HP, estadísticas con barra, descripción y habilidades
def dibujar_ficha(pantalla, rect, nombre):
    datos = CATALOGO_POKEMONS[nombre]
    color_tipo = COLORES_TIPO.get(datos["tipo"].upper(), AZUL_DS)
    pygame.draw.rect(pantalla, (40, 45, 65), rect, border_radius=15)
    pygame.draw.rect(pantalla, color_tipo, rect, 4, border_radius=15)

    factor, lado = _plan(rect)
    if factor == 1.0:
        _dibujar_contenido(pantalla, rect, nombre, datos, color_tipo, lado)
        return
    # No cabe a tamaño normal: se dibuja en un lienzo mayor y se reduce (una sola vez; después sale de la caché)
    clave = (nombre, rect.width, rect.height)
    if clave not in _CACHE_FICHAS:
        ancho, alto = round(rect.width * factor), round(rect.height * factor)
        lienzo = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        _dibujar_contenido(lienzo, pygame.Rect(0, 0, ancho, alto), nombre, datos, color_tipo, lado)
        _CACHE_FICHAS[clave] = pygame.transform.smoothscale(lienzo, (rect.width, rect.height))
    pantalla.blit(_CACHE_FICHAS[clave], (rect.x, rect.y))