import os
import pygame

pygame.mixer.init()

_EFECTOS = {}
_LOOPS = {}
_musica_actual = None


def efecto(nombre, volumen=0.7):

    # Efectos de sonido
    if nombre not in _EFECTOS:
        _EFECTOS[nombre] = None
        for ext in (".wav", ".ogg"):
            ruta = f"assets/audio/{nombre}{ext}"
            if os.path.exists(ruta):
                _EFECTOS[nombre] = pygame.mixer.Sound(ruta)
                break
    if _EFECTOS[nombre]:
        _EFECTOS[nombre].set_volume(volumen)
        _EFECTOS[nombre].play()


def musica(nombre, volumen=0.2):

    # Bucle infinito para el sonido ambiente
    global _musica_actual
    if nombre == _musica_actual:
        return
    for ext in (".ogg", ".mp3"):
        ruta = f"assets/audio/{nombre}{ext}"
        if os.path.exists(ruta):
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(volumen)
            pygame.mixer.music.play(-1)
            _musica_actual = nombre
            return


def loop(nombre, volumen=0.3):

    # Reproduce un sonido en bucle
    canal = _LOOPS.get(nombre)
    if canal is not None and canal.get_busy():
        return
    for ext in (".wav", ".ogg"):
        ruta = f"assets/audio/{nombre}{ext}"
        if os.path.exists(ruta):
            snd = pygame.mixer.Sound(ruta)
            snd.set_volume(volumen)
            _LOOPS[nombre] = snd.play(loops=-1)
            return


def parar_loop(nombre):
    canal = _LOOPS.pop(nombre, None)
    if canal is not None:
        canal.stop()


def parar_musica():

    # Pausar reproduccion
    global _musica_actual
    pygame.mixer.music.fadeout(500)
    _musica_actual = None