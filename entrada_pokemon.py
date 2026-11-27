# ----------------- ENTRADA DE UN POKÉMON: la Poké Ball cae, se abre con un destello y sale el Pokémon -----------------
# Usa assets/ui/pokebola_roja.png: una tira de 9 fotogramas de 16x16 px de la Poké Ball roja.
#   0 cerrada | 1 tapa abriéndose | 2 esfera blanca | 5 abierta con luz | 6, 7 girando
#
# Uso desde la interfaz (EscenaCombate):
#   entrada = EntradaPokemon("jugador")
#   cada frame: entrada.dibujar(pantalla, imagen_pokemon, pos_final)   # sustituye al dibujo normal del Pokémon
#   cuando entrada.terminada() es True se vuelve al dibujo normal

# ===== TEMA: Modularidad (Clase 10) =====
# Se importan math, os, pygame y el módulo de sonido del juego
import math
import os

import pygame

import sonido

RUTA_POKEBOLA = "assets/ui/pokebola_roja.png"
LADO_FOTOGRAMA = 16                 # cada fotograma de la tira mide 16x16 px

# ===== TEMA: Diccionarios (Clase 11) + Tuplas (Clase 11) =====
# Diccionarios con clave 'ia'/'jugador' y tuplas (x, y) como valores
# Dónde cae la Poké Ball (centro de la bola, en la pantalla virtual 1920x1080) y cuánto se agranda (16 px x escala)
POS_POKEBOLA = {"ia": (1290, 500), "jugador": (640, 770)}
ESCALA_POKEBOLA = {"ia": 5, "jugador": 6}

# Duración de cada fase de la animación, en frames (el juego va a 60 fps)
FRAMES_CAIDA = 40                  # la bola cae desde arriba
FRAMES_REBOTE = 12                  # un saltito al tocar el suelo
FRAMES_TAPA = 5                     # fotograma 1: la tapa empieza a abrirse
FRAMES_LUZ = 5                      # fotograma 5: se abre y sale luz
FRAMES_SALIDA = 30                  # el Pokémon crece hasta su tamaño normal
FRAMES_DESTELLO = 22                # el círculo blanco que se expande
FRAMES_DESVANECER_BOLA = 10         # la esfera blanca se desvanece

F_REBOTE = FRAMES_CAIDA
F_TAPA = F_REBOTE + FRAMES_REBOTE
F_LUZ = F_TAPA + FRAMES_TAPA
F_SALIDA = F_LUZ + FRAMES_LUZ                       # aquí aparece el destello y empieza a salir el Pokémon
F_FIN = F_SALIDA + FRAMES_SALIDA

ALTURA_REBOTE = 40                  # píxeles que salta la bola
RADIO_DESTELLO = 330                # radio final del círculo blanco
ESCALA_INICIAL_POKEMON = 0.10       # tamaño con el que sale (1.0 = tamaño normal)

# ===== TEMA: Diccionarios (Clase 11) + Listas (Clase 11) =====
# Cachés para no cargar ni escalar las mismas imágenes en cada frame
_FOTOGRAMAS = []                    # los 9 fotogramas de la bola, sin escalar
_CACHE_BOLAS = {}                   # (fotograma, escala) -> imagen ya agrandada


# ===== TEMA: Funciones (Clase 7) + Listas (Clase 11) =====
# Carga la tira una sola vez y la corta en fotogramas; si falta el archivo se dibuja una bola sencilla
def _fotogramas():
    if not _FOTOGRAMAS:
        if os.path.exists(RUTA_POKEBOLA):
            tira = pygame.image.load(RUTA_POKEBOLA).convert_alpha()
            for i in range(tira.get_width() // LADO_FOTOGRAMA):
                _FOTOGRAMAS.append(tira.subsurface((i * LADO_FOTOGRAMA, 0, LADO_FOTOGRAMA, LADO_FOTOGRAMA)).copy())
        else:
            # Respaldo: una bola roja y blanca dibujada con círculos
            bola = pygame.Surface((LADO_FOTOGRAMA, LADO_FOTOGRAMA), pygame.SRCALPHA)
            pygame.draw.circle(bola, (40, 40, 50), (8, 8), 8)
            pygame.draw.circle(bola, (235, 235, 240), (8, 8), 7)
            pygame.draw.circle(bola, (230, 60, 45), (8, 8), 7, draw_top_right=True, draw_top_left=True)
            _FOTOGRAMAS.append(bola)
    return _FOTOGRAMAS


# Fotograma de la bola agrandado sin suavizar (es pixel art); si el número no existe se usa el último
def _bola(indice, escala):
    fotogramas = _fotogramas()
    indice = min(indice, len(fotogramas) - 1)
    clave = (indice, escala)
    if clave not in _CACHE_BOLAS:
        _CACHE_BOLAS[clave] = pygame.transform.scale(fotogramas[indice], (LADO_FOTOGRAMA * escala, LADO_FOTOGRAMA * escala))
    return _CACHE_BOLAS[clave]


# ===== TEMA: Funciones (Clase 7) + Expresiones y operadores (Clase 3) =====
# Interpolación lineal: con fraccion=0 devuelve inicio, con fraccion=1 devuelve fin
def _lerp(inicio, fin, fraccion):
    return inicio + (fin - inicio) * fraccion


# ===== TEMA: POO (Clase 16) =====
# Cada entrada guarda en qué frame va; dibujar() hace todo el trabajo
class EntradaPokemon:

    # lado: "ia" o "jugador". retraso: frames que espera antes de empezar (para que no salgan los dos a la vez)
    def __init__(self, lado, retraso=0):
        self.lado = lado
        self.frame = -retraso
        self._cache_pokemon = {}        # tamaño -> imagen del Pokémon ya reducida
        self._cache_blanco = {}         # tamaño -> silueta blanca del Pokémon

    # True cuando la animación ya terminó
    def terminada(self):
        return self.frame >= F_FIN

    # True desde que el Pokémon empieza a salir (la interfaz usa esto para mostrar su caja de vida)
    def salio(self):
        return self.frame >= F_SALIDA

    # ===== TEMA: Condicionales (Clase 4) =====
    # if según la fase: caída, rebote, apertura y salida del Pokémon; cada frame avanza uno
    def dibujar(self, pantalla, imagen_pokemon, pos_final):
        # Mientras espera su turno no se dibuja nada
        if self.frame < 0:
            self.frame += 1
            return
        bola_x, bola_y = POS_POKEBOLA[self.lado]
        escala = ESCALA_POKEBOLA[self.lado]
        frame = self.frame

        # --- Sonidos (si los archivos no existen, simplemente no suenan) ---
        if frame == 0:
            sonido.efecto("efectos/pokebola_caida")
        elif frame == F_SALIDA:
            sonido.efecto("efectos/pokebola_abrir")

        # --- La bola ---
        if frame < F_REBOTE:
            # Cae desde arriba acelerando (progreso al cuadrado) y gira alternando tres fotogramas
            progreso = (frame + 1) / FRAMES_CAIDA
            y = _lerp(-120, bola_y, progreso * progreso)
            fotograma = (0, 7, 6, 7)[(frame // 3) % 4]
        elif frame < F_TAPA:
            # Un saltito al tocar el suelo (media vuelta de seno)
            progreso = (frame - F_REBOTE) / FRAMES_REBOTE
            y = bola_y - ALTURA_REBOTE * math.sin(math.pi * progreso)
            fotograma = 0
        else:
            y = bola_y
            fotograma = 1 if frame < F_LUZ else (5 if frame < F_SALIDA else 2)
        imagen_bola = _bola(fotograma, escala)
        if frame >= F_SALIDA:
            # La esfera blanca se desvanece mientras sale el Pokémon
            alfa = int(255 * max(0.0, 1 - (frame - F_SALIDA) / FRAMES_DESVANECER_BOLA))
            if alfa > 0:
                imagen_bola = imagen_bola.copy()
                imagen_bola.set_alpha(alfa)
                pantalla.blit(imagen_bola, imagen_bola.get_rect(center=(int(bola_x), int(y))))
        else:
            pantalla.blit(imagen_bola, imagen_bola.get_rect(center=(int(bola_x), int(y))))

        # --- El Pokémon sale de la bola creciendo, primero como silueta blanca ---
        if frame >= F_SALIDA:
            self._dibujar_salida(pantalla, imagen_pokemon, pos_final, (bola_x, bola_y), frame - F_SALIDA)

        # --- Destello blanco: un círculo que se expande y se vuelve transparente ---
        if F_SALIDA <= frame < F_SALIDA + FRAMES_DESTELLO:
            progreso = (frame - F_SALIDA) / FRAMES_DESTELLO
            radio = int(_lerp(30, RADIO_DESTELLO, progreso))
            superficie = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(superficie, (255, 255, 255, int(230 * (1 - progreso))), (radio, radio), radio)
            pantalla.blit(superficie, superficie.get_rect(center=(int(bola_x), int(bola_y - 20))))

        self.frame += 1

    # El Pokémon va del tamaño pequeño al normal (salida rápida y frenada al final) y de la bola a su sitio.
    # Empieza como silueta blanca y recupera sus colores
    def _dibujar_salida(self, pantalla, imagen_pokemon, pos_final, bola, frames_salida):
        progreso = min(1.0, frames_salida / FRAMES_SALIDA)
        suave = 1 - (1 - progreso) ** 3
        ancho, alto = imagen_pokemon.get_size()
        escala = _lerp(ESCALA_INICIAL_POKEMON, 1.0, suave)
        tam = (max(2, int(ancho * escala)), max(2, int(alto * escala)))
        # El centro viaja desde la bola hasta el centro final del Pokémon
        centro_final = (pos_final[0] + ancho / 2, pos_final[1] + alto / 2)
        centro = (_lerp(bola[0], centro_final[0], suave), _lerp(bola[1] - 20, centro_final[1], suave))

        if tam not in self._cache_pokemon:
            self._cache_pokemon[tam] = pygame.transform.smoothscale(imagen_pokemon, tam)
            blanco = self._cache_pokemon[tam].copy()
            blanco.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGB_ADD)      # mismo contorno, todo en blanco
            self._cache_blanco[tam] = blanco
        imagen = self._cache_pokemon[tam]
        pantalla.blit(imagen, imagen.get_rect(center=(int(centro[0]), int(centro[1]))))

        # La silueta blanca se desvanece durante el 75 % de la salida
        alfa = int(255 * max(0.0, 1 - progreso / 0.75))
        if alfa > 0:
            blanco = self._cache_blanco[tam]
            blanco.set_alpha(alfa)
            pantalla.blit(blanco, blanco.get_rect(center=(int(centro[0]), int(centro[1]))))