# ----------------- POKÉDEX (misma cuadrícula que la selección) -----------------
import pygame

from config import (
    BLANCO, AZUL_DS, COLORES_TIPO, FUENTE, FUENTE_CHICA, FUENTE_GRANDE
)
from pokemons import CATALOGO_POKEMONS
from .utilidades import pos_virtual, dibujar_resalte, separar_texto_en_lineas
from .recursos import obtener_pokemon
from .seleccion import EscenaSeleccion, ORIGEN_SEL, CELDA_SEL, FILAS_VISIBLES_SEL, RECT_PANEL_SEL, TAM_POKEMON_CELDA


# Pokédex: reutiliza la cuadrícula de la selección (flechas, mouse y rueda) pero sin elegir equipo.
# El panel de la derecha muestra la ficha completa del pokémon resaltado.
class EscenaPokedex(EscenaSeleccion):

    TAM_IMAGEN_FICHA = (180, 180)
    STAT_MAX = 130                          # valor que llena la barra de estadística

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

    def _dibujar_barra(self, pantalla, x, y, etiqueta, valor, color):
        pantalla.blit(FUENTE_CHICA.render(etiqueta, True, (200, 220, 250)), (x, y))
        barra = pygame.Rect(x + 170, y + 4, 220, 18)
        pygame.draw.rect(pantalla, (25, 28, 40), barra, border_radius=9)
        ancho = int(barra.width * min(valor, self.STAT_MAX) / self.STAT_MAX)
        if ancho > 0:
            pygame.draw.rect(pantalla, color, (barra.x, barra.y, ancho, barra.height), border_radius=9)
        pygame.draw.rect(pantalla, (90, 105, 140), barra, 2, border_radius=9)
        num = FUENTE_CHICA.render(str(valor), True, BLANCO)
        pantalla.blit(num, num.get_rect(midright=(RECT_PANEL_SEL.right - 30, y + 13)))

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

        # Panel con la ficha del pokémon resaltado
        nombre = self.lista[self.idx]
        datos = CATALOGO_POKEMONS[nombre]
        color_tipo = COLORES_TIPO.get(self.tipos[self.idx], AZUL_DS)
        panel = RECT_PANEL_SEL
        pygame.draw.rect(pantalla, (40, 45, 65), panel, border_radius=15)
        pygame.draw.rect(pantalla, color_tipo, panel, 4, border_radius=15)

        imagen = obtener_pokemon(nombre, "frente", self.TAM_IMAGEN_FICHA)
        if imagen:
            pantalla.blit(imagen, imagen.get_rect(midtop=(panel.centerx, panel.y + 12)))
        y = panel.y + 12 + self.TAM_IMAGEN_FICHA[1] + 6

        txt = FUENTE_GRANDE.render(nombre.upper(), True, (255, 230, 50))
        pantalla.blit(txt, txt.get_rect(midtop=(panel.centerx, y)))
        y += txt.get_height() + 2
        txt = FUENTE.render(f"Tipo: {datos['tipo']} | HP: {datos['hp']}", True, (255, 220, 50))
        pantalla.blit(txt, txt.get_rect(midtop=(panel.centerx, y)))
        y += txt.get_height() + 10

        # Estadísticas con barra
        paso = FUENTE_CHICA.get_linesize() + 4
        for etiqueta, clave in (("Ataque", "ataque"), ("Defensa", "defensa"), ("At. Esp.", "atk_esp"),
                                ("Def. Esp.", "def_esp"), ("Velocidad", "velocidad")):
            self._dibujar_barra(pantalla, panel.x + 30, y, etiqueta, datos[clave], color_tipo)
            y += paso
        y += 6

        # Descripción
        for linea in separar_texto_en_lineas(datos["desc"], FUENTE_CHICA, panel.width - 60):
            pantalla.blit(FUENTE_CHICA.render(linea.strip(), True, BLANCO), (panel.x + 30, y))
            y += FUENTE_CHICA.get_linesize()
        y += 8

        # Habilidades
        pantalla.blit(FUENTE.render("Habilidades:", True, (200, 220, 250)), (panel.x + 30, y))
        y += FUENTE.get_linesize()
        for nombre_hab, potencia, tipo_hab in datos["habilidades"]:
            detalle = "Estado" if potencia == 0 else f"{tipo_hab} - Pot. {potencia}"
            pantalla.blit(FUENTE_CHICA.render(f"• {nombre_hab} ({detalle})", True, BLANCO), (panel.x + 30, y))
            y += FUENTE_CHICA.get_linesize()

        ayuda = "Flechas / mouse: ver pokémon | Rueda del mouse: desplazar | ESC o clic derecho: volver"
        pantalla.blit(FUENTE_CHICA.render(ayuda, True, (200, 220, 240)), (60, 1015))
