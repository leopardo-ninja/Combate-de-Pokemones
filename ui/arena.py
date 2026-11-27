# ----------------- MODO ARENA: formato + escenario -----------------
import pygame

from config import (
    BLANCO, NEGRO, AZUL_DS, VERDE_BOTON, FUENTE, FUENTE_CHICA, FUENTE_GRANDE
)
from escenarios import ESCENARIOS
from .utilidades import pos_virtual, dibujar_resalte
from .recursos import obtener_base, obtener_vista_previa

# Modo Arena: columnas de la cuadrícula de escenarios, tamaño y origen de cada celda, botones de formato y vista previa
COLUMNAS_ARENA = 6
CELDA_ARENA = (215, 150)
ORIGEN_ARENA = (60, 220)
RECT_FORMATOS = [pygame.Rect(60, 110, 300, 70), pygame.Rect(380, 110, 300, 70)]
FORMATOS = ["1v1", "3v3"]
TAM_VISTA_PREVIA = (480, 270)
POS_VISTA_PREVIA = (1380, 220)


# Rectángulo de la celda número idx de la cuadrícula (fila y columna salen con divmod)
def rect_celda_arena(idx):
    fila, col = divmod(idx, COLUMNAS_ARENA)
    return pygame.Rect(ORIGEN_ARENA[0] + col * CELDA_ARENA[0], ORIGEN_ARENA[1] + fila * CELDA_ARENA[1],
                       CELDA_ARENA[0] - 10, CELDA_ARENA[1] - 10)


# Pantalla del modo Arena: se elige el formato (1v1 / 3v3) y el escenario.
class EscenaArena:

    def __init__(self):
        self.formato = 0          # índice en FORMATOS (el elegido de verdad: solo cambia con clic)
        self.formato_foco = 0     # botón de formato resaltado (flechas / mouse), no cambia la selección
        self.escenario = 0        # índice en ESCENARIOS
        self.foco = "grid"        # "formato" o "grid": dónde están las flechas

    @property
    def modo(self):
        return FORMATOS[self.formato]

    # Flechas. Con el foco en "formato": izquierda/derecha solo mueven el resalte entre 1v1/3v3 y abajo baja a la cuadrícula.
    # En la cuadrícula: se mueve entre escenarios y, desde la primera fila, arriba sube al formato
    def mover(self, tecla):
        cantidad_escenarios = len(ESCENARIOS)
        if self.foco == "formato":
            if tecla == pygame.K_LEFT:
                self.formato_foco = 0
            elif tecla == pygame.K_RIGHT:
                self.formato_foco = 1
            elif tecla == pygame.K_DOWN:
                self.foco = "grid"
            return
        fila, col = divmod(self.escenario, COLUMNAS_ARENA)
        if tecla == pygame.K_LEFT and col > 0:
            self.escenario -= 1
        elif tecla == pygame.K_RIGHT and self.escenario + 1 < cantidad_escenarios and col < COLUMNAS_ARENA - 1:
            self.escenario += 1
        elif tecla == pygame.K_DOWN:
            self.escenario = min(self.escenario + COLUMNAS_ARENA, cantidad_escenarios - 1)
        elif tecla == pygame.K_UP:
            if fila == 0:
                self.foco = "formato"
            else:
                self.escenario -= COLUMNAS_ARENA

    # ENTER: en el formato baja a los escenarios; en un escenario continúa. Devuelve 'continuar' o None.
    def elegir(self):
        if self.foco == "formato":
            self.foco = "grid"
            return None
        return "continuar"

    # Mouse encima: solo mueve el resalte (no cambia el formato elegido)
    def pasar_mouse(self, pos_real):
        pos = pos_virtual(pos_real)
        for i, rect_boton in enumerate(RECT_FORMATOS):
            if rect_boton.collidepoint(pos):
                self.foco = "formato"
                self.formato_foco = i
                return
        for i in range(len(ESCENARIOS)):
            if rect_celda_arena(i).collidepoint(pos):
                self.foco = "grid"
                self.escenario = i
                return

    # Clic sobre un formato lo elige y devuelve "formato"; sobre un escenario lo elige y devuelve "continuar"
    def clic(self, pos_real):
        pos = pos_virtual(pos_real)
        for i, rect_boton in enumerate(RECT_FORMATOS):
            if rect_boton.collidepoint(pos):
                self.foco = "formato"
                self.formato_foco = i
                self.formato = i
                return "formato"
        for i in range(len(ESCENARIOS)):
            if rect_celda_arena(i).collidepoint(pos):
                self.foco = "grid"
                self.escenario = i
                return "continuar"
        return None

    def dibujar(self, pantalla):
        pantalla.fill((25, 28, 40))
        pantalla.blit(FUENTE_GRANDE.render("COMBATE", True, BLANCO), (60, 30))

        # Formato: el verde marca el elegido (clic); el borde resaltado marca el foco (flechas / mouse)
        for i, rect_formato in enumerate(RECT_FORMATOS):
            activo = (i == self.formato)
            pygame.draw.rect(pantalla, VERDE_BOTON if activo else (45, 52, 75), rect_formato, border_radius=12)
            pygame.draw.rect(pantalla, BLANCO if activo else (90, 105, 140), rect_formato, 3, border_radius=12)
            etiqueta = "1 vs 1" if i == 0 else "3 vs 3"
            txt = FUENTE_GRANDE.render(etiqueta, True, BLANCO)
            pantalla.blit(txt, txt.get_rect(center=rect_formato.center))
            if self.foco == "formato" and i == self.formato_foco:
                dibujar_resalte(pantalla, rect_formato)

        # Cuadrícula de escenarios
        for i, datos_escenario in enumerate(ESCENARIOS):
            rect_celda = rect_celda_arena(i)
            elegido = (i == self.escenario)
            pygame.draw.rect(pantalla, (55, 65, 100) if elegido else (35, 42, 60), rect_celda, border_radius=12)
            pygame.draw.rect(pantalla, (130, 150, 200) if elegido else (70, 85, 120),
                             rect_celda, 4 if elegido else 2, border_radius=12)
            if elegido and self.foco == "grid":
                dibujar_resalte(pantalla, rect_celda)
            base = obtener_base("rival", datos_escenario["base"], 1.5)
            if base:
                pantalla.blit(base, base.get_rect(center=(rect_celda.centerx, rect_celda.y + 62)))
            txt = FUENTE_CHICA.render(datos_escenario["nombre"], True, BLANCO)
            pantalla.blit(txt, txt.get_rect(center=(rect_celda.centerx, rect_celda.bottom - 22)))

        # Vista previa del escenario elegido
        vista_x, vista_y = POS_VISTA_PREVIA
        pygame.draw.rect(pantalla, (40, 45, 65), (vista_x - 20, vista_y - 20, TAM_VISTA_PREVIA[0] + 40, 460), border_radius=15)
        pygame.draw.rect(pantalla, AZUL_DS, (vista_x - 20, vista_y - 20, TAM_VISTA_PREVIA[0] + 40, 460), 4, border_radius=15)
        pantalla.blit(obtener_vista_previa(self.escenario, TAM_VISTA_PREVIA), (vista_x, vista_y))
        pygame.draw.rect(pantalla, NEGRO, (vista_x, vista_y, TAM_VISTA_PREVIA[0], TAM_VISTA_PREVIA[1]), 3)
        nombre = FUENTE_GRANDE.render(ESCENARIOS[self.escenario]["nombre"], True, (255, 230, 50))
        pantalla.blit(nombre, nombre.get_rect(center=(vista_x + TAM_VISTA_PREVIA[0] // 2, vista_y + TAM_VISTA_PREVIA[1] + 50)))
        modo = FUENTE.render(f"Formato: {self.modo}", True, BLANCO)
        pantalla.blit(modo, modo.get_rect(center=(vista_x + TAM_VISTA_PREVIA[0] // 2, vista_y + TAM_VISTA_PREVIA[1] + 100)))