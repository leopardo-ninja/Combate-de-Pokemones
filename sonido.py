# ===== TEMA: Modularidad (Clase 10) =====
# Se importan los módulos os y pygame
import os
import pygame

# ===== TEMA: Pygame (fuera de temario) =====
# Inicia el sistema de sonido
pygame.mixer.init()

# ===== TEMA: Diccionarios (Clase 11) =====
# _EFECTOS y _LOOPS guardan los sonidos ya cargados (clave -> sonido)
# Cachés: efectos cortos ya cargados, canales de los sonidos en bucle y música que suena ahora
_EFECTOS = {}
_LOOPS = {}
_musica_actual = None


# ===== TEMA: Funciones (Clase 7) =====
# Parámetro con valor por defecto (volumen=0.7)
def efecto(nombre, volumen=0.7):

    # Efectos de sonido
    # Primera vez: busca el archivo (.wav u .ogg) y lo carga. Si no existe se guarda None y simplemente no suena
    # ===== TEMA: Condicionales (Clase 4) + Diccionarios (Clase 11) =====
    # Operador 'in' sobre un diccionario
    if nombre not in _EFECTOS:
        _EFECTOS[nombre] = None
        # ===== TEMA: Bucles (Clase 4) + Tuplas (Clase 11) =====
        # for recorriendo una tupla de extensiones
        for extension in (".wav", ".ogg"):
            ruta = f"assets/audio/{nombre}{extension}"
            if os.path.exists(ruta):
                _EFECTOS[nombre] = pygame.mixer.Sound(ruta)
                break
    # Ajusta el volumen y lo reproduce una vez
    if _EFECTOS[nombre]:
        _EFECTOS[nombre].set_volume(volumen)
        _EFECTOS[nombre].play()


# ===== TEMA: Funciones (Clase 7) =====
# Usa 'global' para modificar una variable que está fuera de la función
def musica(nombre, volumen=0.2):

    # Bucle infinito para el sonido ambiente
    global _musica_actual
    # ===== TEMA: Condicionales (Clase 4) =====
    # return anticipado: si ya suena, la función termina
    # Si esa música ya está sonando no se reinicia (esta función se llama en cada frame)
    if nombre == _musica_actual:
        return
    for extension in (".ogg", ".mp3"):
        ruta = f"assets/audio/{nombre}{extension}"
        if os.path.exists(ruta):
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(volumen)
            # -1 = se repite sin fin
            pygame.mixer.music.play(-1)
            _musica_actual = nombre
            return


# ===== TEMA: Funciones (Clase 7) + Diccionarios (Clase 11) =====
# .get() devuelve None si la clave no existe
def loop(nombre, volumen=0.3):

    # Reproduce un sonido en bucle
    # Si ya está sonando en bucle no se vuelve a lanzar
    canal = _LOOPS.get(nombre)
    if canal is not None and canal.get_busy():
        return
    for extension in (".wav", ".ogg"):
        ruta = f"assets/audio/{nombre}{extension}"
        if os.path.exists(ruta):
            sonido_cargado = pygame.mixer.Sound(ruta)
            sonido_cargado.set_volume(volumen)
            # Se guarda el canal para poder detenerlo luego con parar_loop
            _LOOPS[nombre] = sonido_cargado.play(loops=-1)
            return


# ===== TEMA: Funciones (Clase 7) + Diccionarios (Clase 11) =====
# .pop() saca la clave del diccionario y devuelve su valor
# Detiene un sonido en bucle (si estaba sonando)
def parar_loop(nombre):
    canal = _LOOPS.pop(nombre, None)
    if canal is not None:
        canal.stop()


# ===== TEMA: Funciones (Clase 7) =====
# Sin parámetros ni retorno (void): solo produce un efecto
def parar_musica():

    # Pausar reproduccion
    global _musica_actual
    # Baja el volumen poco a poco durante 500 ms antes de parar
    pygame.mixer.music.fadeout(500)
    _musica_actual = None