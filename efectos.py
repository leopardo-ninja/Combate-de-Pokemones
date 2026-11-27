# ----------------- EFECTOS VISUALES DE LAS HABILIDADES -----------------
# Usa las imágenes recortadas en assets/efectos/ (ver recortar_efectos.py).
#   assets/efectos/ataque/aNNN.png  -> imágenes sueltas de ataques
#   assets/efectos/stats/<stat>.png -> baldosas de subida/bajada de estadísticas
#
# Uso desde la interfaz:
#   gestor = GestorEfectos()
#   gestor.lanzar("jugador", "Lanzallamas", "Fuego", al_impactar=funcion)
#   cada frame: gestor.actualizar(); gestor.dibujar_fondo(...); gestor.dibujar(...)

# ===== TEMA: Modularidad (Clase 10) =====
# Se importan math, os, random y pygame
import math
import os
import random

import pygame

RUTA_EFECTOS = "assets/efectos"

# ===== TEMA: Diccionarios (Clase 11) + Tuplas (Clase 11) =====
# Diccionarios con clave 'ia'/'jugador' y tuplas (x, y) como valores
# Centro de cada Pokémon en la pantalla virtual 1920x1080
CENTRO = {"ia": (1280, 410), "jugador": (640, 690)}
# Punto de la cara (de donde salen los chorros y adonde llegan)
CARA = {"ia": (1250, 360), "jugador": (700, 590)}

# ===== TEMA: Diccionarios (Clase 11) =====
# Diccionarios que guardan imágenes ya cargadas, escaladas y teñidas
# Cachés para no cargar ni escalar las mismas imágenes en cada frame: originales, escaladas y teñidas
_CACHE = {}
_CACHE_ESCALADAS = {}
_CACHE_TINTADAS = {}


# ===== TEMA: Funciones (Clase 7) + Diccionarios (Clase 11) =====
# La tupla (grupo, nombre) es la clave de la caché; retorna la imagen o None
# Carga assets/efectos/<grupo>/<nombre>.png (o None si no existe) y la guarda en caché
def _cargar(grupo, nombre):
    clave = (grupo, nombre)
    if clave not in _CACHE:
        ruta = f"{RUTA_EFECTOS}/{grupo}/{nombre}.png"
        _CACHE[clave] = pygame.image.load(ruta).convert_alpha() if os.path.exists(ruta) else None
    return _CACHE[clave]


# ===== TEMA: Funciones (Clase 7) + Modularidad (Clase 10) =====
# Una función que reutiliza a otra (_cargar)
# Carga la imagen de un ataque: n puede ser un número (a001, a002...) o el nombre de un archivo
def cargar_pokemon_ataque(n):
    return _cargar("ataque", n if isinstance(n, str) else f"a{n:03d}")


# ===== TEMA: Funciones (Clase 7) =====
# Usa max() e int(); guarda el resultado en el diccionario de caché
# Agranda la imagen por un factor (sin suavizar, es pixel art) y recuerda el resultado
def _escalar_con_cache(superficie, factor):
    clave = (id(superficie), round(factor, 2))
    if clave not in _CACHE_ESCALADAS:
        ancho, alto = superficie.get_size()
        _CACHE_ESCALADAS[clave] = pygame.transform.scale(superficie, (max(1, int(ancho * factor)), max(1, int(alto * factor))))
    return _CACHE_ESCALADAS[clave]


# ===== TEMA: Funciones (Clase 7) + Tuplas (Clase 11) =====
# tuple(...) crea una tupla nueva con los colores aclarados
def _tintar(img, tinte):
    """Devuelve una copia de img con sus colores multiplicados por 'tinte' (r, g, b). Se guarda en caché."""
    clave = (id(img), tinte)
    if clave not in _CACHE_TINTADAS:
        copia = img.copy()
        copia.fill(tinte, special_flags=pygame.BLEND_RGB_MULT)
        brillo = tuple(int(c * 0.35) for c in tinte)       # aclara un poco para que el color no quede apagado
        copia.fill(brillo, special_flags=pygame.BLEND_RGB_ADD)
        _CACHE_TINTADAS[clave] = copia
    return _CACHE_TINTADAS[clave]


# ===== TEMA: Funciones (Clase 7) + Expresiones y operadores (Clase 3) =====
# Fórmula aritmética pura: retorna un valor entre inicio y fin
# Interpolación lineal: con fraccion=0 devuelve inicio, con fraccion=1 devuelve fin y en medio, un punto intermedio
def _lerp(inicio, fin, fraccion):
    return inicio + (fin - inicio) * fraccion


# ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) =====
# Expresión condicional en una línea que retorna 'ia' o 'jugador'
# Devuelve el otro bando: "ia" <-> "jugador"
def _oponente(lado):
    return "ia" if lado == "jugador" else "jugador"


# ===== TEMA: POO (Clase 16) =====
# Cada efecto visual es una clase con constructor (__init__) y método dibujar; todas comparten la misma interfaz
# ----------------- ELEMENTOS ANIMADOS -----------------
# Elemento animado básico: una imagen (o varios fotogramas) que se mueve, crece, rota y se desvanece
class Particula:
    """Una imagen (o varios fotogramas) que viaja de 'desde' a 'hasta'."""

    def __init__(self, ids_pokemons, frame_inicio, duracion, desde, hasta, escala=5, escala_fin=None, altura_arco=0, frames_por_cuadro=4,
                 alpha_fin=255, angulo=0, giro_por_frame=0, aditivo=False, amplitud_temblor=0, ida_vuelta=False, tinte=None):
        self.frames = [s for s in (cargar_pokemon_ataque(i) for i in ids_pokemons) if s is not None]
        self.tinte = tinte          # (r, g, b) para cambiar el color de la imagen, ej. (255, 70, 50) = rojo
        self.frame_inicio, self.duracion = frame_inicio, duracion
        self.desde, self.hasta = desde, hasta
        self.escala, self.escala_fin = escala, escala if escala_fin is None else escala_fin
        self.altura_arco, self.frames_por_cuadro = altura_arco, frames_por_cuadro
        self.alpha_fin, self.angulo, self.giro_por_frame = alpha_fin, angulo, giro_por_frame
        self.aditivo, self.amplitud_temblor, self.ida_vuelta = aditivo, amplitud_temblor, ida_vuelta
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        # Fuera de su ventana de tiempo (o sin imágenes) no se dibuja nada
        if not self.frames or frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        frames_transcurridos = frame_actual - self.frame_inicio
        # ===== TEMA: Expresiones y operadores (Clase 3) + Condicionales (Clase 4) =====
        # Operadores aritméticos y expresión condicional en una línea (ida_vuelta)
        # progreso va de 0 (al empezar) a 1 (al terminar); con ida_vuelta sube hasta 1 y vuelve a 0
        progreso = frames_transcurridos / self.duracion
        progreso_ajustado = 1 - abs(2 * progreso - 1) if self.ida_vuelta else progreso
        # Posición actual: punto intermedio entre origen y destino, con un arco hacia arriba si altura_arco > 0
        x = _lerp(self.desde[0], self.hasta[0], progreso_ajustado)
        y = _lerp(self.desde[1], self.hasta[1], progreso_ajustado) - self.altura_arco * 4 * progreso_ajustado * (1 - progreso_ajustado)
        # Temblor aleatorio de la posición (usado en la electricidad)
        if self.amplitud_temblor:
            x += random.randint(-self.amplitud_temblor, self.amplitud_temblor)
            y += random.randint(-self.amplitud_temblor, self.amplitud_temblor)
        # Fotograma actual (cambia cada frames_por_cuadro) con la escala que va de escala a escala_fin
        img = _escalar_con_cache(self.frames[(frames_transcurridos // self.frames_por_cuadro) % len(self.frames)], _lerp(self.escala, self.escala_fin, progreso))
        # Cambia el color de la imagen
        if self.tinte:
            img = _tintar(img, self.tinte)
        # Rotación: ángulo inicial más el giro acumulado en cada frame
        angulo_actual = self.angulo + self.giro_por_frame * frames_transcurridos
        if angulo_actual:
            img = pygame.transform.rotate(img, angulo_actual)
        # Transparencia: se desvanece de 255 (opaco) hasta alpha_fin
        alpha = int(_lerp(255, self.alpha_fin, progreso))
        if alpha < 255:
            img = img.copy()
            img.set_alpha(alpha)
        # Modo aditivo: suma los colores con el fondo (efecto de brillo)
        modo_mezcla = pygame.BLEND_RGB_ADD if self.aditivo else 0
        pantalla.blit(img, img.get_rect(center=(int(x), int(y))), special_flags=modo_mezcla)


# ===== TEMA: POO (Clase 16) =====
# Clase Chorro: atributos en __init__ y método dibujar
class Chorro:
    """Chorro fijo: sale de 'desde', se estira hasta 'hasta' y solo cambia de fotograma.
    La imagen es vertical con la cresta arriba; la cresta queda en el extremo del rival."""

    def __init__(self, ids_pokemons, desde, hasta, frame_inicio, duracion, ancho=6, frames_por_cuadro=3, frames_crecimiento=4):
        self.frames = [s for s in (cargar_pokemon_ataque(i) for i in ids_pokemons) if s is not None]
        self.desde, self.hasta, self.frame_inicio, self.duracion = desde, hasta, frame_inicio, duracion
        self.ancho, self.frames_por_cuadro, self.frames_crecimiento = ancho, frames_por_cuadro, frames_crecimiento
        self.frame_fin = frame_inicio + duracion
        self._cache = {}

    def dibujar(self, pantalla, frame_actual):
        if not self.frames or frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        frames_transcurridos = frame_actual - self.frame_inicio
        dx, dy = self.hasta[0] - self.desde[0], self.hasta[1] - self.desde[1]
        fraccion_extendida = min(1.0, (frames_transcurridos + 1) / self.frames_crecimiento)               # sale rápido y luego queda fijo
        largo = max(4, int(math.hypot(dx, dy) * fraccion_extendida))
        idx = (frames_transcurridos // self.frames_por_cuadro) % len(self.frames)
        # Se guarda en caché la imagen estirada y girada hacia el rival para cada fotograma y largo
        clave = (idx, largo)
        if clave not in self._cache:
            base = self.frames[idx]
            superficie_escalada = pygame.transform.scale(base, (base.get_width() * self.ancho, largo))
            self._cache[clave] = pygame.transform.rotate(superficie_escalada, math.degrees(math.atan2(-dx, -dy)))
        img = self._cache[clave]
        # El chorro se dibuja centrado entre su origen y su punta actual
        centro = (self.desde[0] + dx * fraccion_extendida / 2, self.desde[1] + dy * fraccion_extendida / 2)
        pantalla.blit(img, img.get_rect(center=(int(centro[0]), int(centro[1]))))


# ===== TEMA: POO (Clase 16) =====
# Clase Anillo: atributos en __init__ y método dibujar
class Anillo:
    """Círculo que se expande (ondas, pulsos)."""

    def __init__(self, centro, frame_inicio, duracion, radio_inicial, radio_final, color, grosor=10):
        self.centro, self.frame_inicio, self.duracion, self.radio_inicial, self.radio_final = centro, frame_inicio, duracion, radio_inicial, radio_final
        self.color, self.grosor = color, grosor
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        # El radio crece con el tiempo; el color pierde opacidad hasta desaparecer
        radio = int(_lerp(self.radio_inicial, self.radio_final, progreso))
        lado = radio * 2 + self.grosor * 2
        superficie = pygame.Surface((lado, lado), pygame.SRCALPHA)
        pygame.draw.circle(superficie, (*self.color, int(255 * (1 - progreso))), (lado // 2, lado // 2), radio, self.grosor)
        pantalla.blit(superficie, superficie.get_rect(center=self.centro))


# ===== TEMA: POO (Clase 16) =====
# Clase Tajo: atributos en __init__ y método dibujar
class Tajo:
    """Tres arañazos diagonales (Arañazo, Mordisco...)."""

    def __init__(self, centro, frame_inicio, duracion=18, color=(255, 255, 255), largo=170):
        self.centro, self.frame_inicio, self.duracion, self.color, self.largo = centro, frame_inicio, duracion, color, largo
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        # Los arañazos se trazan en el primer 40% de la animación y luego solo se adelgazan
        crecer = min(1.0, progreso * 2.5)
        # ===== TEMA: Bucles (Clase 4) =====
        # for/range dibuja los 3 arañazos
        for i in range(3):
            desfase_x = (i - 1) * 46
            x0, y0 = self.centro[0] + desfase_x - self.largo // 3, self.centro[1] - self.largo // 2 + i * 8
            x1 = x0 + int(self.largo * 0.55 * crecer)
            y1 = y0 + int(self.largo * crecer)
            ancho = max(2, int(10 * (1 - progreso)))
            pygame.draw.line(pantalla, self.color, (x0, y0), (x1, y1), ancho)


# ===== TEMA: POO (Clase 16) =====
# Clase Haz: atributos en __init__ y método dibujar
class Haz:
    """Rayo continuo entre dos puntos (Rayo Solar, Electrocañón...)."""

    def __init__(self, desde, hasta, frame_inicio, duracion, color=(255, 240, 120), grosor=60):
        self.desde, self.hasta, self.frame_inicio, self.duracion = desde, hasta, frame_inicio, duracion
        self.color, self.grosor = color, grosor
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        progreso_extension = min(1.0, progreso * 4)
        progreso_apagado = min(1.0, (1 - progreso) * 4)
        # La punta del rayo avanza rápido (primer cuarto) y el grosor se apaga al final con una ligera vibración
        punta = (_lerp(self.desde[0], self.hasta[0], progreso_extension), _lerp(self.desde[1], self.hasta[1], progreso_extension))
        grosor_actual = max(2, int(self.grosor * progreso_apagado * (0.85 + 0.15 * math.sin(frame_actual * 1.3))))
        pygame.draw.line(pantalla, self.color, self.desde, punta, grosor_actual)
        pygame.draw.line(pantalla, (255, 255, 255), self.desde, punta, max(2, grosor_actual // 2))


# ===== TEMA: POO (Clase 16) =====
# Clase Ola: atributos en __init__ y método dibujar
class Ola:
    """Ola de agua que cruza la pantalla (Surf)."""

    def __init__(self, frame_inicio, duracion, y0=330, y1=900):
        self.frame_inicio, self.duracion, self.y0, self.y1 = frame_inicio, duracion, y0, y1
        self.frame_fin = frame_inicio + duracion
        self._superficie = None

    def dibujar(self, pantalla, frame_actual):
        if frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        ancho = pantalla.get_width()
        # frente: posición x del borde delantero de la ola, que cruza la pantalla
        frente = int(_lerp(-200, ancho + 300, progreso))
        if self._superficie is None:
            self._superficie = pygame.Surface((ancho, self.y1 - self.y0), pygame.SRCALPHA)
        superficie = self._superficie
        superficie.fill((0, 0, 0, 0))
        alto_ola = self.y1 - self.y0
        # Polígono azul cuyo borde derecho ondula con un seno; encima van círculos blancos de espuma
        puntos = [(0, 0)]
        # ===== TEMA: Bucles (Clase 4) + Listas (Clase 11) =====
        # range con paso 20; append agrega puntos (tuplas) a la lista del polígono
        for y_ola in range(0, alto_ola + 1, 20):
            puntos.append((frente + int(40 * math.sin(y_ola / 28 + frame_actual / 4)), y_ola))
        puntos.append((0, alto_ola))
        pygame.draw.polygon(superficie, (50, 130, 235, 170), puntos)
        for y_ola in range(0, alto_ola, 20):
            x_ola = frente + int(40 * math.sin(y_ola / 28 + frame_actual / 4))
            pygame.draw.circle(superficie, (235, 245, 255, 230), (x_ola, y_ola), 14)
        pantalla.blit(superficie, (0, self.y0))


# ===== TEMA: POO (Clase 16) =====
# Clase Flash: atributos en __init__ y método dibujar
class Flash:
    """Destello de pantalla completa."""

    def __init__(self, frame_inicio, duracion, color=(255, 255, 255), alpha_maximo=200):
        self.frame_inicio, self.duracion, self.color, self.alpha_maximo = frame_inicio, duracion, color, alpha_maximo
        self.frame_fin = frame_inicio + duracion
        self._superficie = None

    def dibujar(self, pantalla, frame_actual):
        if frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        # Superficie del color del destello; su opacidad baja con el tiempo
        if self._superficie is None or self._superficie.get_size() != pantalla.get_size():
            self._superficie = pygame.Surface(pantalla.get_size())
            self._superficie.fill(self.color)
        self._superficie.set_alpha(int(self.alpha_maximo * (1 - progreso)))
        pantalla.blit(self._superficie, (0, 0))


# ===== TEMA: POO (Clase 16) =====
# Clase Orbita: atributos en __init__ y método dibujar
class Orbita:
    """Imágenes girando alrededor de un punto (Giro Fuego). Si se da centro_final, el anillo viaja
    desde 'centro' hasta 'centro_final' mientras gira (Llamarada)."""

    def __init__(self, ids_pokemons, centro, frame_inicio, duracion, cantidad=8, radio_inicial=260, radio_final=40, escala=4, vueltas=2.0, centro_final=None):
        self.frames = [s for s in (cargar_pokemon_ataque(i) for i in ids_pokemons) if s is not None]
        self.centro, self.frame_inicio, self.duracion, self.cantidad = centro, frame_inicio, duracion, cantidad
        self.centro_final = centro if centro_final is None else centro_final
        self.radio_inicial, self.radio_final, self.escala, self.vueltas = radio_inicial, radio_final, escala, vueltas
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if not self.frames or frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        radio = _lerp(self.radio_inicial, self.radio_final, progreso)
        # ===== TEMA: Bucles (Clase 4) =====
        # for/range coloca cada imagen en su ángulo
        for i in range(self.cantidad):
            # Cada imagen ocupa un ángulo propio y todas giran 'vueltas' veces. El 0.7 aplasta el círculo para dar perspectiva
            angulo = 2 * math.pi * (i / self.cantidad + self.vueltas * progreso)
            img = _escalar_con_cache(self.frames[(frame_actual // 4 + i) % len(self.frames)], self.escala)
            centro_x = _lerp(self.centro[0], self.centro_final[0], progreso)
            centro_y = _lerp(self.centro[1], self.centro_final[1], progreso)
            pos = (centro_x + radio * math.cos(angulo), centro_y + radio * math.sin(angulo) * 0.7)
            pantalla.blit(img, img.get_rect(center=(int(pos[0]), int(pos[1]))))


# ===== TEMA: POO (Clase 16) =====
# Clase RayoDescendente: atributos en __init__ y método dibujar
class RayoDescendente:
    # Rayo que se dibuja de arriba hacia abajo, se mantiene y se borra de arriba hacia abajo

    def __init__(self, id_pokemon, base, frame_inicio, duracion, escala=6, frames_crecer=5, frames_borrar=6, amplitud_temblor=0, estiramiento=1.0):
        self.pokemon = cargar_pokemon_ataque(id_pokemon)
        self.estiramiento, self._img = estiramiento, None                   # estiramiento > 1 alarga solo en vertical
        self.base, self.frame_inicio, self.duracion, self.escala = base, frame_inicio, duracion, escala
        self.frames_crecer, self.frames_borrar, self.amplitud_temblor = frames_crecer, frames_borrar, amplitud_temblor
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if self.pokemon is None or frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        if self._img is None:
            ancho_original, alto_original = self.pokemon.get_size()
            self._img = pygame.transform.scale(self.pokemon, (max(1, int(ancho_original * self.escala)), max(1, int(alto_original * self.escala * self.estiramiento))))
        img = self._img
        ancho, alto = img.get_size()
        frames_transcurridos = frame_actual - self.frame_inicio
        fila_desde, fila_hasta = 0, alto                                   # filas visibles de la imagen
        if frames_transcurridos < self.frames_crecer:                      # se dibuja de arriba hacia abajo
            fila_hasta = math.ceil(alto * (frames_transcurridos + 1) / self.frames_crecer)
        elif frames_transcurridos >= self.duracion - self.frames_borrar:   # se borra de arriba hacia abajo
            paso = frames_transcurridos - (self.duracion - self.frames_borrar)
            fila_desde = int(alto * (paso + 1) / self.frames_borrar)
        if fila_desde >= fila_hasta:
            return
        x = self.base[0] - ancho // 2 + (random.randint(-self.amplitud_temblor, self.amplitud_temblor) if self.amplitud_temblor else 0)
        y = self.base[1] - alto
        pantalla.blit(img, (x, y + fila_desde), area=pygame.Rect(0, fila_desde, ancho, fila_hasta - fila_desde))


# ===== TEMA: Funciones (Clase 7) + Diccionarios (Clase 11) =====
# Las funciones constructoras retornan un diccionario que describe el ataque
# Funciones que arman los elementos de cada ataque. Devuelven un diccionario con:
# elementos (lo que se dibuja), impacto (frame del golpe, donde se aplica el daño) y opciones (sacude, embestida, tile...)
# ----------------- CONSTRUCTORES DE EFECTOS -----------------
# ===== TEMA: Funciones (Clase 7) =====
# Parámetros con valor por defecto; retorna un objeto Particula
# Destello de impacto fijo sobre destino que crece y se desvanece (spread lo mueve un poco al azar)
def _impacto(destino, ids_pokemons, frame_inicio, escala=6, escala_fin=None, duracion=16, spread=0):
    pos = (destino[0] + random.randint(-spread, spread), destino[1] + random.randint(-spread, spread))
    return Particula(ids_pokemons, frame_inicio, duracion, pos, pos, escala=escala, escala_fin=escala_fin or escala * 1.4, frames_por_cuadro=4, alpha_fin=0)


# ===== TEMA: Funciones (Clase 7) + Listas (Clase 11) =====
# Muchos parámetros con valor por defecto; la lista elementos crece con append y +=
# Ataque a distancia: lanza 'cantidad' proyectiles de origen a destino y un efecto de impacto al llegar cada uno
def proyectil(origen, destino, ids_proyectil, cantidad=1, escala=5, duracion=24, separacion_frames=4, altura_arco=0, frames_por_cuadro=4, ids_impacto=(233,), escala_impacto=6,
              spread=0, aditivo=False, giro_por_frame=0, ida_vuelta=False, sacude=0, extra=None):
    elementos = []
    # Cada proyectil sale separacion_frames después del anterior y cae en un punto algo disperso
    # ===== TEMA: Bucles (Clase 4) =====
    # for/range crea un proyectil por cada repetición
    for k in range(cantidad):
        variacion = random.randint(-spread, spread) if spread else 0
        hasta = (destino[0] + variacion, destino[1] + variacion // 2)
        elementos.append(Particula(ids_proyectil, k * separacion_frames, duracion, origen, hasta, escala=escala, altura_arco=altura_arco, frames_por_cuadro=frames_por_cuadro,
                            aditivo=aditivo, giro_por_frame=giro_por_frame, ida_vuelta=ida_vuelta))
        if ids_impacto:
            elementos.append(_impacto(hasta, ids_impacto, k * separacion_frames + (duracion // 2 if ida_vuelta else duracion), escala=escala_impacto))
    elementos += extra or []
    # Con ida_vuelta (bumerán) el golpe ocurre a mitad del recorrido
    return {"elementos": elementos, "impacto": duracion // 2 if ida_vuelta else duracion, "sacude": sacude}


# ===== TEMA: Funciones (Clase 7) =====
# Retorna un diccionario con los elementos y las opciones del ataque
# Ataque cuerpo a cuerpo: el atacante embiste y el golpe aparece sobre el rival en frame_impacto
def contacto(origen, destino, golpe, escala=7, embestida=True, sacude=8, extra=None, frame_impacto=12):
    elementos = [_impacto(destino, golpe, frame_impacto, escala=escala, duracion=16)]
    elementos += extra or []
    return {"elementos": elementos, "impacto": frame_impacto, "embestida": embestida, "sacude": sacude}


# ===== TEMA: Funciones (Clase 7) =====
# Retorna un diccionario con la baldosa de estadística
# Habilidad de Estado: no hace daño, muestra una baldosa de estadística (sube o baja) sobre un Pokémon
def estado(sobre, tile, sube, extra=None, duracion=70):
    return {"elementos": extra or [], "impacto": 10, "tile": (sobre, tile, sube, duracion)}


# ===== TEMA: Condicionales (Clase 4) + Modularidad (Clase 10) =====
# construir() es una cadena de if según el nombre de la habilidad; reutiliza proyectil, contacto y estado
# ----------------- Recrear cada habilidad -----------------
# Recibe el nombre y tipo de la habilidad y quién la usa, y devuelve el efecto correspondiente.
# Está ordenada por tipo y al final hay un efecto genérico de respaldo
def construir(nombre, tipo, atacante):
    # origen = centro del atacante, destino = centro del rival
    origen, destino = CENTRO[atacante], CENTRO[_oponente(atacante)]
    rival = _oponente(atacante)
    # 1 si el rival está a la derecha del atacante, -1 si está a la izquierda
    direccion_x = 1 if destino[0] > origen[0] else -1
    punto_salida = (origen[0] + direccion_x * 120, origen[1] - 20)          # salida del proyectil (de cara al rival)

    # ===== TEMA: Funciones (Clase 7) =====
    # Función definida dentro de otra función
    # Atajo para crear la baldosa de una habilidad de Estado
    def tile(sobre, nombre_tile, sube, extra=None):
        return estado(sobre, nombre_tile, sube, extra)

    # ===== TEMA: Condicionales (Clase 4) + Tuplas (Clase 11) =====
    # if nombre in (...): operador in sobre tuplas; return anticipado
    # ---------- NORMAL ----------
    # Ataques de contacto: el atacante embiste y el rival se sacude
    if nombre in ("Placaje", "Tacleada", "Constricción"):
        return contacto(origen, destino, (), sacude=10)
    if nombre in ("Patada",):
        return contacto(origen, destino, (), sacude=12)
    if nombre in ("Arañazo", "Acuchillar") and tipo != "Estado":
        return contacto(origen, destino, (), extra=[Tajo(destino, 6)], sacude=6)
    if nombre == "Ataque Rápido":
        # El atacante se mueve rápido de izquierda a derecha y, al terminar, estalla la estrella en el rival
        fin = 26
        return {"elementos": [_impacto(destino, (98,), fin, escala=1, escala_fin=2, duracion=16)],
                "impacto": fin, "vaiven": (42, fin), "sacude": 8}
    if nombre == "Rapidez":
        return proyectil(origen, destino, (145, 144), escala=3, duracion=12, ids_impacto=(), sacude=6)
    if nombre == "Mordisco":
        return contacto(origen, destino, (), extra=[Particula((142,), 4, 18, destino, destino, escala=2.5, escala_fin=3)], sacude=10)
    if nombre in ("Puño Certero",):
        return contacto(origen, destino, (), extra=[Particula((189,), 4, 14, destino, destino, escala=3, escala_fin=4)], sacude=12)
    if nombre == "Bofetón":
        return contacto(origen, destino, (), extra=[Particula((192,), 4, 14, (destino[0] - 90, destino[1]), (destino[0] + 90, destino[1]), escala=7)])
    if nombre == "Látigo":
        return contacto(origen, destino, (), embestida=False, extra=[Particula((50, 51, 52), 2, 16, punto_salida, destino, escala=3, frames_por_cuadro=3)])
    if nombre == "Hueso Palo":
        return proyectil(origen, destino, (80,), escala=3, duracion=22, giro_por_frame=28, ids_impacto=(), sacude=8)
    if nombre in ("Derribo", "Golpe Cuerpo", "Doble Filo", "Hipercolmillo"):
        sacudida = 14 if nombre in ("Doble Filo", "Derribo") else 10
        extra = [Particula((142,), 4, 18, destino, destino, escala=2.5, escala_fin=3)] if nombre == "Hipercolmillo" else None
        return contacto(origen, destino, (), sacude=sacudida, extra=extra)
    if nombre in ("Cuchillada", "Tijera X", "Megacuerno"):
        color_tajo = (165, 215, 70) if nombre == "Tijera X" else ((220, 220, 235) if nombre == "Cuchillada" else (210, 140, 255))
        largo_tajo = 195 if nombre == "Megacuerno" else 170
        return contacto(origen, destino, (), extra=[Tajo(destino, 6, color=color_tajo, largo=largo_tajo)], sacude=11)
    if nombre in ("Picotazo", "Picotazo Veneno"):
        tinte_pico = (180, 85, 220) if nombre == "Picotazo Veneno" else None
        return contacto(origen, destino, (), sacude=8,
                        extra=[Particula((145,), 3, 14, punto_salida, destino, escala=3, tinte=tinte_pico)])
    if nombre == "Hiperrayo":
        return {"elementos": [Orbita((101, 145), origen, 0, 24, cantidad=8, radio_inicial=150, radio_final=15, escala=3, vueltas=1.0),
                              Flash(24, 18, (255, 245, 200), 150),
                              Haz(punto_salida, destino, 24, 30, (255, 210, 90), 85)],
                "impacto": 26, "sacude": 16}

    # ---------- FUEGO ----------
    # Ráfaga de 9 llamas con algo de dispersión
    if nombre == "Lanzallamas":
        return proyectil(punto_salida, destino, (38, 39, 40), cantidad=9, escala=4, duracion=22, separacion_frames=3, spread=24, ids_impacto=(43,), escala_impacto=3, aditivo=False)

    if nombre == "Ascuas":
        return proyectil(punto_salida, destino, (57, 58, 38), cantidad=6, escala=4, duracion=22, separacion_frames=5, spread=40, ids_impacto=(58,), escala_impacto=5)

    # Anillo de llamas girando que se cierra sobre el rival
    if nombre == "Giro Fuego":
        return {"elementos": [Orbita((38, 39, 40), destino, 0, 40, cantidad=8, radio_inicial=260, radio_final=30, escala=4), Flash(40, 10, (255, 150, 60), 90)], "impacto": 40, "sacude": 6}

    if nombre == "Colmillo Ígneo":
        return contacto(origen, destino, (43,), escala=3, extra=[Particula((142,), 4, 18, destino, destino, escala=2.5, escala_fin=3), _impacto(destino, (46,), 14, escala=6)], sacude=10)

    if nombre == "Rueda Fuego":
        return proyectil(punto_salida, destino, (39, 40), cantidad=1, escala=7, duracion=26, altura_arco=120, ids_impacto=(46, 47), escala_impacto=6, giro_por_frame=0, sacude=10, extra=
                         [Particula((58,), 2, 24, punto_salida, destino, escala=4, altura_arco=120, alpha_fin=0)])

    if nombre == "Nitrocarga":
        return contacto(origen, destino, (46, 47), escala=2, sacude=12, extra=[Particula((23,), 0, 12, origen, destino, escala=2)])

    if nombre == "Envite Ígneo":
        return contacto(origen, destino, (44, 44), escala=5, sacude=3, extra=[Particula((23,), 0, 14, origen, destino, escala=3), Flash(12, 14, (255, 180, 80), 120)], frame_impacto=12)

    if nombre == "Puño Fuego":
        return contacto(origen, destino, (46,), escala=3, sacude=12, extra=[Particula((189,), 4, 14, destino, destino, escala=2, escala_fin=3, tinte=(255, 70, 50)), _impacto(destino, (43,), 12, escala=2.5)])

    if nombre == "Llamarada":
        # Círculo de fuego (el mismo anillo de Giro Fuego) que viaja desde el atacante hasta el rival
        llegada = 30
        return {"elementos": [Orbita((38, 39, 40), punto_salida, 0, llegada, cantidad=12, radio_inicial=80, radio_final=130, escala=4, vueltas=1.5, centro_final=destino), _impacto(destino, (44, 45), llegada, escala=5, escala_fin=4, duracion=18),
                              Flash(llegada, 12, (255, 140, 50), 110)], "impacto": llegada, "sacude": 16}

    # ---------- AGUA ----------
    if nombre == "Pistola Agua":
        # Chorro con los fotogramas de la hoja: pistola0..3 en vuelo y pistola4 al impactar.
        # La imagen apunta hacia arriba-derecha; cuando dispara el rival se gira 180 grados.
        giro = 0 if atacante == "jugador" else 180
        en_vuelo = tuple(f"pistola{i}" for i in range(4))
        elementos = [Particula(en_vuelo, k * 5, 16, punto_salida, destino, escala=3, frames_por_cuadro=3, angulo=giro) for k in range(3)]
        elementos.append(Particula(("pistola4",), 16, 18, destino, destino, escala=3, escala_fin=4, angulo=giro, alpha_fin=0))
        return {"elementos": elementos, "impacto": 16, "sacude": 6}
    if nombre == "Burbuja":
        return proyectil(punto_salida, destino, (22, 19, 112, 18), cantidad=6, escala=3, duracion=34, separacion_frames=6, altura_arco=40, spread=40, ids_impacto=(9,), escala_impacto=3, frames_por_cuadro=8)
    if nombre == "Rayos Burbuja":
        return proyectil(punto_salida, destino, (112, 22, 113), cantidad=10, escala=2.5, duracion=26, separacion_frames=3, spread=60, ids_impacto=(9,), escala_impacto=3, frames_por_cuadro=6)
    if nombre == "Hidrobomba":
        # Chorro fijo desde la cara del atacante hasta el rival; solo cambian los 4 fotogramas
        fotogramas_hidro = ("hidro0", "hidro1", "hidro2", "hidro3")
        return {"elementos": [Chorro(fotogramas_hidro, CARA[atacante], CARA[rival], 0, 46, ancho=8, frames_por_cuadro=3)],
                "impacto": 8, "sacude": 10, "sacude_duracion": 36}
    if nombre == "Surf":
        # Ola animada con los 14 fotogramas de la hoja (surf00..surf13): viaja del atacante al rival creciendo
        olas = tuple(f"surf{i:02d}" for i in range(14))
        desde = (origen[0], origen[1] + 20)
        hasta = (destino[0], destino[1] + 20)
        return {"elementos": [Particula(olas, 0, 42, desde, hasta, escala=3, escala_fin=5, frames_por_cuadro=3),
                              _impacto(destino, (7, 6), 36, escala=6, duracion=20)],
                "impacto": 36, "sacude": 8}
    if nombre == "Hidropulso":
        return {"elementos": [Anillo(origen, 0, 24, 20, 200, (150, 210, 255), 12), Anillo(origen, 6, 24, 20, 200, (90, 160, 255), 10),
                       Particula((18, 19), 20, 26, punto_salida, destino, escala=5, frames_por_cuadro=6), Anillo(destino, 46, 22, 20, 160, (180, 230, 255), 12)],
                "impacto": 46, "sacude": 6}
    if nombre == "Rayo Hielo":
        return proyectil(punto_salida, destino, (160, 161, 162, 113), cantidad=7, escala=4, duracion=18, separacion_frames=3, spread=30, ids_impacto=(113, 160),
                         escala_impacto=5, extra=[Flash(18, 12, (190, 230, 255), 110)])

    # ---------- PLANTA ----------
    if nombre in ("Látigo Cepa", "Látigo Cerval"):
        escala_latigo = 8 if nombre == "Látigo Cerval" else 6
        return contacto(origen, destino, (234,), embestida=False, sacude=10,
                        extra=[Particula((50, 51, 52), 0, 14, (destino[0] - 140, destino[1] - 80), (destino[0] + 60, destino[1] + 60), escala=escala_latigo, frames_por_cuadro=3),
                               Particula((51, 52, 50), 6, 14, (destino[0] + 140, destino[1] - 80), (destino[0] - 60, destino[1] + 60), escala=escala_latigo, frames_por_cuadro=3)], frame_impacto=10)
    if nombre == "Hoja Afilada":
        return proyectil(punto_salida, destino, (136, 137, 138, 139), cantidad=8, escala=4, duracion=22, separacion_frames=3, spread=50, altura_arco=30, giro_por_frame=25, ids_impacto=(234,), escala_impacto=5)
    if nombre == "Rayo Solar":
        return {"elementos": [Orbita((101, 102), origen, 0, 30, cantidad=7, radio_inicial=170, radio_final=10, escala=3, vueltas=1.0),
                       Flash(30, 20, (255, 250, 170), 130),
                       Haz(punto_salida, destino, 30, 34, (255, 240, 120), 70), _impacto(destino, (233,), 36, escala=8)],
                "impacto": 32, "sacude": 12}
    # ===== TEMA: Diccionarios (Clase 11) + Listas (Clase 11) =====
    # Diccionario usado como tabla de búsqueda; lista por comprensión con random
    # Energía que sale del rival hacia el atacante; más partículas cuanto más fuerte es el ataque
    if nombre in ("Absorber", "Megaagotar", "Gigadrenado"):
        cantidad = {"Absorber": 6, "Megaagotar": 9, "Gigadrenado": 12}[nombre]
        return {"elementos": [_impacto(destino, (200, 202), 0, escala=5, duracion=14)] +
                [Particula((200, 201, 202, 203), 10 + k * 3, 26, (destino[0] + random.randint(-70, 70), destino[1] + random.randint(-70, 70)), origen, escala=3.5, frames_por_cuadro=3, alpha_fin=120) for k in range(cantidad)], "impacto": 6, "sacude": 6}
    if nombre == "Bomba Lodo":
        return proyectil(punto_salida, destino, (238, 237), cantidad=1, escala=4, duracion=24, altura_arco=100, giro_por_frame=14, ids_impacto=(233, 238), escala_impacto=4, sacude=10)

    # ---------- PSÍQUICO ----------
    if nombre == "Confusión":
        return {"elementos": [Anillo(destino, k * 8, 30, 20, 170, (255, 150, 230), 8) for k in range(3)], "impacto": 14, "sacude": 6, "temblor": "objetivo"}
    if nombre == "Psíquico":
        return {"elementos": [Anillo(destino, k * 7, 34, 20, 230, (190, 110, 255), 12) for k in range(4)] +
                      [Flash(0, 40, (200, 120, 255), 90)], "impacto": 16, "sacude": 10, "temblor": "objetivo"}
    if nombre == "Psicorrayo":
        return {"elementos": [Anillo(destino, 8, 28, 20, 175, (235, 110, 220), 9),
                              Haz(punto_salida, destino, 0, 26, (215, 115, 255), 55)],
                "impacto": 14, "sacude": 10, "temblor": "objetivo"}

    # ---------- ELÉCTRICO ----------
    # Rayo que cae desde arriba sobre el rival
    if nombre == "Impactrueno":
        return {"elementos": [RayoDescendente("a125_arriba", (destino[0], destino[1] + 20), 0, 18, escala=6, frames_crecer=5, frames_borrar=6, amplitud_temblor=3, estiramiento=1.5),
                       Flash(5, 8, (255, 255, 160), 110)], "impacto": 5, "sacude": 8, "temblor": "objetivo"}
    if nombre == "Onda Shock":
        return {"elementos": [Particula((154,), 0, 22, destino, destino, escala=4, frames_por_cuadro=3, amplitud_temblor=6),
                       Particula((204, 205, 206, 207), 0, 22, destino, destino, escala=6, frames_por_cuadro=2, amplitud_temblor=40),
                       Flash(0, 10, (255, 255, 160), 110)], "impacto": 4, "sacude": 8, "temblor": "objetivo"}
    if nombre == "Chispa":
        return proyectil(punto_salida, destino, (101,), cantidad=1, escala=5, duracion=20, ids_impacto=(205, 206), escala_impacto=7, sacude=8,
                         extra=[Particula((207, 204), 0, 20, punto_salida, destino, escala=5, frames_por_cuadro=2, amplitud_temblor=14)])
    if nombre == "Trueno":
        return {"elementos": [Particula((125,), 4, 22, (destino[0], destino[1] - 120), (destino[0], destino[1] - 120), escala=5.5, frames_por_cuadro=1, amplitud_temblor=10),
                       Particula((125,), 14, 18, (destino[0] + 40, destino[1] - 120), (destino[0] + 40, destino[1] - 120), escala=5, frames_por_cuadro=1, amplitud_temblor=10),
                       Particula((205, 206, 207), 8, 28, destino, destino, escala=7, frames_por_cuadro=2, amplitud_temblor=40),
                       Flash(4, 8, (255, 255, 255), 230), Flash(16, 8, (255, 255, 200), 200)],
                "impacto": 6, "sacude": 18, "temblor": "objetivo"}
    if nombre == "Electrocañón":
        return {"elementos": [Particula((101,), 0, 30, origen, origen, escala=4, escala_fin=11, aditivo=True),
                       Particula((101,), 30, 18, punto_salida, destino, escala=9, frames_por_cuadro=2),
                       Particula((204, 205, 206, 207), 30, 18, punto_salida, destino, escala=7, frames_por_cuadro=2, amplitud_temblor=30),
                       _impacto(destino, (233, 205), 48, escala=9), Flash(48, 14, (255, 255, 180), 180)],
                "impacto": 48, "sacude": 18}
    if nombre == "Autodestrucción":
        return {"elementos": [Flash(0, 20, (255, 255, 255), 255), _impacto(origen, (44,), 4, escala=10, escala_fin=8, duracion=30),
                       _impacto(destino, (233,), 10, escala=6, duracion=16), Anillo(origen, 4, 30, 30, 520, (255, 220, 120), 16)],
                "impacto": 8, "sacude": 24}
    if nombre == "Puño Trueno":
        return contacto(origen, destino, (233,), escala=7, sacude=12,
                        extra=[Particula((189,), 4, 14, destino, destino, escala=7, escala_fin=9),
                               Particula((204, 205, 206, 207), 6, 18, destino, destino, escala=6, frames_por_cuadro=2, amplitud_temblor=40)])

    # ---------- TIERRA ----------
    if nombre in ("Disparo Lodo", "Bofetón Lodo"):
        resultado = proyectil(punto_salida, destino, (238, 237, 236), cantidad=4, escala=5, duracion=22, separacion_frames=5, altura_arco=60, spread=30, ids_impacto=(238,), escala_impacto=6, giro_por_frame=10, sacude=8)
        if nombre == "Bofetón Lodo":
            resultado["elementos"].append(Particula((192,), 6, 14, (destino[0] - 90, destino[1]), (destino[0] + 90, destino[1]), escala=7))
        return resultado
    # ===== TEMA: Bucles (Clase 4) + Listas (Clase 11) =====
    # for/range con append sobre la lista elementos
    # Rocas que saltan por el campo y sacuden a ambos Pokémon (más fuerte con Terremoto)
    if nombre in ("Terremoto", "Terratemblor"):
        fuerte = nombre == "Terremoto"
        cantidad = 10 if fuerte else 5
        elementos = []
        for k in range(cantidad):
            x = random.randint(300, 1620)
            y = random.randint(520, 880)
            elementos.append(Particula((176, 177, 178, 179, 236, 237), k * 3, 26, (x, y), (x + random.randint(-60, 60), y - random.randint(80, 200)),
                                escala=5, altura_arco=random.randint(60, 140), alpha_fin=0, giro_por_frame=random.choice((-9, 9))))
        return {"elementos": elementos, "impacto": 8, "sacude": 26 if fuerte else 14, "sacude_duracion": 50 if fuerte else 36, "sacude_a": "ambos"}
    # El hueso viaja hacia el rival y vuelve (ida_vuelta)
    if nombre == "Huesomerang":
        return proyectil(punto_salida, destino, (80,), cantidad=1, escala=6, duracion=44, giro_por_frame=34, ida_vuelta=True, ids_impacto=(233,), sacude=10, altura_arco=60)

    # ---------- LUCHA ----------
    if nombre in ("Golpe Kárate", "Sumisión", "A Bocajarro", "Doble Patada"):
        escala_golpe = 4 if nombre in ("A Bocajarro", "Sumisión") else 3
        sacudida = 14 if nombre == "A Bocajarro" else 11
        return contacto(origen, destino, (), escala=escala_golpe, sacude=sacudida,
                        extra=[Particula((189,), 4, 14, destino, destino, escala=escala_golpe, escala_fin=escala_golpe + 1)])

    # ---------- HIELO ----------
    if nombre in ("Viento Hielo", "Ventisca"):
        rafaga = 12 if nombre == "Ventisca" else 6
        escala_hielo = 4 if nombre == "Ventisca" else 3
        sacudida = 14 if nombre == "Ventisca" else 8
        elementos = [Particula((113, 160, 161, 162), k * 3, 24,
                               (punto_salida[0], punto_salida[1] + random.randint(-50, 50)),
                               (destino[0] + random.randint(-45, 45), destino[1] + random.randint(-35, 35)),
                               escala=escala_hielo, giro_por_frame=18, alpha_fin=80)
                     for k in range(rafaga)]
        elementos.append(Flash(18, 12, (190, 235, 255), 120))
        return {"elementos": elementos, "impacto": 18, "sacude": sacudida}

    # ---------- DRAGÓN ----------
    if nombre == "Garra Dragón":
        return contacto(origen, destino, (), extra=[Tajo(destino, 6, color=(110, 130, 255), largo=190)], sacude=12)
    if nombre == "Pulso Dragón":
        return {"elementos": [Anillo(destino, k * 7, 30, 20, 195, (115, 130, 255), 11) for k in range(3)] +
                              [Flash(8, 14, (130, 140, 255), 100)],
                "impacto": 14, "sacude": 12}

    # ===== TEMA: Condicionales (Clase 4) + Listas (Clase 11) =====
    # if + return anticipado; lista por comprensión con for/range y random.randint
    # ---------- ESTADO = POCIÓN + ESCUDO (siempre sobre quien la usa) ----------
    # Todas las habilidades de Estado son la misma: el Pokémon se cura y se protege con un escudo.
    # Por eso TODAS dibujan el efecto sobre el atacante (origen) y ninguna sobre el rival (destino),
    # sin importar si antes eran de "ataque" (bajaban una estadística del rival) o de "defensa"
    if tipo == "Estado":
        # Partículas de curación que suben alrededor del atacante (las mismas de Recuperación/Drenadoras)
        curacion = [Particula((200, 201, 202, 203), k * 4, 34, (origen[0] + random.randint(-110, 110), origen[1] + 110),
                              (origen[0] + random.randint(-110, 110), origen[1] - 130), escala=4, frames_por_cuadro=3, alpha_fin=0) for k in range(8)]
        # Dos anillos que se expanden desde el atacante: el escudo
        escudo = [Anillo(origen, 4, 30, 50, 170, (120, 200, 255), 8), Anillo(origen, 12, 30, 50, 190, (180, 230, 255), 5)]
        # impacto = frame en el que el motor aplica la cura (el texto "+N HP" sale sobre el atacante)
        return {"elementos": curacion + escudo, "impacto": 10}

    # ===== TEMA: Diccionarios (Clase 11) + Tuplas (Clase 11) =====
    # .get() con valor por defecto y desempaquetado de tupla
    # ---------- RESPALDO POR TIPO ----------
    # Si la habilidad no tiene efecto propio se usa uno genérico según su tipo
    respaldo = {"Fuego": ((38, 39, 40), (43,)), "Agua": ((3, 2, 1), (7,)), "Planta": ((136, 137), (234,)),
                "Eléctrico": ((101,), (205, 206)), "Tierra": ((238, 237), (233,)), "Psíquico": ((101,), (233,)),
                "Hielo": ((160, 161), (113,)), "Dragón": ((101, 145), (233,)), "Lucha": ((189,), (233,)),
                "Veneno": ((238, 237), (233,)), "Bicho": ((136, 137), (234,)), "Fantasma": ((101,), (233,)),
                "Normal": ((145,), (233,))}
    ids_proyectil, ids_impacto = respaldo.get(tipo, ((145,), (233,)))
    return proyectil(punto_salida, destino, ids_proyectil, cantidad=3, escala=5, duracion=22, separacion_frames=5, spread=20, ids_impacto=ids_impacto)


# ===== TEMA: POO (Clase 16) =====
# Clase _Efecto: guarda el estado de la animación en curso
# --------- Gestor ---------
# Estado de la animación en curso: sus elementos, el frame actual y las opciones (sacudida, embestida, baldosa...)
class _Efecto:
    def __init__(self, atacante, spec, al_impactar):
        self.atacante = atacante
        self.elementos = spec["elementos"]
        # ===== TEMA: Diccionarios (Clase 11) =====
        # .get(clave, valor_por_defecto) lee las opciones del diccionario spec
        # Frame en el que ocurre el golpe: ahí se aplica el daño
        self.impacto = spec.get("impacto", 10)
        self.embestida = spec.get("embestida", False)
        self.vaiven = spec.get("vaiven")           # (amplitud px, duración): el atacante va de lado a lado
        self.sacude = spec.get("sacude", 0)
        self.sacude_duracion = spec.get("sacude_duracion", 22)
        self.sacude_a = spec.get("sacude_a", "objetivo")
        self.temblor = spec.get("temblor")
        self.tile = spec.get("tile")
        self.al_impactar = al_impactar
        self.frame_actual = 0
        # ===== TEMA: Listas (Clase 11) =====
        # Lista por comprensión + concatenación; max() devuelve el mayor
        # La animación termina cuando acaba el último elemento (o 14 frames después del impacto)
        frame_fin = max([elemento.frame_fin for elemento in self.elementos] + [self.impacto + 14])
        if self.tile:
            frame_fin = max(frame_fin, self.tile[3])
        self.frame_fin = frame_fin
        self.impacto_notificado = False


# ===== TEMA: POO (Clase 16) =====
# Clase GestorEfectos: controla qué efecto se reproduce y lo avanza frame a frame
# Controla qué efecto se reproduce, lo avanza frame a frame y calcula los desplazamientos de los pokémons
class GestorEfectos:
    def __init__(self):
        self.actual = None
        self._tiles = {}
        self._mascaras = {}

    # --------- Control ---------
    # ===== TEMA: POO (Clase 16) =====
    # Método que retorna un booleano
    # True mientras hay una animación (la interfaz bloquea los botones)
    def ocupado(self):
        return self.actual is not None

    # ===== TEMA: POO (Clase 16) + Modularidad (Clase 10) =====
    # Llama a construir() y guarda el objeto en self.actual
    # Construye y empieza el efecto de una habilidad; al_impactar se llama cuando ocurre el golpe
    def lanzar(self, atacante, nombre, tipo, al_impactar=None):
        self.actual = _Efecto(atacante, construir(nombre, tipo, atacante), al_impactar)

    # ===== TEMA: Condicionales (Clase 4) =====
    # if anidados; return anticipado si no hay efecto
    # Se llama una vez por frame: avanza la animación y avisa del impacto
    def actualizar(self):
        efecto = self.actual
        if efecto is None:
            return
        # En el frame del impacto se avisa una sola vez (aquí el motor aplica el daño)
        if efecto.frame_actual == efecto.impacto and not efecto.impacto_notificado:
            efecto.impacto_notificado = True
            if efecto.al_impactar:
                efecto.al_impactar()
        efecto.frame_actual += 1
        # Al terminar se borra el efecto; por seguridad, si el golpe no se notificó se aplica ahora
        if efecto.frame_actual >= efecto.frame_fin:
            if not efecto.impacto_notificado and efecto.al_impactar:   # por seguridad, nunca se pierde el golpe
                efecto.al_impactar()
            # actual: el efecto en curso (None si no hay animación)
            self.actual = None

    # ===== TEMA: Condicionales (Clase 4) + Tuplas (Clase 11) =====
    # Varios if seguidos; retorna una tupla (dx, dy)
    # --------- Desplazamientos de los Pokemons ---------
    # Devuelve cuánto (dx, dy) hay que mover a un Pokémon en este frame por embestida, vaivén, sacudida o temblor
    def desplazamiento(self, quien):
        efecto = self.actual
        if efecto is None:
            return (0, 0)
        dx = dy = 0
        objetivo = _oponente(efecto.atacante)
        # Embestida: el atacante avanza hacia el rival y vuelve (curva seno), hasta el 28% del trayecto
        if efecto.embestida and quien == efecto.atacante:
            progreso = min(1.0, efecto.frame_actual / (efecto.impacto + 8))
            origen, destino = CENTRO[efecto.atacante], CENTRO[objetivo]
            factor_embestida = math.sin(math.pi * progreso) * 0.28
            dx, dy = (destino[0] - origen[0]) * factor_embestida, (destino[1] - origen[1]) * factor_embestida
        if efecto.vaiven and quien == efecto.atacante and efecto.frame_actual < efecto.vaiven[1]:
            progreso = efecto.frame_actual / efecto.vaiven[1]
            dx += efecto.vaiven[0] * math.sin(2 * math.pi * 3 * progreso)    # 3 idas y vueltas, termina en su sitio
        # Sacudida al recibir el golpe: aleatoria y cada vez más pequeña
        if efecto.sacude and efecto.frame_actual >= efecto.impacto and efecto.frame_actual < efecto.impacto + efecto.sacude_duracion:
            quienes = (efecto.atacante, objetivo) if efecto.sacude_a == "ambos" else (objetivo,)
            if quien in quienes:
                fraccion_restante = 1 - (efecto.frame_actual - efecto.impacto) / efecto.sacude_duracion
                amplitud = efecto.sacude * fraccion_restante
                dx += random.uniform(-amplitud, amplitud)
                dy += random.uniform(-amplitud, amplitud) * 0.6
        # Temblor lateral del objetivo (ataques eléctricos o psíquicos)
        if efecto.temblor == "objetivo" and quien == objetivo and efecto.impacto <= efecto.frame_actual < efecto.impacto + 26:
            dx += math.sin(efecto.frame_actual * 1.7) * 14
        return (int(dx), int(dy))

    # ===== TEMA: Diccionarios (Clase 11) + Tuplas (Clase 11) =====
    # pokemons es un diccionario {lado: (imagen, posición)}
    # --------- dibujo ---------
    def dibujar_sobre_pokemons(self, pantalla, pokemons):
        """Baldosas de estadísticas sobre la silueta del Pokémon. pokemons = {"ia": (imagen, pos), ...}"""
        efecto = self.actual
        if efecto is None or not efecto.tile:
            return
        sobre, nombre_tile, sube, duracion = efecto.tile
        if efecto.frame_actual < efecto.impacto - 4 or sobre not in pokemons:
            return
        imagen_pokemon, pos = pokemons[sobre]
        frames_transcurridos = efecto.frame_actual - (efecto.impacto - 4)
        progreso = frames_transcurridos / duracion
        # Opacidad: aparece rápido y se desvanece al final
        alfa = int(190 * min(1.0, progreso * 6, (1 - progreso) * 4))
        if alfa <= 0:
            return
        base = self._tile(nombre_tile, imagen_pokemon.get_width())
        ancho, alto = imagen_pokemon.get_size()
        # Capa donde se repite la baldosa en vertical y se desplaza para dar sensación de subir o bajar
        capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        paso = base.get_height()
        desplazamiento_y = (-frames_transcurridos * 7 if sube else frames_transcurridos * 7) % paso
        # ===== TEMA: Bucles (Clase 4) =====
        # range con tres argumentos (inicio, fin, paso)
        for y_baldosa in range(-paso, alto + paso, paso):
            capa.blit(base, (0, y_baldosa + desplazamiento_y))
        # Se recorta con la silueta del Pokémon: la baldosa solo se ve sobre su cuerpo
        capa.blit(self._mascara(imagen_pokemon), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        capa.set_alpha(alfa)
        pantalla.blit(capa, pos)

    # ===== TEMA: Bucles (Clase 4) + POO (Clase 16) =====
    # for sobre una lista de objetos; cada uno ejecuta su propio dibujar
    # Dibuja todos los elementos del efecto en curso en su frame actual
    def dibujar(self, pantalla):
        efecto = self.actual
        if efecto is None:
            return
        for elemento in efecto.elementos:
            elemento.dibujar(pantalla, efecto.frame_actual)

    # ===== TEMA: POO (Clase 16) + Diccionarios (Clase 11) =====
    # Métodos privados con caché en diccionario
    # --- utilidades ---
    # Devuelve la baldosa de estadística como cuadrado del ancho pedido (si falta la imagen usa un cuadro blanco)
    def _tile(self, nombre, ancho):
        clave = (nombre, ancho)
        if clave not in self._tiles:
            img = _cargar("stats", nombre)
            if img is None:
                img = pygame.Surface((ancho, ancho))
                img.fill((255, 255, 255))
            self._tiles[clave] = pygame.transform.scale(img, (ancho, ancho))
        return self._tiles[clave]

    # Convierte la silueta del Pokémon en una imagen blanca/transparente, que sirve para recortar la baldosa
    def _mascara(self, imagen_pokemon):
        clave = id(imagen_pokemon)
        if clave not in self._mascaras:
            mascara = pygame.mask.from_surface(imagen_pokemon, 20)
            self._mascaras[clave] = mascara.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
        return self._mascaras[clave]