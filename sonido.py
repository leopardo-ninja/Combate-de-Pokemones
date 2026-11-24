import os
import pygame

pygame.mixer.init()

# Cachés: efectos cortos ya cargados, canales de los sonidos en bucle y música que suena ahora
_EFECTOS = {}
_LOOPS = {}
_musica_actual = None


def efecto(nombre, volumen=0.7):

    # Efectos de sonido
    # Primera vez: busca el archivo (.wav u .ogg) y lo carga. Si no existe se guarda None y simplemente no suena
    if nombre not in _EFECTOS:
        _EFECTOS[nombre] = None
        for extension in (".wav", ".ogg"):
            ruta = f"assets/audio/{nombre}{extension}"
            if os.path.exists(ruta):
                _EFECTOS[nombre] = pygame.mixer.Sound(ruta)
                break
    # Ajusta el volumen y lo reproduce una vez
    if _EFECTOS[nombre]:
        _EFECTOS[nombre].set_volume(volumen)
        _EFECTOS[nombre].play()


def musica(nombre, volumen=0.2):

    # Bucle infinito para el sonido ambiente
    global _musica_actual
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


# Detiene un sonido en bucle (si estaba sonando)
def parar_loop(nombre):
    canal = _LOOPS.pop(nombre, None)
    if canal is not None:
        canal.stop()


def parar_musica():

    # Pausar reproduccion
    global _musica_actual
    # Baja el volumen poco a poco durante 500 ms antes de parar
    pygame.mixer.music.fadeout(500)
    _musica_actual = None