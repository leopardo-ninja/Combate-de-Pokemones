# ----------------- UTILIDADES COMPARTIDAS: mouse, resalte, texto y botones -----------------
import pygame

from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL, ANCHO_REAL, ALTO_REAL, BLANCO, AZUL_OSCURO, FUENTE
)


COLOR_RESALTE = (222, 239, 255)        # linea interior (plateado)
COLOR_RESALTE_BORDE = (30, 30, 30)     # contorno exterior oscuro


# Convierte la posición del mouse de la pantalla real a la virtual (1920x1080), porque todo se dibuja en la virtual y luego se escala
def pos_virtual(pos):
    #Posicion del mouse
    return (int(pos[0] * ANCHO_VIRTUAL / ANCHO_REAL), int(pos[1] * ALTO_VIRTUAL / ALTO_REAL))


# Resalte unico de todo el juego: borde doble, oscuro por fuera y plateado por dentro.
def dibujar_resalte(pantalla, rect, radio=12):
    pygame.draw.rect(pantalla, COLOR_RESALTE_BORDE, rect.inflate(8, 8), 8, border_radius=radio + 2)
    pygame.draw.rect(pantalla, COLOR_RESALTE, rect.inflate(4, 4), 4, border_radius=radio)


# Relleno del botón resaltado (el botón resaltado se aclara y su borde se engrosa)
COLOR_BOTON_RESALTADO = (35, 68, 130)


# Dibuja un botón del menú; si está resaltado (flechas o mouse encima) se aclara y engrosa el borde
# Se usa en el menú principal y en la pausa del combate
def dibujar_boton_menu(pantalla, boton, resaltado):
    pygame.draw.rect(pantalla, COLOR_BOTON_RESALTADO if resaltado else AZUL_OSCURO, boton.rect, border_radius=12)
    pygame.draw.rect(pantalla, BLANCO, boton.rect, 4 if resaltado else 2, border_radius=12)
    fuente = getattr(boton, "fuente", FUENTE)
    txt = fuente.render(boton.texto, True, BLANCO)
    pantalla.blit(txt, txt.get_rect(center=boton.rect.center))


# Parte un texto largo en líneas que quepan en max_ancho píxeles (para mensajes y descripciones)
def separar_texto_en_lineas(texto, fuente, max_ancho):
    # Se arma cada línea palabra por palabra
    palabras = texto.split(" ")
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        prueba = linea_actual + palabra + " "
        # Si la palabra cabe, se añade a la línea; si no, se cierra la línea y se empieza otra
        if fuente.size(prueba)[0] < max_ancho:
            linea_actual = prueba
        else:
            lineas.append(linea_actual)
            linea_actual = palabra + " "
    lineas.append(linea_actual)
    return lineas


class Boton:
    # Botón rectangular reactivo con texto

    def __init__(self, x, y, ancho, alto, texto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto

    # True si la posición del mouse (pantalla real) cae sobre el botón.
    def contiene(self, pos_real):
        return self.rect.collidepoint(pos_virtual(pos_real))

    def dibujar(self, superficie, resaltado=False):
        color = BLANCO
        # Fondo azul con borde blanco; si el botón está resaltado se añade el borde doble del resalte
        pygame.draw.rect(superficie, AZUL_OSCURO, self.rect, border_radius=12)
        pygame.draw.rect(superficie, color, self.rect, 4, border_radius=12)
        if resaltado:
            dibujar_resalte(superficie, self.rect)
        txt = FUENTE.render(self.texto, True, color)
        superficie.blit(txt, txt.get_rect(center=self.rect.center))