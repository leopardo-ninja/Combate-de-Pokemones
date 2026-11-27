# ----------------- POKÉDEX (misma cuadrícula que la selección) -----------------
import pygame

from config import (
    BLANCO, COLORES_TIPO, FUENTE_CHICA, FUENTE_GRANDE
)
from .utilidades import pos_virtual, dibujar_resalte
from .recursos import obtener_pokemon
from .ficha import dibujar_ficha
from .seleccion import EscenaSeleccion, ORIGEN_SEL, CELDA_SEL, FILAS_VISIBLES_SEL, RECT_PANEL_SEL, TAM_POKEMON_CELDA


# Pokédex: reutiliza la cuadrícula de la selección (flechas, mouse y rueda) pero sin elegir equipo.
# El panel de la derecha muestra la ficha completa del pokémon resaltado.
class EscenaPokedex(EscenaSeleccion):

    def __init__(self):
        super().__init__("pokedex")

    # En la Pokédex no se elige nada: ENTER y el clic solo resaltan (la ficha ya está a la vista)
    def elegir(self):
        return None

    def clic(self, pos_real):
        pos = pos_virtual(pos_real)
        for i in range(len(self.lista)):
            if self._visible(i) and self._rect(i).collidepoint(pos):
                self.idx = i
                return "ver"
        return None

    def dibujar(self, pantalla):
        pantalla.fill((25, 28, 40))
        pantalla.blit(FUENTE_GRANDE.render("POKÉDEX", True, BLANCO), (60, 30))

        # Cuadrícula (igual que en la selección, sin insignias de equipo)
        pantalla.set_clip(pygame.Rect(0, ORIGEN_SEL[1] - 12, 1350, FILAS_VISIBLES_SEL * CELDA_SEL[1] + 12))
        for i, nombre in enumerate(self.lista):
            if not self._visible(i):
                continue
            rect = self._rect(i)
            resaltado = (i == self.idx)
            pygame.draw.rect(pantalla, (55, 65, 100) if resaltado else (35, 42, 60), rect, border_radius=12)
            pygame.draw.rect(pantalla, COLORES_TIPO.get(self.tipos[i], (70, 85, 120)), rect,
                             4 if resaltado else 2, border_radius=12)
            if resaltado:
                dibujar_resalte(pantalla, rect)
            imagen = obtener_pokemon(nombre, "frente", TAM_POKEMON_CELDA)
            if imagen:
                pantalla.blit(imagen, imagen.get_rect(midtop=(rect.centerx, rect.y + 8)))
            txt = FUENTE_CHICA.render(nombre.capitalize(), True, BLANCO)
            pantalla.blit(txt, txt.get_rect(center=(rect.centerx, rect.bottom - 22)))
        pantalla.set_clip(None)

        # Panel con la ficha del pokémon resaltado (la misma que se ve en las estadísticas del equipo)
        dibujar_ficha(pantalla, RECT_PANEL_SEL, self.lista[self.idx])