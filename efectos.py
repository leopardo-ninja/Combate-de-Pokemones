# ----------------- EFECTOS VISUALES DE LAS HABILIDADES -----------------
# Usa los sprites recortados en assets/efectos/ (ver recortar_efectos.py).
#   assets/efectos/ataque/aNNN.png  -> sprites sueltos de ataques
#   assets/efectos/stats/<stat>.png -> baldosas de subida/bajada de estadísticas
#
# Uso desde la interfaz:
#   gestor = GestorEfectos()
#   gestor.lanzar("jugador", "Lanzallamas", "Fuego", al_impactar=funcion)
#   cada frame: gestor.actualizar(); gestor.dibujar_fondo(...); gestor.dibujar(...)

import math
import os
import random

import pygame

RUTA_EFECTOS = "assets/efectos"

# Centro de cada Pokémon en la pantalla virtual 1920x1080
CENTRO = {"ia": (1280, 410), "jugador": (640, 690)}
# Punto de la cara (de donde salen los chorros y adonde llegan)
CARA = {"ia": (1250, 360), "jugador": (700, 590)}

_CACHE = {}
_CACHE_ESCALADAS = {}
_CACHE_TINTADAS = {}


def _cargar(grupo, nombre):
    clave = (grupo, nombre)
    if clave not in _CACHE:
        ruta = f"{RUTA_EFECTOS}/{grupo}/{nombre}.png"
        _CACHE[clave] = pygame.image.load(ruta).convert_alpha() if os.path.exists(ruta) else None
    return _CACHE[clave]


def cargar_sprite_ataque(n):
    return _cargar("ataque", n if isinstance(n, str) else f"a{n:03d}")


def _escalar_con_cache(surf, factor):
    clave = (id(surf), round(factor, 2))
    if clave not in _CACHE_ESCALADAS:
        w, h = surf.get_size()
        _CACHE_ESCALADAS[clave] = pygame.transform.scale(surf, (max(1, int(w * factor)), max(1, int(h * factor))))
    return _CACHE_ESCALADAS[clave]


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


def _lerp(a, b, u):
    return a + (b - a) * u


def _oponente(lado):
    return "ia" if lado == "jugador" else "jugador"


# ----------------- ELEMENTOS ANIMADOS -----------------
class Particula:
    """Un sprite (o varios fotogramas) que viaja de 'desde' a 'hasta'."""

    def __init__(self, ids_sprites, frame_inicio, duracion, desde, hasta, escala=5, escala_fin=None, altura_arco=0, frames_por_cuadro=4,
                 alpha_fin=255, angulo=0, giro_por_frame=0, aditivo=False, amplitud_temblor=0, ida_vuelta=False, tinte=None):
        self.frames = [s for s in (cargar_sprite_ataque(i) for i in ids_sprites) if s is not None]
        self.tinte = tinte          # (r, g, b) para cambiar el color del sprite, ej. (255, 70, 50) = rojo
        self.frame_inicio, self.duracion = frame_inicio, duracion
        self.desde, self.hasta = desde, hasta
        self.escala, self.escala_fin = escala, escala if escala_fin is None else escala_fin
        self.altura_arco, self.frames_por_cuadro = altura_arco, frames_por_cuadro
        self.alpha_fin, self.angulo, self.giro_por_frame = alpha_fin, angulo, giro_por_frame
        self.aditivo, self.amplitud_temblor, self.ida_vuelta = aditivo, amplitud_temblor, ida_vuelta
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if not self.frames or frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        frames_transcurridos = frame_actual - self.frame_inicio
        progreso = frames_transcurridos / self.duracion
        progreso_ajustado = 1 - abs(2 * progreso - 1) if self.ida_vuelta else progreso
        x = _lerp(self.desde[0], self.hasta[0], progreso_ajustado)
        y = _lerp(self.desde[1], self.hasta[1], progreso_ajustado) - self.altura_arco * 4 * progreso_ajustado * (1 - progreso_ajustado)
        if self.amplitud_temblor:
            x += random.randint(-self.amplitud_temblor, self.amplitud_temblor)
            y += random.randint(-self.amplitud_temblor, self.amplitud_temblor)
        img = _escalar_con_cache(self.frames[(frames_transcurridos // self.frames_por_cuadro) % len(self.frames)], _lerp(self.escala, self.escala_fin, progreso))
        if self.tinte:
            img = _tintar(img, self.tinte)
        ang = self.angulo + self.giro_por_frame * frames_transcurridos
        if ang:
            img = pygame.transform.rotate(img, ang)
        alpha = int(_lerp(255, self.alpha_fin, progreso))
        if alpha < 255:
            img = img.copy()
            img.set_alpha(alpha)
        flag = pygame.BLEND_RGB_ADD if self.aditivo else 0
        pantalla.blit(img, img.get_rect(center=(int(x), int(y))), special_flags=flag)


class Chorro:
    """Chorro fijo: sale de 'desde', se estira hasta 'hasta' y solo cambia de fotograma.
    El sprite es vertical con la cresta arriba; la cresta queda en el extremo del rival."""

    def __init__(self, ids_sprites, desde, hasta, frame_inicio, duracion, ancho=6, frames_por_cuadro=3, frames_crecimiento=4):
        self.frames = [s for s in (cargar_sprite_ataque(i) for i in ids_sprites) if s is not None]
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
        clave = (idx, largo)
        if clave not in self._cache:
            base = self.frames[idx]
            sup = pygame.transform.scale(base, (base.get_width() * self.ancho, largo))
            self._cache[clave] = pygame.transform.rotate(sup, math.degrees(math.atan2(-dx, -dy)))
        img = self._cache[clave]
        centro = (self.desde[0] + dx * fraccion_extendida / 2, self.desde[1] + dy * fraccion_extendida / 2)
        pantalla.blit(img, img.get_rect(center=(int(centro[0]), int(centro[1]))))


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
        r = int(_lerp(self.radio_inicial, self.radio_final, progreso))
        lado = r * 2 + self.grosor * 2
        sup = pygame.Surface((lado, lado), pygame.SRCALPHA)
        pygame.draw.circle(sup, (*self.color, int(255 * (1 - progreso))), (lado // 2, lado // 2), r, self.grosor)
        pantalla.blit(sup, sup.get_rect(center=self.centro))


class Tajo:
    """Tres arañazos diagonales (Arañazo, Mordisco...)."""

    def __init__(self, centro, frame_inicio, duracion=18, color=(255, 255, 255), largo=170):
        self.centro, self.frame_inicio, self.duracion, self.color, self.largo = centro, frame_inicio, duracion, color, largo
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        crecer = min(1.0, progreso * 2.5)
        for i in range(3):
            ox = (i - 1) * 46
            x0, y0 = self.centro[0] + ox - self.largo // 3, self.centro[1] - self.largo // 2 + i * 8
            x1 = x0 + int(self.largo * 0.55 * crecer)
            y1 = y0 + int(self.largo * crecer)
            ancho = max(2, int(10 * (1 - progreso)))
            pygame.draw.line(pantalla, self.color, (x0, y0), (x1, y1), ancho)


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
        punta = (_lerp(self.desde[0], self.hasta[0], progreso_extension), _lerp(self.desde[1], self.hasta[1], progreso_extension))
        grosor_actual = max(2, int(self.grosor * progreso_apagado * (0.85 + 0.15 * math.sin(frame_actual * 1.3))))
        pygame.draw.line(pantalla, self.color, self.desde, punta, grosor_actual)
        pygame.draw.line(pantalla, (255, 255, 255), self.desde, punta, max(2, grosor_actual // 2))


class Ola:
    """Ola de agua que cruza la pantalla (Surf)."""

    def __init__(self, frame_inicio, duracion, y0=330, y1=900):
        self.frame_inicio, self.duracion, self.y0, self.y1 = frame_inicio, duracion, y0, y1
        self.frame_fin = frame_inicio + duracion
        self._sup = None

    def dibujar(self, pantalla, frame_actual):
        if frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        ancho = pantalla.get_width()
        frente = int(_lerp(-200, ancho + 300, progreso))
        if self._sup is None:
            self._sup = pygame.Surface((ancho, self.y1 - self.y0), pygame.SRCALPHA)
        sup = self._sup
        sup.fill((0, 0, 0, 0))
        h = self.y1 - self.y0
        pts = [(0, 0)]
        for yy in range(0, h + 1, 20):
            pts.append((frente + int(40 * math.sin(yy / 28 + frame_actual / 4)), yy))
        pts.append((0, h))
        pygame.draw.polygon(sup, (50, 130, 235, 170), pts)
        for yy in range(0, h, 20):
            xx = frente + int(40 * math.sin(yy / 28 + frame_actual / 4))
            pygame.draw.circle(sup, (235, 245, 255, 230), (xx, yy), 14)
        pantalla.blit(sup, (0, self.y0))


class Flash:
    """Destello de pantalla completa."""

    def __init__(self, frame_inicio, duracion, color=(255, 255, 255), alpha_maximo=200):
        self.frame_inicio, self.duracion, self.color, self.alpha_maximo = frame_inicio, duracion, color, alpha_maximo
        self.frame_fin = frame_inicio + duracion
        self._sup = None

    def dibujar(self, pantalla, frame_actual):
        if frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        if self._sup is None or self._sup.get_size() != pantalla.get_size():
            self._sup = pygame.Surface(pantalla.get_size())
            self._sup.fill(self.color)
        self._sup.set_alpha(int(self.alpha_maximo * (1 - progreso)))
        pantalla.blit(self._sup, (0, 0))


class Orbita:
    """Sprites girando alrededor de un punto (Giro Fuego). Si se da centro_final, el anillo viaja
    desde 'centro' hasta 'centro_final' mientras gira (Llamarada)."""

    def __init__(self, ids_sprites, centro, frame_inicio, duracion, cantidad=8, radio_inicial=260, radio_final=40, escala=4, vueltas=2.0, centro_final=None):
        self.frames = [s for s in (cargar_sprite_ataque(i) for i in ids_sprites) if s is not None]
        self.centro, self.frame_inicio, self.duracion, self.cantidad = centro, frame_inicio, duracion, cantidad
        self.centro_final = centro if centro_final is None else centro_final
        self.radio_inicial, self.radio_final, self.escala, self.vueltas = radio_inicial, radio_final, escala, vueltas
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if not self.frames or frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        progreso = (frame_actual - self.frame_inicio) / self.duracion
        r = _lerp(self.radio_inicial, self.radio_final, progreso)
        for i in range(self.cantidad):
            ang = 2 * math.pi * (i / self.cantidad + self.vueltas * progreso)
            img = _escalar_con_cache(self.frames[(frame_actual // 4 + i) % len(self.frames)], self.escala)
            cx = _lerp(self.centro[0], self.centro_final[0], progreso)
            cy = _lerp(self.centro[1], self.centro_final[1], progreso)
            pos = (cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.7)
            pantalla.blit(img, img.get_rect(center=(int(pos[0]), int(pos[1]))))


class RayoDescendente:
    # Rayo que se dibuja de arriba hacia abajo, se mantiene y se borra de arriba hacia abajo

    def __init__(self, id_sprite, base, frame_inicio, duracion, escala=6, frames_crecer=5, frames_borrar=6, amplitud_temblor=0, estiramiento=1.0):
        self.sprite = cargar_sprite_ataque(id_sprite)
        self.estiramiento, self._img = estiramiento, None                   # estiramiento > 1 alarga solo en vertical
        self.base, self.frame_inicio, self.duracion, self.escala = base, frame_inicio, duracion, escala
        self.frames_crecer, self.frames_borrar, self.amplitud_temblor = frames_crecer, frames_borrar, amplitud_temblor
        self.frame_fin = frame_inicio + duracion

    def dibujar(self, pantalla, frame_actual):
        if self.sprite is None or frame_actual < self.frame_inicio or frame_actual >= self.frame_fin:
            return
        if self._img is None:
            w, h = self.sprite.get_size()
            self._img = pygame.transform.scale(self.sprite, (max(1, int(w * self.escala)), max(1, int(h * self.escala * self.estiramiento))))
        img = self._img
        ancho, alto = img.get_size()
        frames_transcurridos = frame_actual - self.frame_inicio
        fila_desde, fila_hasta = 0, alto                                   # filas visibles del sprite
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


# ----------------- CONSTRUCTORES DE EFECTOS -----------------
def _impacto(destino, ids_sprites, frame_inicio, escala=6, escala_fin=None, duracion=16, spread=0):
    pos = (destino[0] + random.randint(-spread, spread), destino[1] + random.randint(-spread, spread))
    return Particula(ids_sprites, frame_inicio, duracion, pos, pos, escala=escala, escala_fin=escala_fin or escala * 1.4, frames_por_cuadro=4, alpha_fin=0)


def proyectil(origen, destino, ids_proyectil, cantidad=1, escala=5, duracion=24, separacion_frames=4, altura_arco=0, frames_por_cuadro=4, ids_impacto=(233,), escala_impacto=6,
              spread=0, aditivo=False, giro_por_frame=0, ida_vuelta=False, sacude=0, extra=None):
    elementos = []
    for k in range(cantidad):
        s = random.randint(-spread, spread) if spread else 0
        hasta = (destino[0] + s, destino[1] + s // 2)
        elementos.append(Particula(ids_proyectil, k * separacion_frames, duracion, origen, hasta, escala=escala, altura_arco=altura_arco, frames_por_cuadro=frames_por_cuadro,
                            aditivo=aditivo, giro_por_frame=giro_por_frame, ida_vuelta=ida_vuelta))
        if ids_impacto:
            elementos.append(_impacto(hasta, ids_impacto, k * separacion_frames + (duracion // 2 if ida_vuelta else duracion), escala=escala_impacto))
    elementos += extra or []
    return {"elementos": elementos, "impacto": duracion // 2 if ida_vuelta else duracion, "sacude": sacude}


def contacto(origen, destino, golpe, escala=7, lunge=True, sacude=8, extra=None, frame_impacto=12):
    elementos = [_impacto(destino, golpe, frame_impacto, escala=escala, duracion=16)]
    elementos += extra or []
    return {"elementos": elementos, "impacto": frame_impacto, "lunge": lunge, "sacude": sacude}


def estado(sobre, tile, sube, extra=None, duracion=70):
    return {"elementos": extra or [], "impacto": 10, "tile": (sobre, tile, sube, duracion)}


# ----------------- Recrear cada habilidad -----------------
def construir(nombre, tipo, atacante):
    origen, destino = CENTRO[atacante], CENTRO[_oponente(atacante)]
    rival = _oponente(atacante)
    dx = 1 if destino[0] > origen[0] else -1
    punto_salida = (origen[0] + dx * 120, origen[1] - 20)          # salida del proyectil (de cara al rival)

    def tile(sobre, nombre_tile, sube, extra=None):
        return estado(sobre, nombre_tile, sube, extra)

    # ---------- NORMAL ----------
    if nombre in ("Placaje", "Tacleada", "Constricción"):
        return contacto(origen, destino, (), sacude = 10)
    if nombre in ("Patada",):
        return contacto(origen, destino, (), sacude = 12)
    if nombre in ("Arañazo", "Acuchillar") and tipo != "Estado":
        return contacto(origen, destino, (), extra = [Tajo(destino, 6)], sacude = 6)
    if nombre == "Ataque Rápido":
        # El atacante se mueve rápido de izquierda a derecha y, al terminar, estalla la estrella en el rival
        fin = 26
        return {"elementos": [_impacto(destino, (98,), fin, escala=1, escala_fin=2, duracion=16)],
                "impacto": fin, "vaiven": (42, fin), "sacude": 8}
    if nombre == "Rapidez":
        return proyectil(origen, destino, (145, 144), escala = 3, duracion = 12, ids_impacto = (), sacude = 6)
    if nombre == "Mordisco":
        return contacto(origen, destino, (), extra=[Particula((142,), 4, 18, destino, destino, escala = 2.5, escala_fin = 3)], sacude = 10)
    if nombre in ("Puño Certero",):
        return contacto(origen, destino, (), extra=[Particula((189,), 4, 14, destino, destino, escala = 3, escala_fin = 4)], sacude = 12)
    if nombre == "Bofetón":
        return contacto(origen, destino, (), extra=[Particula((192,), 4, 14, (destino[0] - 90, destino[1]), (destino[0] + 90, destino[1]), escala=7)])
    if nombre == "Látigo":
        return contacto(origen, destino, (), lunge=False, extra=[Particula((50, 51, 52), 2, 16, punto_salida, destino, escala = 3, frames_por_cuadro=3)])
    if nombre == "Hueso Palo":
        return proyectil(origen, destino, (80,), escala = 3, duracion = 22, giro_por_frame = 28, ids_impacto = (), sacude = 8)

    # ---------- FUEGO ----------
    if nombre == "Lanzallamas":
        return proyectil(punto_salida, destino, (38, 39, 40), cantidad=9, escala=4, duracion=22, separacion_frames=3, spread=24, ids_impacto=(43,), escala_impacto=3, aditivo=False)
    if nombre == "Ascuas":
        return proyectil(punto_salida, destino, (57, 58, 38), cantidad=6, escala=4, duracion=22, separacion_frames=5, spread=40, ids_impacto=(58,), escala_impacto=5)
    if nombre == "Giro Fuego":
        return {"elementos": [Orbita((38, 39, 40), destino, 0, 40, cantidad = 8, radio_inicial = 260, radio_final = 30, escala = 4), Flash(40, 10, (255, 150, 60), 90)],"impacto": 40, "sacude": 6}
    if nombre == "Colmillo Ígneo":
        return contacto(origen, destino, (43,), escala = 3, extra = [Particula((142,), 4, 18, destino, destino, escala = 2.5, escala_fin = 3), _impacto(destino, (46,), 14, escala = 6)], sacude = 10)
    if nombre == "Rueda Fuego":
        return proyectil(punto_salida, destino, (39, 40), cantidad = 1, escala = 7, duracion = 26, altura_arco = 120, ids_impacto = (46, 47), escala_impacto = 6, giro_por_frame = 0, sacude = 10, extra = 
                         [Particula((58,), 2, 24, punto_salida, destino, escala = 4, altura_arco = 120, alpha_fin = 0)])
    if nombre == "Nitrocarga":
        return contacto(origen, destino, (46, 47), escala = 2, sacude = 12, extra = [Particula((23,), 0, 12, origen, destino, escala = 2)])
    if nombre == "Envite Ígneo":
        return contacto(origen, destino, (47, 46), escala = 3, sacude = 3, extra = [Particula((23,), 0, 14, origen, destino, escala = 3), Flash(12, 14, (255, 180, 80), 120)], frame_impacto = 14)
    if nombre == "Puño Fuego":
        return contacto(origen, destino, (46,), escala = 3, sacude = 12, extra = [Particula((189,), 4, 14, destino, destino, escala = 2, escala_fin = 3, tinte = (255, 70, 50)), _impacto(destino, (43,), 12, escala = 2.5)])
    if nombre == "Llamarada":
        # Círculo de fuego (el mismo anillo de Giro Fuego) que viaja desde el atacante hasta el rival
        llegada = 30
        return {"elementos": [Orbita((38, 39, 40), punto_salida, 0, llegada, cantidad=12, radio_inicial=80, radio_final=130, escala=4, vueltas=1.5, centro_final=destino), _impacto(destino, (44, 45), llegada, escala = 5, escala_fin = 4, duracion = 18), 
                              Flash(llegada, 12, (255, 140, 50), 110)], "impacto": llegada, "sacude": 16}

    # ---------- AGUA ----------
    if nombre == "Pistola Agua":
        # Chorro con los fotogramas de la hoja: pistola0..3 en vuelo y pistola4 al impactar.
        # El sprite apunta hacia arriba-derecha; cuando dispara el rival se gira 180 grados.
        giro = 0 if atacante == "jugador" else 180
        en_vuelo = tuple(f"pistola{i}" for i in range(4))
        elementos = [Particula(en_vuelo, k * 5, 16, punto_salida, destino, escala=3, frames_por_cuadro=3, angulo=giro) for k in range(3)]
        elementos.append(Particula(("pistola4",), 16, 18, destino, destino, escala=3, escala_fin=4, angulo=giro, alpha_fin=0))
        return {"elementos": elementos, "impacto": 16, "sacude": 6}
    if nombre == "Burbuja":
        return proyectil(punto_salida, destino, (22, 19, 112, 18), cantidad = 6, escala = 3, duracion = 34, separacion_frames = 6, altura_arco = 40, spread = 40, ids_impacto = (9,), escala_impacto = 3, frames_por_cuadro = 8)
    if nombre == "Rayos Burbuja":
        return proyectil(punto_salida, destino, (112, 22, 113), cantidad = 10, escala = 2.5, duracion = 26, separacion_frames = 3, spread = 60, ids_impacto = (9,), escala_impacto = 3, frames_por_cuadro = 6)
    if nombre == "Hidrobomba":
        # Chorro fijo desde la cara del atacante hasta el rival; solo cambian los 4 fotogramas
        col = ("hidro0", "hidro1", "hidro2", "hidro3")
        return {"elementos": [Chorro(col, CARA[atacante], CARA[rival], 0, 46, ancho = 8, frames_por_cuadro = 3)],
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
        return proyectil(punto_salida, destino, (160, 161, 162, 113), cantidad = 7, escala = 4, duracion = 18, separacion_frames = 3, spread = 30, ids_impacto = (113, 160),
                         escala_impacto = 5, extra = [Flash(18, 12, (190, 230, 255), 110)])

    # ---------- PLANTA ----------
    if nombre in ("Látigo Cepa", "Látigo Cerval"):
        grande = 8 if nombre == "Látigo Cerval" else 6
        return contacto(origen, destino, (234,), lunge = False, sacude = 10,
                        extra=[Particula((50, 51, 52), 0, 14, (destino[0] - 140, destino[1] - 80), (destino[0] + 60, destino[1] + 60), escala=grande, frames_por_cuadro=3),
                               Particula((51, 52, 50), 6, 14, (destino[0] + 140, destino[1] - 80), (destino[0] - 60, destino[1] + 60), escala=grande, frames_por_cuadro=3)], frame_impacto=10)
    if nombre == "Hoja Afilada":
        return proyectil(punto_salida, destino, (136, 137, 138, 139), cantidad=8, escala=4, duracion=22, separacion_frames=3, spread=50, altura_arco=30, giro_por_frame=25, ids_impacto=(234,), escala_impacto=5)
    if nombre == "Rayo Solar":
        return {"elementos": [Orbita((101, 102), origen, 0, 30, cantidad=7, radio_inicial=170, radio_final=10, escala=3, vueltas=1.0),
                       Flash(30, 20, (255, 250, 170), 130),
                       Haz(punto_salida, destino, 30, 34, (255, 240, 120), 70), _impacto(destino, (233,), 36, escala=8)],
                "impacto": 32, "sacude": 12}
    if nombre in ("Absorber", "Megaagotar", "Gigadrenado"):
        cantidad = {"Absorber": 6, "Megaagotar": 9, "Gigadrenado": 12}[nombre]
        return {"elementos": [_impacto(destino, (200, 202), 0, escala = 5, duracion = 14)] + 
                [Particula((200, 201, 202, 203), 10 + k * 3, 26, (destino[0] + random.randint(-70, 70), destino[1] + random.randint(-70, 70)), origen, escala = 3.5, frames_por_cuadro = 3, alpha_fin = 120) for k in range(cantidad)], "impacto": 6, "sacude": 6}
    if nombre == "Bomba Lodo":
        return proyectil(punto_salida, destino, (238, 237), cantidad = 1, escala = 4, duracion = 24, altura_arco = 100, giro_por_frame = 14, ids_impacto = (233, 238), escala_impacto = 4, sacude = 10)

    # ---------- PSÍQUICO ----------
    if nombre == "Confusión":
        return {"elementos": [Anillo(destino, k * 8, 30, 20, 170, (255, 150, 230), 8) for k in range(3)], "impacto": 14, "sacude": 6, "temblor": "objetivo"}
    if nombre == "Psíquico":
        return {"elementos": [Anillo(destino, k * 7, 34, 20, 230, (190, 110, 255), 12) for k in range(4)] +
                      [Flash(0, 40, (200, 120, 255), 90)], "impacto": 16, "sacude": 10, "temblor": "objetivo"}

    # ---------- ELÉCTRICO ----------
    if nombre == "Impactrueno":
        return {"elementos": [RayoDescendente("a125_arriba", (destino[0], destino[1] + 20), 0, 18, escala = 6, frames_crecer = 5, frames_borrar = 6, amplitud_temblor = 3, estiramiento = 1.5),
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
                       Particula((125,), 14, 18, (destino[0] + 40, destino[1] - 120), (destino[0] + 40, destino[1] - 120), escala=5, amplitud_temblor=10),
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
        return {"elementos": [Flash(0, 20, (255, 255, 255), 255), _impacto(origen, (46, 47), 4, escala=11, escala_fin=15, duracion=30),
                       _impacto(destino, (233,), 10, escala=8, duracion=16), Anillo(origen, 4, 30, 30, 520, (255, 220, 120), 16)],
                "impacto": 8, "sacude": 24}
    if nombre == "Puño Trueno":
        return contacto(origen, destino, (233,), escala=7, sacude=12,
                        extra=[Particula((189,), 4, 14, destino, destino, escala=7, escala_fin=9),
                               Particula((204, 205, 206, 207), 6, 18, destino, destino, escala=6, frames_por_cuadro=2, amplitud_temblor=40)])

    # ---------- TIERRA ----------
    if nombre in ("Disparo Lodo", "Bofetón Lodo"):
        r = proyectil(punto_salida, destino, (238, 237, 236), cantidad=4, escala=5, duracion=22, separacion_frames=5, altura_arco=60, spread=30, ids_impacto=(238,), escala_impacto=6, giro_por_frame=10, sacude=8)
        if nombre == "Bofetón Lodo":
            r["elementos"].append(Particula((192,), 6, 14, (destino[0] - 90, destino[1]), (destino[0] + 90, destino[1]), escala=7))
        return r
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
    if nombre == "Huesomerang":
        return proyectil(punto_salida, destino, (80,), cantidad = 1, escala = 6, duracion = 44, giro_por_frame = 34, ida_vuelta = True, ids_impacto = (233,), sacude = 10, altura_arco = 60)

    # ---------- ESTADO (baldosas de estadísticas) ----------
    if tipo == "Estado":
        if nombre in ("Foco Energía", "Acuchillar"):
            return tile(atacante, "ataque", True)
        if nombre in ("Refugio", "Defensa Férrea", "Fortaleza"):
            return tile(atacante, "defensa", True)
        if nombre == "Agilidad":
            return tile(atacante, "velocidad", True)
        if nombre in ("Amnesia", "Pantalla Luz", "Pantalla de Luz"):
            return tile(atacante, "def_esp", True)
        if nombre == "Crecimiento":
            return tile(atacante, "atk_esp", True)
        if nombre in ("Rugido", "Growl"):
            return tile(rival, "ataque", False)
        if nombre == "Malicioso":
            return tile(rival, "defensa", False)
        if nombre in ("Pantalla Humo", "Supersónico"):
            return tile(rival, "precision", False)
        if nombre == "Infortunio":
            return tile(rival, "evasion", False)
        if nombre == "Encanto":
            return tile(rival, "ataque", False, [Particula((166, 165, 167), k * 6, 34, (destino[0] + (k - 1) * 70, destino[1] + 40),
                                                         (destino[0] + (k - 1) * 90, destino[1] - 140), escala=5, alpha_fin=0) for k in range(3)])
        if nombre in ("Hipnosis", "Polvo Sueño", "Smog"):
            return tile(rival, "mezcla", False, [Particula((205, 207, 206), k * 4, 30, (destino[0] + random.randint(-80, 80), destino[1] - 40),
                                                           (destino[0] + random.randint(-80, 80), destino[1] - 160), escala=4, alpha_fin=0) for k in range(6)])
        if nombre == "Onda Trueno":
            return {"elementos": [Particula((204, 205, 206, 207), 0, 40, destino, destino, escala=6, frames_por_cuadro=2, amplitud_temblor=60),
                           Particula((154,), 0, 40, destino, destino, escala=4, frames_por_cuadro=3, amplitud_temblor=8)], "impacto": 6, "temblor": "objetivo"}
        if nombre in ("Recuperación", "Drenadoras"):
            return {"elementos": [Particula((200, 201, 202, 203), k * 5, 40, (origen[0] + random.randint(-120, 120), origen[1] + 120),
                                     (origen[0] + random.randint(-120, 120), origen[1] - 140), escala=4, frames_por_cuadro=3, alpha_fin=0) for k in range(10)],
                    "impacto": 10}
        return tile(atacante, "mezcla", True)

    # ---------- RESPALDO POR TIPO ----------
    respaldo = {"Fuego": ((38, 39, 40), (43,)), "Agua": ((3, 2, 1), (7,)), "Planta": ((136, 137), (234,)),
                "Eléctrico": ((101,), (205, 206)), "Tierra": ((238, 237), (233,)), "Psíquico": ((101,), (233,))}
    ids_proyectil, ids_impacto = respaldo.get(tipo, ((145,), (233,)))
    return proyectil(punto_salida, destino, ids_proyectil, cantidad=3, escala=5, duracion=22, separacion_frames=5, spread=20, ids_impacto=ids_impacto)


# --------- Gestor ---------
class _Efecto:
    def __init__(self, atacante, spec, al_impactar):
        self.atacante = atacante
        self.elementos = spec["elementos"]
        self.impacto = spec.get("impacto", 10)
        self.lunge = spec.get("lunge", False)
        self.vaiven = spec.get("vaiven")           # (amplitud px, duración): el atacante va de lado a lado
        self.sacude = spec.get("sacude", 0)
        self.sacude_duracion = spec.get("sacude_duracion", 22)
        self.sacude_a = spec.get("sacude_a", "objetivo")
        self.temblor = spec.get("temblor")
        self.tile = spec.get("tile")
        self.al_impactar = al_impactar
        self.frame_actual = 0
        frame_fin = max([e.frame_fin for e in self.elementos] + [self.impacto + 14])
        if self.tile:
            frame_fin = max(frame_fin, self.tile[3])
        self.frame_fin = frame_fin
        self.impacto_notificado = False


class GestorEfectos:
    def __init__(self):
        self.actual = None
        self._tiles = {}
        self._mascaras = {}

    # --------- Control ---------
    def ocupado(self):
        return self.actual is not None

    def lanzar(self, atacante, nombre, tipo, al_impactar=None):
        self.actual = _Efecto(atacante, construir(nombre, tipo, atacante), al_impactar)

    def actualizar(self):
        e = self.actual
        if e is None:
            return
        if e.frame_actual == e.impacto and not e.impacto_notificado:
            e.impacto_notificado = True
            if e.al_impactar:
                e.al_impactar()
        e.frame_actual += 1
        if e.frame_actual >= e.frame_fin:
            if not e.impacto_notificado and e.al_impactar:   # por seguridad, nunca se pierde el golpe
                e.al_impactar()
            self.actual = None

    # --------- Desplazamientos de los Pokemons ---------
    def desplazamiento(self, quien):
        e = self.actual
        if e is None:
            return (0, 0)
        dx = dy = 0
        objetivo = _oponente(e.atacante)
        if e.lunge and quien == e.atacante:
            progreso = min(1.0, e.frame_actual / (e.impacto + 8))
            origen, destino = CENTRO[e.atacante], CENTRO[objetivo]
            f = math.sin(math.pi * progreso) * 0.28
            dx, dy = (destino[0] - origen[0]) * f, (destino[1] - origen[1]) * f
        if e.vaiven and quien == e.atacante and e.frame_actual < e.vaiven[1]:
            progreso = e.frame_actual / e.vaiven[1]
            dx += e.vaiven[0] * math.sin(2 * math.pi * 3 * progreso)    # 3 idas y vueltas, termina en su sitio
        if e.sacude and e.frame_actual >= e.impacto and e.frame_actual < e.impacto + e.sacude_duracion:
            quienes = (e.atacante, objetivo) if e.sacude_a == "ambos" else (objetivo,)
            if quien in quienes:
                resto = 1 - (e.frame_actual - e.impacto) / e.sacude_duracion
                amp = e.sacude * resto
                dx += random.uniform(-amp, amp)
                dy += random.uniform(-amp, amp) * 0.6
        if e.temblor == "objetivo" and quien == objetivo and e.impacto <= e.frame_actual < e.impacto + 26:
            dx += math.sin(e.frame_actual * 1.7) * 14
        return (int(dx), int(dy))

    # --------- dibujo ---------
    def dibujar_sobre_sprites(self, pantalla, sprites):
        """Baldosas de estadísticas sobre la silueta del Pokémon. sprites = {"ia": (surf, pos), ...}"""
        e = self.actual
        if e is None or not e.tile:
            return
        sobre, nombre_tile, sube, duracion = e.tile
        if e.frame_actual < e.impacto - 4 or sobre not in sprites:
            return
        surf, pos = sprites[sobre]
        frames_transcurridos = e.frame_actual - (e.impacto - 4)
        progreso = frames_transcurridos / duracion
        alfa = int(190 * min(1.0, progreso * 6, (1 - progreso) * 4))
        if alfa <= 0:
            return
        base = self._tile(nombre_tile, surf.get_width())
        w, h = surf.get_size()
        capa = pygame.Surface((w, h), pygame.SRCALPHA)
        paso = base.get_height()
        desp = (-frames_transcurridos * 7 if sube else frames_transcurridos * 7) % paso
        for yy in range(-paso, h + paso, paso):
            capa.blit(base, (0, yy + desp))
        capa.blit(self._mascara(surf), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        capa.set_alpha(alfa)
        pantalla.blit(capa, pos)

    def dibujar(self, pantalla):
        e = self.actual
        if e is None:
            return
        for elemento in e.elementos:
            elemento.dibujar(pantalla, e.frame_actual)

    # --- utilidades ---
    def _tile(self, nombre, ancho):
        clave = (nombre, ancho)
        if clave not in self._tiles:
            img = _cargar("stats", nombre)
            if img is None:
                img = pygame.Surface((ancho, ancho))
                img.fill((255, 255, 255))
            self._tiles[clave] = pygame.transform.scale(img, (ancho, ancho))
        return self._tiles[clave]

    def _mascara(self, surf):
        clave = id(surf)
        if clave not in self._mascaras:
            m = pygame.mask.from_surface(surf, 20)
            self._mascaras[clave] = m.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
        return self._mascaras[clave]