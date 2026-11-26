# ----------------- MENÚ PRINCIPAL -----------------
import pygame

from config import (
    BLANCO, AZUL_DS, FUENTE_CHICA, FUENTE_GRANDE
)
from .utilidades import Boton

# Textos de los botones del menú, de arriba abajo
TEXTOS_MENU = ["Modo Arena", "Pokédex", "Salir"]


# Crea los botones del menú principal (x, y, ancho, alto, texto), uno debajo del otro dentro del panel
def crear_botones_menu():
    return [Boton(710, 430 + i * 90, 500, 70, texto) for i, texto in enumerate(TEXTOS_MENU)]


# ----------------- PANTALLAS -----------------
# Dibuja el menú principal: panel azul, título y botones (el seleccionado lleva resalte)
def dibujar_menu_principal(pantalla, botones, seleccion_idx):
    pantalla.fill((20, 35, 60))
    pygame.draw.rect(pantalla, AZUL_DS, (610, 240, 700, 600), border_radius=20)
    pygame.draw.rect(pantalla, BLANCO, (610, 240, 700, 600), 6, border_radius=20)

    titulo = FUENTE_GRANDE.render("POKÉMON", True, BLANCO)
    pantalla.blit(titulo, (720, 300))

    for idx, boton in enumerate(botones):
        boton.dibujar(pantalla, resaltado=(idx == seleccion_idx))

    texto_ayuda = FUENTE_CHICA.render("Usa Flechas ARRIBA/ABAJO y ENTER para seleccionar", True, (200, 220, 240))
    pantalla.blit(texto_ayuda, (710, 800))