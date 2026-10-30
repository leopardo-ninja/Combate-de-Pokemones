# ----------------- ENTRENADORES -----------------
# Los tres personajes son los tres integrantes del equipo.
#
# El arte se dibuja en un programa de pixel art (Piskel, Aseprite, LibreSprite...)
# y se guarda como PNG en assets/entrenadores/<nombre>/:
#
#   busto.png    retrato cuadrado (cabeza y hombros), de cualquier tamaño (ej. 112x112)
#   caminar.png  hoja de 3 columnas x 4 filas, todos los cuadros del mismo tamaño (ej. 32x48):
#                  columnas: quieto, paso A, paso B
#                  filas:    abajo, izquierda, derecha, arriba   (formato de RPG Maker)
#
# Si falta algún PNG se usa el dibujo guardado en personajes/<nombre>.py.
# Ver assets/entrenadores/LEEME.md para las instrucciones de dibujo.

import os

import pygame

import datos_personajes as dp

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "entrenadores")
FILAS_HOJA = ["abajo", "izquierda", "derecha", "arriba"]

ENTRENADORES = {
    "tortuga": {"nombre": "Tortuga", "frase": "Lento pero seguro. Nunca se rinde."},
    "leopardo": {"nombre": "Leopardo", "frase": "Rápido y curioso. Siempre va primero."},
    "tullio": {"nombre": "Tullio", "frase": "Tranquilo y calculador. Viste de negro."},
}
ORDEN_ENTRENADORES = ["tortuga", "leopardo", "tullio"]

_CACHE = {}


def _png(nombre, archivo):
    ruta = os.path.join(CARPETA, nombre, archivo)
    if os.path.exists(ruta):
        return pygame.image.load(ruta).convert_alpha()
    return None


def _escalar(sup, alto):
    """Amplía sin suavizar (píxeles nítidos) hasta la altura pedida, manteniendo la proporción."""
    ancho = round(sup.get_width() * alto / sup.get_height())
    return pygame.transform.scale(sup, (ancho, alto))


# ----------------- Cuadros sin escalar -----------------
def _cuadros_originales(nombre):
    """{direccion: [quieto, paso_a, paso_b]} al tamaño en que se dibujaron."""
    hoja = _png(nombre, "caminar.png")
    if hoja is not None:
        w, h = hoja.get_width() // 3, hoja.get_height() // 4
        return {d: [hoja.subsurface((c * w, f * h, w, h)).copy() for c in range(3)]
                for f, d in enumerate(FILAS_HOJA)}
    datos = dp.cargar(nombre)
    if "SPRITES" in datos:
        cuadros = {d: [dp.filas_a_superficie(fr, datos["PALETA_SPRITE"]) for fr in datos["SPRITES"][d]]
                   for d in dp.DIRECCIONES}
        cuadros["izquierda"] = [pygame.transform.flip(s, True, False) for s in cuadros["derecha"]]
        return cuadros
    vacio = pygame.Surface((dp.ANCHO_SPRITE, dp.ALTO_SPRITE), pygame.SRCALPHA)
    pygame.draw.rect(vacio, (255, 0, 255), vacio.get_rect(), 2)       # aviso: falta el dibujo
    return {d: [vacio] * 3 for d in FILAS_HOJA}


def _busto_original(nombre):
    busto = _png(nombre, "busto.png")
    if busto is not None:
        return busto
    datos = dp.cargar(nombre)
    if "BUSTO" in datos:
        return dp.filas_a_superficie(datos["BUSTO"], datos["PALETA_BUSTO"])
    return crear_sprites(nombre, 96)["abajo"][0]


# ----------------- API usada por el juego -----------------
def crear_sprites(nombre, alto=96):
    """Cuadros de caminar escalados a 'alto' píxeles: {direccion: [quieto, paso_a, paso_b]}."""
    clave = ("sprites", nombre, alto)
    if clave not in _CACHE:
        _CACHE[clave] = {d: [_escalar(s, alto) for s in cuadros]
                         for d, cuadros in _cuadros_originales(nombre).items()}
    return _CACHE[clave]


def crear_busto(nombre, lado):
    """Retrato ajustado a un cuadrado de 'lado' píxeles (centrado, sin suavizar)."""
    clave = ("busto", nombre, lado)
    if clave not in _CACHE:
        original = _busto_original(nombre)
        factor = lado / max(original.get_width(), original.get_height())
        if factor >= 1:
            factor = int(factor)                  # múltiplo entero: los píxeles quedan iguales
        grande = pygame.transform.scale(original, (round(original.get_width() * factor),
                                                   round(original.get_height() * factor)))
        sup = pygame.Surface((lado, lado), pygame.SRCALPHA)
        sup.blit(grande, grande.get_rect(midbottom=(lado // 2, lado)))
        _CACHE[clave] = sup
    return _CACHE[clave]


def recargar():
    """Olvida lo cargado (por si se cambian los PNG con el juego abierto)."""
    _CACHE.clear()
