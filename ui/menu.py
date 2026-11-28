# ----------------- MENÚ PRINCIPAL -----------------
import os
import pygame

from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL, BLANCO, FUENTE_CHICA, FUENTE_GRANDE
)
from .utilidades import Boton, dibujar_boton_menu

# Textos de los botones del menú, de arriba abajo
TEXTOS_MENU = ["Combate", "Pokédex", "Salir"]

# Logo "Pokémon UMA Edition" (PNG con transparencia), su ancho en pantalla y su posición vertical (coordenadas virtuales)
RUTA_LOGO = "assets/ui/logo_menu.png"
ANCHO_LOGO = 1000
Y_LOGO = 130

# Mosaico del fondo: el logo de la UMA (PNG blanco con transparencia), su ancho, su opacidad (0-255) y la separación
RUTA_LOGO_FONDO = "assets/ui/logo_uma.png"
ANCHO_LOGO_FONDO, ALPHA_LOGO_FONDO = 110, 18
SEP_LOGO_X, SEP_LOGO_Y = 220, 170

# Botones: x, y del primero, ancho, alto y separación entre ellos
BOTON_X, BOTON_Y0, BOTON_ANCHO, BOTON_ALTO, BOTON_SEP = 835, 540, 250, 70, 90

# Caché: el fondo y el logo se preparan una sola vez (no en cada frame)
_CACHE_MENU = {}


# Crea los botones del menú principal (x, y, ancho, alto, texto), uno debajo del otro
def crear_botones_menu():
    return [Boton(BOTON_X, BOTON_Y0 + i * BOTON_SEP, BOTON_ANCHO, BOTON_ALTO, texto) for i, texto in enumerate(TEXTOS_MENU)]


# Fondo del menú: mismo color liso que la Pokédex y el logo de la UMA muy tenue
COLOR_FONDO = (25, 28, 40)


def _crear_fondo():
    fondo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
    fondo.fill(COLOR_FONDO)

    # Logo de la UMA repetido en diagonal, muy suave (si falta la imagen, el fondo queda liso)
    if os.path.exists(RUTA_LOGO_FONDO):
        imagen = pygame.image.load(RUTA_LOGO_FONDO).convert_alpha()
        alto = int(imagen.get_height() * ANCHO_LOGO_FONDO / imagen.get_width())
        logo_uma = pygame.transform.smoothscale(imagen, (ANCHO_LOGO_FONDO, alto))
        logo_uma.set_alpha(ALPHA_LOGO_FONDO)
        for fila in range(-1, 8):
            for col in range(-1, 12):
                x = col * SEP_LOGO_X + (SEP_LOGO_X // 2 if fila % 2 else 0)
                y = fila * SEP_LOGO_Y
                fondo.blit(logo_uma, logo_uma.get_rect(center=(x, y)))
    return fondo


# Logo ya escalado (None si falta la imagen: entonces se dibuja el título con texto)
def _obtener_logo():
    if "logo" not in _CACHE_MENU:
        if os.path.exists(RUTA_LOGO):
            imagen = pygame.image.load(RUTA_LOGO).convert_alpha()
            alto = int(imagen.get_height() * ANCHO_LOGO / imagen.get_width())
            _CACHE_MENU["logo"] = pygame.transform.smoothscale(imagen, (ANCHO_LOGO, alto))
        else:
            _CACHE_MENU["logo"] = None
    return _CACHE_MENU["logo"]


# ----------------- PANTALLAS -----------------
# Dibuja el menú principal: fondo, logo y botones (el seleccionado lleva resalte)
def dibujar_menu_principal(pantalla, botones, seleccion_idx):
    if "fondo" not in _CACHE_MENU:
        _CACHE_MENU["fondo"] = _crear_fondo()
    pantalla.blit(_CACHE_MENU["fondo"], (0, 0))

    logo = _obtener_logo()
    if logo:
        pantalla.blit(logo, logo.get_rect(midtop=(ANCHO_VIRTUAL // 2, Y_LOGO)))
    else:
        # Respaldo si falta assets/ui/logo_menu.png
        titulo = FUENTE_GRANDE.render("POKÉMON UMA EDITION", True, BLANCO)
        pantalla.blit(titulo, titulo.get_rect(midtop=(ANCHO_VIRTUAL // 2, Y_LOGO + 120)))

    for idx, boton in enumerate(botones):
        dibujar_boton_menu(pantalla, boton, idx == seleccion_idx)