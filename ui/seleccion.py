# ----------------- SELECCIÓN DE POKÉMONS (cuadrícula) -----------------
import pygame

from config import (
    BLANCO, AZUL_DS, COLORES_TIPO, FUENTE, FUENTE_CHICA, FUENTE_GRANDE
)
from pokemons import SECCIONES_POKEMON, CATALOGO_POKEMONS
from .utilidades import pos_virtual, dibujar_resalte
from .recursos import obtener_pokemon

# Misma idea que la arena: cuadrícula de celdas con foco por flechas/mouse y panel de vista previa a la derecha
COLUMNAS_SEL = 6
CELDA_SEL = (215, 150)
ORIGEN_SEL = (60, 120)
FILAS_VISIBLES_SEL = 5                     # filas que caben en pantalla; si hay más, la cuadrícula se desplaza
RECT_PANEL_SEL = pygame.Rect(1360, 120, 520, 800)          # panel alto (lo usa la Pokédex para la ficha)
RECT_PANEL_VISTA_SEL = pygame.Rect(1360, 120, 520, 560)    # panel de la selección: solo imagen, nombre y tipo
TAM_POKEMON_CELDA = (96, 96)
TAM_POKEMON_PANEL = (400, 400)


# Pantalla para elegir el equipo: cuadrícula de pokémons (cada tipo empieza en una fila nueva).
class EscenaSeleccion:

    def __init__(self, modo):
        self.modo = modo
        self.meta = 1 if modo == "1v1" else 3     # cuántos pokémons hay que elegir
        self.equipo = []                          # nombres elegidos, en orden
        self.idx = 0                              # pokémon resaltado (índice en self.lista)
        self.scroll = 0                           # primera fila visible

        # Se recorre SECCIONES_POKEMON y a cada pokémon se le asigna (fila, columna); cada tipo empieza una fila nueva
        self.lista = []
        self.tipos = []
        self.pos = []
        fila = 0
        for tipo, pokes in SECCIONES_POKEMON.items():
            for k, nombre in enumerate(pokes):
                self.lista.append(nombre)
                self.tipos.append(tipo)
                self.pos.append((fila + k // COLUMNAS_SEL, k % COLUMNAS_SEL))
            fila += (len(pokes) + COLUMNAS_SEL - 1) // COLUMNAS_SEL
        self.filas = fila
        self.mapa = {p: i for i, p in enumerate(self.pos)}    # (fila, columna) -> índice

    # Rectángulo de la celda i en pantalla (tiene en cuenta el scroll)
    def _rect(self, i):
        fila, col = self.pos[i]
        return pygame.Rect(ORIGEN_SEL[0] + col * CELDA_SEL[0], ORIGEN_SEL[1] + (fila - self.scroll) * CELDA_SEL[1],
                           CELDA_SEL[0] - 10, CELDA_SEL[1] - 10)

    def _visible(self, i):
        return self.scroll <= self.pos[i][0] < self.scroll + FILAS_VISIBLES_SEL

    # Mueve el scroll lo justo para que la fila resaltada siempre se vea
    def _ajustar_scroll(self):
        fila = self.pos[self.idx][0]
        if fila < self.scroll:
            self.scroll = fila
        elif fila >= self.scroll + FILAS_VISIBLES_SEL:
            self.scroll = fila - FILAS_VISIBLES_SEL + 1

    # Flechas: se mueve por la cuadrícula; al subir/bajar a una fila más corta se queda en su última celda
    def mover(self, tecla):
        fila, col = self.pos[self.idx]
        nueva = None
        if tecla == pygame.K_LEFT:
            nueva = self.mapa.get((fila, col - 1))
        elif tecla == pygame.K_RIGHT:
            nueva = self.mapa.get((fila, col + 1))
        elif tecla in (pygame.K_UP, pygame.K_DOWN):
            f = fila + (-1 if tecla == pygame.K_UP else 1)
            while col >= 0 and (f, col) not in self.mapa and 0 <= f < self.filas:
                col -= 1
            nueva = self.mapa.get((f, col))
        if nueva is not None:
            self.idx = nueva
            self._ajustar_scroll()

    # Rueda del mouse: desplaza la cuadrícula de fila en fila
    def desplazar(self, pasos):
        maximo = max(0, self.filas - FILAS_VISIBLES_SEL)
        self.scroll = max(0, min(maximo, self.scroll - pasos))

    # Mouse encima: el resaltado pasa a la celda que esté bajo el cursor
    def pasar_mouse(self, pos_real):
        pos = pos_virtual(pos_real)
        for i in range(len(self.lista)):
            if self._visible(i) and self._rect(i).collidepoint(pos):
                self.idx = i
                return

    # Marca/desmarca el pokémon resaltado. Devuelve "completo" cuando el equipo ya tiene los que pide el modo
    def elegir(self):
        nombre = self.lista[self.idx]
        if nombre in self.equipo:
            self.equipo.remove(nombre)
            return "quitado"
        # Con el equipo ya completo no se puede elegir otro (hay que quitar uno antes)
        if len(self.equipo) >= self.meta:
            return None
        self.equipo.append(nombre)
        return "completo" if len(self.equipo) == self.meta else "elegido"

    # Al volver desde las estadísticas se quita el último elegido, para poder cambiarlo
    def deshacer_ultimo(self):
        if self.equipo:
            self.equipo.pop()

    # Clic sobre una celda: la resalta y la elige. Devuelve lo mismo que elegir() o None si no se pulsó ninguna
    def clic(self, pos_real):
        pos = pos_virtual(pos_real)
        for i in range(len(self.lista)):
            if self._visible(i) and self._rect(i).collidepoint(pos):
                self.idx = i
                return self.elegir()
        return None

    def dibujar(self, pantalla):
        pantalla.fill((25, 28, 40))
        titulo = FUENTE_GRANDE.render(f"SELECCIONA TUS POKÉMON ({len(self.equipo)}/{self.meta}) - Modo {self.modo}", True, BLANCO)
        pantalla.blit(titulo, (60, 30))

        # Cuadrícula (recortada para que las filas ocultas por el scroll no se vean)
        pantalla.set_clip(pygame.Rect(0, ORIGEN_SEL[1] - 12, 1350, FILAS_VISIBLES_SEL * CELDA_SEL[1] + 12))
        for i, nombre in enumerate(self.lista):
            if not self._visible(i):
                continue
            rect = self._rect(i)
            # Resaltada: la que tiene el foco (flechas / mouse) y también las ya elegidas, que se quedan marcadas
            resaltado = (i == self.idx) or (nombre in self.equipo)
            pygame.draw.rect(pantalla, (55, 65, 100) if resaltado else (35, 42, 60), rect, border_radius=12)
            pygame.draw.rect(pantalla, COLORES_TIPO.get(self.tipos[i], (70, 85, 120)), rect, 4 if resaltado else 2, border_radius=12)
            if resaltado:
                dibujar_resalte(pantalla, rect)
            imagen = obtener_pokemon(nombre, "frente", TAM_POKEMON_CELDA)
            if imagen:
                pantalla.blit(imagen, imagen.get_rect(midtop=(rect.centerx, rect.y + 8)))
            txt = FUENTE_CHICA.render(nombre.capitalize(), True, BLANCO)
            pantalla.blit(txt, txt.get_rect(center=(rect.centerx, rect.bottom - 22)))
        pantalla.set_clip(None)

        # Panel de vista previa del pokémon con el foco
        nombre = self.lista[self.idx]
        datos = CATALOGO_POKEMONS[nombre]
        panel = RECT_PANEL_VISTA_SEL
        pygame.draw.rect(pantalla, (40, 45, 65), panel, border_radius=15)
        pygame.draw.rect(pantalla, COLORES_TIPO.get(datos["tipo"].upper(), AZUL_DS), panel, 4, border_radius=15)
        imagen = obtener_pokemon(nombre, "frente", TAM_POKEMON_PANEL)
        if imagen:
            pantalla.blit(imagen, imagen.get_rect(midtop=(panel.centerx, panel.y + 20)))
        txt = FUENTE_GRANDE.render(nombre.upper(), True, COLORES_TIPO.get(datos["tipo"].upper(), AZUL_DS))
        pantalla.blit(txt, txt.get_rect(center=(panel.centerx, panel.y + 450)))
        txt = FUENTE.render(f"Tipo: {datos['tipo']}", True, COLORES_TIPO.get(datos["tipo"].upper(), AZUL_DS))
        pantalla.blit(txt, txt.get_rect(center=(panel.centerx, panel.y + 500)))

        ayuda = "Flechas + ENTER para elegir (otra vez para quitar) | ESC para volver"
        if self.filas > FILAS_VISIBLES_SEL:
            ayuda += " | Rueda del mouse para desplazar"
        pantalla.blit(FUENTE_CHICA.render(ayuda, True, (200, 220, 240)), (60, 1015))