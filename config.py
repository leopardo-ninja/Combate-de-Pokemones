# Constantes compartidas por todo el juego: resolución, colores y fuentes

import pygame

# Pygame debe iniciarse antes de crear las fuentes
pygame.init()
pygame.font.init()

MODO_VENTANA = False

# Resolución Virtual de Referencia
ANCHO_VIRTUAL, ALTO_VIRTUAL = 1920, 1080

# Resolución real
if MODO_VENTANA:
    ANCHO_REAL, ALTO_REAL = 1280, 720
else:
    _info_pantalla = pygame.display.Info()
    ANCHO_REAL, ALTO_REAL = _info_pantalla.current_w, _info_pantalla.current_h

# Colores Base y de Interfaz DS
BLANCO = (255, 255, 255)
NEGRO = (30, 30, 30)
GRIS_CLARO = (245, 245, 250)
GRIS_OSCURO = (70, 70, 80)
AZUL_DS = (30, 144, 255)
AZUL_OSCURO = (15, 45, 90)
ROJO_BOTON = (215, 60, 60)
VERDE_BOTON = (40, 180, 90)
AZUL_BOTON = (30, 140, 210)
BORDE_CAJA = (40, 40, 50)
AMARILLO_ALERTA = (230, 190, 40)
ROJO_ALERTA = (220, 50, 50)

# Colores de Tipos
COLORES_TIPO = {
    "FUEGO": (230, 80, 40),
    "AGUA": (40, 130, 235),
    "PLANTA": (50, 180, 70),
    "ELÉCTRICO": (220, 190, 20),
    "TIERRA": (160, 110, 50),
}

# Fuentes Escaladas
RUTA_FUENTE = "assets/fuentes/Comfortaa-Bold.ttf"
FUENTE = pygame.font.Font(RUTA_FUENTE, 26)
FUENTE_CHICA = pygame.font.Font(RUTA_FUENTE, 20)
FUENTE_GRANDE = pygame.font.Font(RUTA_FUENTE, 38)