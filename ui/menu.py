# ----------------- MENÚ PRINCIPAL -----------------
import pygame

from config import (
    BLANCO, AZUL_DS, FUENTE_CHICA, FUENTE_GRANDE
)


# ----------------- PANTALLAS -----------------
# Dibuja el menú principal: panel azul, título y botones (el seleccionado lleva resalte)
def dibujar_menu_principal(pantalla, botones, seleccion_idx):
    pantalla.fill((20, 35, 60))
    pygame.draw.rect(pantalla, AZUL_DS, (610, 240, 700, 600), border_radius=20)
    pygame.draw.rect(pantalla, BLANCO, (610, 240, 700, 600), 6, border_radius=20)

    titulo = FUENTE_GRANDE.render("POKÉMON AÑIL - DUELO", True, BLANCO)
    pantalla.blit(titulo, (720, 300))

    for idx, boton in enumerate(botones):
        boton.dibujar(pantalla, resaltado=(idx == seleccion_idx))

    texto_ayuda = FUENTE_CHICA.render("Usa Flechas ARRIBA/ABAJO y ENTER para seleccionar", True, (200, 220, 240))
    pantalla.blit(texto_ayuda, (710, 800))
