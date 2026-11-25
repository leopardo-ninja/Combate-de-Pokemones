# ----------------- ESTADÍSTICAS DEL EQUIPO (antes del combate) -----------------
import pygame

from config import (
    BLANCO, NEGRO, AZUL_OSCURO, FUENTE, FUENTE_GRANDE
)
from pokemons import CATALOGO_POKEMONS
from .recursos import obtener_pokemon
from .utilidades import pos_virtual, dibujar_resalte

# Botón COMENZAR (coordenadas virtuales); se confirma con ENTER, ESPACIO o clic
RECT_COMENZAR = pygame.Rect(710, 900, 500, 70)


# True si la posición del mouse (pantalla real) cae sobre el botón COMENZAR.
def clic_comenzar(pos_real):
    return RECT_COMENZAR.collidepoint(pos_virtual(pos_real))

# Muestra las estadísticas de cada Pokémon del equipo antes de empezar el combate
def dibujar_estadisticas(pantalla, equipo_seleccionado):
        pantalla.fill((30, 144, 255))
        pygame.draw.rect(pantalla, (240, 245, 255), (100, 80, 1720, 920), border_radius=15)
        pygame.draw.rect(pantalla, (20, 80, 160), (100, 80, 1720, 920), 5, border_radius=15)

        pygame.draw.rect(pantalla, (20, 80, 160), (100, 80, 1720, 70), border_top_left_radius=15, border_top_right_radius=15)
        texto_encabezado = FUENTE.render("ESTADÍSTICAS DEL EQUIPO SELECCIONADO", True, BLANCO)
        pantalla.blit(texto_encabezado, (140, 100))

        # Una tarjeta por Pokémon, separadas 560 px entre sí
        for i, pokemon_elegido in enumerate(equipo_seleccionado):
            datos_pokemon = CATALOGO_POKEMONS[pokemon_elegido]
            tarjeta_x = 140 + (i * 560)
            tarjeta_y = 180

            pygame.draw.rect(pantalla, BLANCO, (tarjeta_x, tarjeta_y, 500, 680), border_radius=12)
            pygame.draw.rect(pantalla, (100, 150, 200), (tarjeta_x, tarjeta_y, 500, 680), 3, border_radius=12)

            imagen_frente = obtener_pokemon(pokemon_elegido, "frente", (250, 250))
            if imagen_frente:
                pantalla.blit(imagen_frente, (tarjeta_x + 125, tarjeta_y + 20))

            texto_nombre = FUENTE_GRANDE.render(pokemon_elegido.upper(), True, NEGRO)
            pantalla.blit(texto_nombre, (tarjeta_x + 30, tarjeta_y + 290))

            texto_tipo = FUENTE.render(f"Tipo: {datos_pokemon['tipo']} | Nv. 70", True, AZUL_OSCURO)
            pantalla.blit(texto_tipo, (tarjeta_x + 30, tarjeta_y + 350))

            lineas_estadisticas = [
                f"HP: {datos_pokemon['hp']}", f"Ataque: {datos_pokemon['ataque']}", f"Defensa: {datos_pokemon['defensa']}",
                f"At. Esp: {datos_pokemon['atk_esp']}", f"Velocidad: {datos_pokemon['velocidad']}"
            ]
            for indice_estadistica, linea in enumerate(lineas_estadisticas):
                texto_estadistica = FUENTE.render(linea, True, NEGRO)
                pantalla.blit(texto_estadistica, (tarjeta_x + 30, tarjeta_y + 420 + (indice_estadistica * 45)))

        # Botón COMENZAR: se resalta cuando el mouse está encima
        rect_boton = RECT_COMENZAR
        pygame.draw.rect(pantalla, (40, 180, 90), rect_boton, border_radius=12)
        if clic_comenzar(pygame.mouse.get_pos()):
            dibujar_resalte(pantalla, rect_boton)
        texto_comenzar = FUENTE.render("¡COMENZAR COMBATE!", True, BLANCO)
        rect_texto = texto_comenzar.get_rect(center=rect_boton.center)
        pantalla.blit(texto_comenzar, rect_texto)
