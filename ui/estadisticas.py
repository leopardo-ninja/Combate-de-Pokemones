# ----------------- ESTADÍSTICAS DEL EQUIPO (antes del combate) -----------------
import pygame

from config import BLANCO, FUENTE
from .utilidades import pos_virtual, dibujar_resalte
from .ficha import dibujar_ficha

# Botón COMENZAR (coordenadas virtuales); se confirma con ENTER, ESPACIO o clic
RECT_COMENZAR = pygame.Rect(710, 900, 500, 70)


# True si la posición del mouse (pantalla real) cae sobre el botón COMENZAR.
def clic_comenzar(pos_real):
    return RECT_COMENZAR.collidepoint(pos_virtual(pos_real))


# Tamaño y posición de las tarjetas del equipo (coordenadas virtuales)
TAM_TARJETA = (560, 820)
Y_TARJETA = 50
SEP_TARJETAS = 40


# Muestra la ficha de cada Pokémon del equipo (la misma de la Pokédex) antes de empezar el combate.
# Las tarjetas van centradas: con 1 pokémon (1v1) queda una sola en el medio
def dibujar_estadisticas(pantalla, equipo_seleccionado):
        # Mismo fondo que la Pokédex; solo se ven las fichas y el botón
        pantalla.fill((25, 28, 40))

        # El conjunto de tarjetas se centra en la pantalla (centro en x=960)
        cantidad = len(equipo_seleccionado)
        ancho_total = cantidad * TAM_TARJETA[0] + (cantidad - 1) * SEP_TARJETAS
        x_inicial = 960 - ancho_total // 2
        for i, pokemon_elegido in enumerate(equipo_seleccionado):
            rect_tarjeta = pygame.Rect(x_inicial + i * (TAM_TARJETA[0] + SEP_TARJETAS), Y_TARJETA, TAM_TARJETA[0], TAM_TARJETA[1])
            dibujar_ficha(pantalla, rect_tarjeta, pokemon_elegido)

        # Botón COMENZAR: se resalta cuando el mouse está encima
        rect_boton = RECT_COMENZAR
        pygame.draw.rect(pantalla, (40, 180, 90), rect_boton, border_radius=12)
        if clic_comenzar(pygame.mouse.get_pos()):
            dibujar_resalte(pantalla, rect_boton)
        texto_comenzar = FUENTE.render("¡COMENZAR COMBATE!", True, BLANCO)
        rect_texto = texto_comenzar.get_rect(center=rect_boton.center)
        pantalla.blit(texto_comenzar, rect_texto)