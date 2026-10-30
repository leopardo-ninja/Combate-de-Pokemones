# ----------------- MAPA DEL MODO AVENTURA -----------------
# El mundo es una cuadrícula de casillas (tiles). Cada casilla es una letra:
#   .  suelo de la zona      T  árbol / palmera      H  hierba alta (encuentros)
#   ~  agua                  #  camino               c  cactus o roca
#   f  flores                P  punto de inicio
#   b  arbusto
# Los edificios (tienda y gimnasio) se guardan aparte en EDIFICIOS.
#
# Zonas: pradera (pueblo, centro), bosque (norte), playa (este), dunas (sur-oeste).

import random
import pygame

from config import FUENTE_CHICA, BLANCO

TILE = 64
COLUMNAS, FILAS = 48, 36

# ---------- Regiones de cada zona (x, y, ancho, alto en casillas) ----------
REGIONES = [
    ("bosque", pygame.Rect(0, 0, COLUMNAS, 12)),
    ("playa", pygame.Rect(34, 12, COLUMNAS - 34, FILAS - 12)),
    ("dunas", pygame.Rect(0, 24, 34, FILAS - 24)),
    ("pradera", pygame.Rect(0, 12, 34, 12)),
]

NOMBRES_ZONA = {
    "pradera": "Pueblo Pradera",
    "bosque": "Bosque Verde",
    "playa": "Playa Azul",
    "dunas": "Dunas Doradas",
    "gimnasio": "Gimnasio",
}

# Pokémon que aparecen en la hierba alta de cada zona
ENCUENTROS_POR_ZONA = {
    "bosque": ["bulbasaur", "oddish", "bellsprout", "tangela", "exeggcute", "pikachu", "mareep"],
    "playa": ["squirtle", "psyduck", "poliwag", "horsea", "staryu"],
    "dunas": ["sandshrew", "geodude", "cubone", "phanpy", "diglett", "charmander", "vulpix", "growlithe", "ponyta"],
    "pradera": ["pikachu", "magnemite", "voltorb", "mareep", "growlithe", "oddish"],
}

PROBABILIDAD_ENCUENTRO = 0.10

# Edificios: casillas sólidas + una puerta (la casilla de la puerta se pisa para entrar)
EDIFICIOS = [
    {"tipo": "tienda", "rect": pygame.Rect(8, 13, 5, 4), "puerta": (10, 16)},
    {"tipo": "gimnasio", "rect": pygame.Rect(20, 12, 7, 5), "puerta": (23, 16)},
]

SOLIDOS = {"T", "~", "c", "b"}


def zona_en(x, y):
    for nombre, rect in REGIONES:
        if rect.collidepoint(x, y):
            return nombre
    return "pradera"


# ----------------- Generación del mundo -----------------
def _generar_mapa():
    """Construye el mapa como lista de strings (siempre el mismo gracias a la semilla)."""
    rnd = random.Random(7)
    g = [["." for _ in range(COLUMNAS)] for _ in range(FILAS)]

    def poner(x, y, letra):
        if 0 <= x < COLUMNAS and 0 <= y < FILAS:
            g[y][x] = letra

    def parche(x0, y0, w, h, letra):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                poner(x, y, letra)

    # --- Bosque: muchos árboles y claros con hierba alta ---
    for y in range(0, 12):
        for x in range(COLUMNAS):
            if rnd.random() < 0.38:
                g[y][x] = "T"
    for (x0, y0, w, h) in [(3, 3, 6, 4), (14, 2, 7, 4), (26, 5, 6, 4), (37, 2, 6, 5), (10, 8, 5, 3)]:
        parche(x0, y0, w, h, "H")

    # --- Playa: arena, agua al este, hierba de playa y alguna palmera ---
    for y in range(12, FILAS):
        for x in range(34, COLUMNAS):
            if x >= 42 + (1 if (y // 3) % 2 else 0):
                g[y][x] = "~"
            elif rnd.random() < 0.06:
                g[y][x] = "T"
    for (x0, y0, w, h) in [(35, 15, 4, 4), (36, 24, 5, 4), (35, 30, 4, 3)]:
        parche(x0, y0, w, h, "H")

    # --- Dunas: cactus/rocas dispersos y matorrales secos ---
    for y in range(24, FILAS):
        for x in range(0, 34):
            if rnd.random() < 0.07:
                g[y][x] = "c"
    for (x0, y0, w, h) in [(3, 27, 6, 4), (14, 29, 7, 4), (25, 26, 5, 5)]:
        parche(x0, y0, w, h, "H")

    # --- Pradera: flores y un par de parches de hierba ---
    for y in range(12, 24):
        for x in range(0, 34):
            if rnd.random() < 0.05:
                g[y][x] = "f"
    parche(28, 19, 5, 3, "H")
    parche(2, 19, 4, 3, "H")

    # --- Arbustos decorativos (semilla propia para no cambiar el resto del mapa) ---
    rnd_arbustos = random.Random(11)
    for y in range(1, 24):
        for x in range(1, 34):
            prob = 0.03 if y >= 12 else 0.05
            if g[y][x] == "." and rnd_arbustos.random() < prob:
                g[y][x] = "b"

    # --- Caminos que conectan todas las zonas (se trazan al final para no quedar bloqueados) ---
    for x in range(2, 42):
        poner(x, 18, "#")           # avenida este-oeste del pueblo
    for y in range(1, 34):
        poner(17, y, "#")           # camino norte-sur (bosque ↔ dunas)
    for x in range(17, 41):
        poner(x, 7, "#")            # sendero del bosque
    for y in range(18, 33):
        poner(38, y, "#")           # paseo de la playa
    for x in range(5, 30):
        poner(x, 30, "#")           # sendero de las dunas
    for y in range(18, 31):
        poner(5, y, "#")
    # Entradas a los edificios
    for e in EDIFICIOS:
        px, py = e["puerta"]
        for y in range(py + 1, 19):
            poner(px, y, "#")

    # --- Borde del mundo: árboles alrededor (agua en la playa) ---
    for x in range(COLUMNAS):
        poner(x, 0, "T")
        poner(x, FILAS - 1, "~" if x >= 34 else "T")
    for y in range(FILAS):
        poner(0, y, "T")
        poner(COLUMNAS - 1, y, "~" if y >= 12 else "T")

    # --- Despejar el pueblo y los edificios ---
    parche(7, 12, 22, 6, ".")
    for e in EDIFICIOS:
        r = e["rect"]
        parche(r.x, r.y, r.w, r.h, ".")
    poner(17, 12, "#")
    for y in range(12, 18):
        poner(17, y, "#")

    # --- Seto de arbustos entre el bosque y el pueblo (con huecos para pasar) ---
    for x in range(1, 34):
        if g[12][x] == "." and not any(e["rect"].collidepoint(x, 12) for e in EDIFICIOS) and x not in (3, 4, 31, 32):
            g[12][x] = "b"

    inicio = (17, 20)
    poner(*inicio, "P")
    return ["".join(f) for f in g], inicio


MAPA, INICIO = _generar_mapa()


def letra_en(x, y):
    if 0 <= x < COLUMNAS and 0 <= y < FILAS:
        return MAPA[y][x]
    return "T"


def edificio_en(x, y):
    for e in EDIFICIOS:
        if e["rect"].collidepoint(x, y):
            return e
    return None


def puerta_en(x, y):
    """Devuelve el edificio cuya puerta está en (x, y), o None."""
    for e in EDIFICIOS:
        if e["puerta"] == (x, y):
            return e
    return None


def es_solido(x, y):
    if puerta_en(x, y):
        return False
    if edificio_en(x, y):
        return True
    return letra_en(x, y) in SOLIDOS


# ----------------- Dibujo de casillas (pixel art 16x16 ampliado x4) -----------------
# Cada casilla se dibuja píxel a píxel en una superficie de 16x16 y luego se amplía
# a 64x64 sin suavizado, como en los Pokémon de Game Boy Advance.
# Los objetos (árboles, arbustos, rocas...) son cuadrículas de letras; cada letra es
# un color de su paleta y "." es transparente.

PX = 16                   # tamaño de una casilla en píxeles de dibujo
ESCALA = TILE // PX       # 4

# ---------- Colores del suelo: (base, oscuro, claro) ----------
COLORES_SUELO = {
    "pasto": ((120, 200, 104), (88, 168, 80), (160, 224, 128)),
    "pasto_osc": ((80, 160, 80), (56, 128, 64), (112, 184, 96)),
    "arena": ((248, 232, 168), (224, 200, 136), (255, 246, 206)),
    "arena_d": ((232, 192, 120), (204, 160, 96), (246, 214, 152)),
    "camino": ((216, 184, 128), (176, 140, 92), (234, 206, 156)),
    "agua": ((80, 152, 232), (56, 120, 208), (152, 200, 248)),
}
ESPUMA = (240, 248, 255)

SUELO_POR_ZONA = {"pradera": "pasto", "bosque": "pasto_osc", "playa": "arena", "dunas": "arena_d"}

# Cuando dos suelos se tocan, el de mayor prioridad "invade" un poco al otro
PRIORIDAD = {"agua": 0, "camino": 1, "arena": 2, "arena_d": 2.5, "pasto": 3, "pasto_osc": 4}

# ---------- Objetos dibujados con letras ----------
ARBOL_REDONDO = [
    "....KKKKKKKK....",
    "..KKLLLMMMMMKK..",
    ".KLLLLMMMMMMDDK.",
    ".KLLMMMMMMMMMDK.",
    "KLLMMMLMMMMMMDDK",
    "KLMMMLLMMMMMDDDK",
    "KMMMMMMMMMMDDMDK",
    "KMMMMMMMMMDDDDDK",
    "KDMMMMMMMDDMDDDK",
    ".KDMDMMMDDDDDDK.",
    ".KDDDDDDDDDDDDK.",
    "..KKDDKTTKDDKK..",
    "....KKtTTtKK....",
    "......KTTtK.....",
    "......KTTtK.....",
    ".....KKKKKKK....",
]
PINO = [
    ".......KK.......",
    "......KLMK......",
    ".....KLMMDK.....",
    "....KLMMMDDK....",
    ".....KMMDDK.....",
    "....KLMMMDDK....",
    "...KLMMMMMDDK...",
    "....KMMMDDDK....",
    "...KLMMMMMDDK...",
    "..KLMMMMMMMDDK..",
    ".KLMMMMMMMMMDDK.",
    ".KKDMMDMMDDDDKK.",
    "...KKDDDDDDKK...",
    "......KTtK......",
    "......KTtK......",
    ".....KKKKKK.....",
]
PALMERA = [
    "....KK....KK....",
    "..KKLLK..KLLKK..",
    ".KLLMMMKKMMMLLK.",
    "KLMMKKMMMMKKMMLK",
    "KMK..KMMMMK..KMK",
    "KK..KMKTTKMK..KK",
    "...KMK.KtK.KMK..",
    "...KK..KTK..KK..",
    ".......KTtK.....",
    ".......KtTK.....",
    "......KTtK......",
    "......KtTK......",
    "......KTtK......",
    ".....KTtTK......",
    ".....KtTtK......",
    "....KKKKKKK.....",
]
ARBOL_SECO = [
    "..K........K....",
    ".KtK..K...KtK...",
    "..KtK.KtK.KtK...",
    "...KtKKtKKtK....",
    "....KtTtTtK.....",
    ".KK..KTtTK..KK..",
    "KtTK.KTTtK.KtK..",
    ".KTtKKTtTKKtK...",
    "..KKTTtTTtKK....",
    ".....KTtTK......",
    ".....KTTtK......",
    ".....KtTTK......",
    ".....KTtTK......",
    "....KTTtTTK.....",
    "...KtTTtTTtK....",
    "....KKKKKKK.....",
]
CACTUS = [
    "......KKK.......",
    ".....KLMMK......",
    ".....KLMDK......",
    "..KK.KLMDK......",
    ".KLMKKLMDK.KK...",
    ".KLMKKLMDKKMDK..",
    ".KLMKKLMDKKMDK..",
    ".KLMMMLMDMMMDK..",
    "..KKMMLMDDDDK...",
    "....KKLMDKKK....",
    ".....KLMDK......",
    ".....KLMDK......",
    ".....KLMDK......",
    ".....KLMDK......",
    "....KKKKKKK.....",
    "................",
]
ROCA = [
    "................",
    "................",
    "................",
    ".....KKKKKK.....",
    "....KLLLMMMK....",
    "...KLLMMMMMDK...",
    "..KLLMMMMMMDDK..",
    "..KLMMMMMMDDDK..",
    ".KLMMMMMMMMDDDK.",
    ".KMMMMMMMMDDDDK.",
    ".KDMMMMMDDDDDDK.",
    "..KDDDDDDDDDDK..",
    "...KKKKKKKKKK...",
    "................",
    "................",
    "................",
]
ARBUSTO = [
    "................",
    "................",
    ".....KKKKKK.....",
    "...KKLLMMMMKK...",
    "..KLLLMMMMMMDK..",
    ".KLLMMMLMMMMDDK.",
    ".KLMMMLLMMMDDDK.",
    "KLMMMMMMMMMMDMDK",
    "KMMMLMMMMMDDDDDK",
    "KMMLLMMMMDDMDDDK",
    "KDMMMMMMDDDDDDDK",
    ".KDDMMDDDDDDDDK.",
    "..KKDDDDDDDDKK..",
    "....KKKKKKKK....",
    "................",
    "................",
]
# Mata de hierba alta (8x8). La casilla se forma con 2 filas de matas desplazadas.
MATA = [
    "...D....",
    "..DLD.D.",
    ".DLLDDLD",
    ".DLGLLLD",
    "DLGGLGLD",
    "DGGGGGGD",
    "DGGgGGgD",
    ".DDDDDD.",
]

PALETAS = {
    "arbol": {"K": (24, 64, 32), "D": (40, 112, 48), "M": (64, 160, 64), "L": (120, 208, 96),
              "T": (136, 88, 48), "t": (96, 60, 32)},
    "pino": {"K": (16, 48, 32), "D": (24, 96, 48), "M": (40, 136, 64), "L": (88, 184, 96),
             "T": (128, 84, 48), "t": (88, 56, 32)},
    "palmera": {"K": (32, 60, 24), "D": (40, 112, 48), "M": (64, 160, 64), "L": (128, 208, 96),
                "T": (176, 128, 72), "t": (136, 96, 48)},
    "seco": {"K": (64, 40, 24), "T": (160, 112, 64), "t": (120, 80, 44)},
    "cactus": {"K": (24, 72, 40), "L": (120, 200, 104), "M": (72, 160, 72), "D": (48, 120, 56)},
    "roca": {"K": (64, 64, 72), "L": (208, 208, 216), "M": (168, 168, 180), "D": (120, 120, 132)},
    "arbusto": {"K": (24, 72, 32), "D": (48, 120, 56), "M": (72, 168, 72), "L": (136, 216, 112)},
}
PALETA_HIERBA = {
    "pradera": {"D": (40, 120, 56), "G": (72, 168, 72), "L": (120, 208, 96), "g": (56, 144, 64)},
    "bosque": {"D": (24, 88, 40), "G": (48, 136, 56), "L": (88, 176, 80), "g": (36, 112, 48)},
    "playa": {"D": (96, 128, 48), "G": (144, 176, 72), "L": (192, 216, 112), "g": (120, 152, 56)},
    "dunas": {"D": (128, 96, 40), "G": (176, 140, 64), "L": (216, 184, 104), "g": (152, 116, 52)},
}
COLORES_FLOR = [(240, 80, 96), (248, 216, 72), (250, 250, 250), (200, 120, 232), (248, 144, 64)]


def _ruido(x, y, extra=0):
    return random.Random(x * 7919 + y * 104729 + extra * 31337)


def _pixel(sup, x, y, color):
    if 0 <= x < sup.get_width() and 0 <= y < sup.get_height():
        sup.set_at((x, y), color)


def _pintar(sup, filas, paleta, ox=0, oy=0):
    for y, fila in enumerate(filas):
        for x, letra in enumerate(fila):
            if letra != "." and letra in paleta:
                _pixel(sup, ox + x, oy + y, paleta[letra])


def _oscurecer(color, factor=0.72):
    return tuple(int(c * factor) for c in color[:3])


def _sombra(sup, x0, x1, y0, y1):
    """Oscurece el suelo bajo un objeto (sombra ovalada)."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                _pixel(sup, x, y, _oscurecer(sup.get_at((x, y))))


# ---------- Tipo de suelo de una casilla ----------
def tipo_suelo(x, y):
    if not (0 <= x < COLUMNAS and 0 <= y < FILAS):
        return None
    letra = MAPA[y][x]
    if letra == "~":
        return "agua"
    if letra in ("#", "P"):
        return "camino"
    return SUELO_POR_ZONA[zona_en(x, y)]


def _textura_suelo(sup, tipo, x, y):
    base, oscuro, claro = COLORES_SUELO[tipo]
    sup.fill(base)
    r = _ruido(x, y)
    if tipo in ("pasto", "pasto_osc"):
        for _ in range(r.randint(2, 5)):              # matitas en forma de "^"
            tx, ty = r.randrange(0, 14), r.randrange(1, 15)
            _pixel(sup, tx, ty + 1, oscuro)
            _pixel(sup, tx + 1, ty, oscuro)
            _pixel(sup, tx + 2, ty + 1, oscuro)
        for _ in range(r.randint(1, 3)):
            _pixel(sup, r.randrange(16), r.randrange(16), claro)
    elif tipo in ("arena", "arena_d"):
        for _ in range(r.randint(3, 6)):
            _pixel(sup, r.randrange(16), r.randrange(16), oscuro)
        for _ in range(r.randint(1, 3)):
            _pixel(sup, r.randrange(16), r.randrange(16), claro)
        if tipo == "arena_d" and r.random() < 0.5:     # ondas de las dunas
            sx, sy = r.randrange(0, 9), r.randrange(3, 13)
            for i in range(7):
                dy = 1 if i in (0, 6) else 0
                _pixel(sup, sx + i, sy + dy, oscuro)
                _pixel(sup, sx + i, sy + dy - 1, claro)
    elif tipo == "camino":
        for _ in range(r.randint(2, 4)):              # piedritas
            px, py = r.randrange(1, 15), r.randrange(1, 15)
            _pixel(sup, px, py, oscuro)
            _pixel(sup, px - 1, py - 1, claro)
    elif tipo == "agua":
        for _ in range(r.randint(2, 3)):              # olitas
            wx, wy = r.randrange(0, 12), r.randrange(2, 14)
            for i in range(4):
                _pixel(sup, wx + i, wy, claro)
            _pixel(sup, wx + 1, wy + 1, oscuro)
            _pixel(sup, wx + 2, wy + 1, oscuro)


_LADOS = {"arriba": (0, -1), "abajo": (0, 1), "izq": (-1, 0), "der": (1, 0)}


def _pixel_borde(lado, d, i):
    """Coordenada del píxel a distancia d del lado indicado, en la posición i a lo largo del borde."""
    if lado == "arriba":
        return i, d
    if lado == "abajo":
        return i, PX - 1 - d
    if lado == "izq":
        return d, i
    return PX - 1 - d, i


def _mezclar_bordes(sup, tipo, x, y):
    """Bordes suaves entre suelos distintos y orilla con espuma junto al agua."""
    base, oscuro, claro = COLORES_SUELO[tipo]
    for n, (lado, (dx, dy)) in enumerate(_LADOS.items()):
        vecino = tipo_suelo(x + dx, y + dy)
        if vecino is None or vecino == tipo:
            continue
        r = _ruido(x, y, n + 1)
        if tipo == "agua":                           # orilla: arena, espuma y agua clara
            color_vecino = COLORES_SUELO[vecino][0]
            for i in range(PX):
                _pixel(sup, *_pixel_borde(lado, 0, i), color_vecino if r.random() < 0.75 else ESPUMA)
                _pixel(sup, *_pixel_borde(lado, 1, i), ESPUMA if r.random() < 0.8 else color_vecino)
                if r.random() < 0.6:
                    _pixel(sup, *_pixel_borde(lado, 2, i), ESPUMA if r.random() < 0.3 else claro)
        elif vecino == "agua":                       # arena mojada junto al agua
            for i in range(PX):
                _pixel(sup, *_pixel_borde(lado, 0, i), oscuro)
                if r.random() < 0.45:
                    _pixel(sup, *_pixel_borde(lado, 1, i), oscuro)
        elif PRIORIDAD[vecino] > PRIORIDAD[tipo]:    # el vecino invade un poco esta casilla
            color_vecino = COLORES_SUELO[vecino][0]
            for i in range(PX):
                prof = 1 + (1 if r.random() < 0.45 else 0)
                for d in range(prof):
                    _pixel(sup, *_pixel_borde(lado, d, i), color_vecino)
                if tipo == "camino":
                    _pixel(sup, *_pixel_borde(lado, prof, i), oscuro)


def _hierba_alta(sup, zona):
    paleta = PALETA_HIERBA[zona]
    for ox, oy in [(0, 0), (8, 0), (-4, 8), (4, 8), (12, 8)]:
        _pintar(sup, MATA, paleta, ox, oy)


def _flores(sup, x, y):
    r = _ruido(x, y, 9)
    for _ in range(r.randint(2, 3)):
        cx, cy = r.randrange(2, 14), r.randrange(2, 14)
        color = r.choice(COLORES_FLOR)
        _pixel(sup, cx, cy + 2, (56, 136, 64))
        for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            _pixel(sup, cx + ddx, cy + ddy, color)
        _pixel(sup, cx, cy, (248, 200, 48))


def _objeto(sup, letra, zona):
    if letra == "T":
        if zona == "playa":
            _sombra(sup, 3, 12, 13, 15)
            _pintar(sup, PALMERA, PALETAS["palmera"])
        elif zona == "dunas":
            _sombra(sup, 3, 12, 13, 15)
            _pintar(sup, ARBOL_SECO, PALETAS["seco"])
        elif zona == "bosque":
            _sombra(sup, 2, 13, 12, 15)
            _pintar(sup, PINO, PALETAS["pino"])
        else:
            _sombra(sup, 1, 14, 12, 15)
            _pintar(sup, ARBOL_REDONDO, PALETAS["arbol"])
    elif letra == "c":
        _sombra(sup, 2, 13, 11, 15)
        if zona == "dunas":
            _pintar(sup, CACTUS, PALETAS["cactus"])
        else:
            _pintar(sup, ROCA, PALETAS["roca"])
    elif letra == "b":
        _sombra(sup, 1, 14, 10, 14)
        _pintar(sup, ARBUSTO, PALETAS["arbusto"])


def crear_tile(letra, zona, x, y):
    """Dibuja una casilla del mapa (16x16) y la devuelve ampliada a 64x64."""
    sup = pygame.Surface((PX, PX))
    tipo = tipo_suelo(x, y) or SUELO_POR_ZONA[zona]
    _textura_suelo(sup, tipo, x, y)
    _mezclar_bordes(sup, tipo, x, y)
    if letra == "H":
        _hierba_alta(sup, zona)
    elif letra == "f":
        _flores(sup, x, y)
    else:
        _objeto(sup, letra, zona)
    return pygame.transform.scale(sup, (TILE, TILE))


def crear_hierba_delante(zona):
    """Mitad inferior de la hierba alta: se dibuja encima del jugador para que 'se meta' en ella."""
    sup = pygame.Surface((PX, PX), pygame.SRCALPHA)
    _hierba_alta(sup, zona)
    grande = pygame.transform.scale(sup, (TILE, TILE))
    recorte = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    corte = 9 * ESCALA
    recorte.blit(grande, (0, corte), pygame.Rect(0, corte, TILE, TILE - corte))
    return recorte


# ----------------- Edificios (pixel art) -----------------
def _techo(s, rect, base, oscuro, claro, contorno):
    """Techo de tejas: franjas horizontales con juntas alternadas."""
    pygame.draw.rect(s, base, rect)
    for yy in range(rect.y + 3, rect.bottom, 4):
        pygame.draw.line(s, oscuro, (rect.x, yy), (rect.right - 1, yy))
        desfase = 0 if ((yy - rect.y) // 4) % 2 else 4
        for xx in range(rect.x + desfase, rect.right, 8):
            pygame.draw.line(s, oscuro, (xx, yy - 3), (xx, yy - 1))
    pygame.draw.line(s, claro, (rect.x + 1, rect.y + 1), (rect.right - 2, rect.y + 1))
    pygame.draw.rect(s, contorno, rect, 1)


def _ventana(s, rect, contorno):
    pygame.draw.rect(s, (168, 216, 248), rect)
    pygame.draw.line(s, (232, 248, 255), (rect.x + 1, rect.bottom - 3), (rect.x + 4, rect.y + 1))
    pygame.draw.line(s, (232, 248, 255), (rect.x + 3, rect.bottom - 2), (rect.x + 6, rect.y + 2))
    pygame.draw.line(s, (104, 152, 200), (rect.centerx, rect.y), (rect.centerx, rect.bottom - 1))
    pygame.draw.rect(s, contorno, rect, 1)
    pygame.draw.line(s, (200, 200, 208), (rect.x - 1, rect.bottom), (rect.right, rect.bottom))  # alféizar


def _edificio_tienda(w, h, puerta_x):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    K = (48, 44, 56)
    pared, pared_osc = (240, 236, 224), (204, 198, 186)
    # Pared con franja azul
    pared_r = pygame.Rect(3, 26, w - 6, h - 26)
    pygame.draw.rect(s, pared, pared_r)
    pygame.draw.rect(s, (88, 128, 216), (3, h - 9, w - 6, 5))
    pygame.draw.line(s, (56, 92, 176), (3, h - 4), (w - 4, h - 4))
    pygame.draw.rect(s, K, pared_r, 1)
    # Techo azul y sombra del alero
    _techo(s, pygame.Rect(0, 3, w, 25), (72, 120, 216), (48, 88, 176), (136, 176, 240), K)
    pygame.draw.line(s, pared_osc, (4, 28), (w - 5, 28))
    pygame.draw.line(s, pared_osc, (4, 29), (w - 5, 29))
    # Cartel
    pygame.draw.rect(s, (40, 72, 160), (w // 2 - 18, 20, 36, 9))
    pygame.draw.rect(s, K, (w // 2 - 18, 20, 36, 9), 1)
    # Ventanas
    _ventana(s, pygame.Rect(9, 35, 14, 10), K)
    _ventana(s, pygame.Rect(w - 23, 35, 14, 10), K)
    # Puertas automáticas de vidrio
    puerta = pygame.Rect(puerta_x + 2, h - 19, 12, 19)
    pygame.draw.rect(s, (96, 104, 120), puerta.inflate(2, 2))
    pygame.draw.rect(s, (152, 200, 240), puerta)
    pygame.draw.line(s, (96, 104, 120), (puerta.centerx, puerta.y), (puerta.centerx, puerta.bottom))
    pygame.draw.line(s, (224, 240, 255), (puerta.x + 1, puerta.y + 2), (puerta.x + 1, puerta.bottom - 3))
    pygame.draw.line(s, (224, 240, 255), (puerta.centerx + 1, puerta.y + 2), (puerta.centerx + 1, puerta.bottom - 3))
    pygame.draw.rect(s, K, puerta.inflate(2, 2), 1)
    return s


def _edificio_gimnasio(w, h, puerta_x):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    K = (56, 40, 40)
    pared, pared_osc = (224, 212, 192), (188, 174, 152)
    pared_r = pygame.Rect(4, 34, w - 8, h - 34)
    pygame.draw.rect(s, pared, pared_r)
    # Base de piedra
    pygame.draw.rect(s, (168, 160, 152), (4, h - 6, w - 8, 6))
    for xx in range(6, w - 6, 8):
        pygame.draw.line(s, (128, 120, 112), (xx, h - 6), (xx, h - 1))
    pygame.draw.rect(s, K, pared_r, 1)
    # Columnas
    for cx in (5, 18, w - 24, w - 11):
        col = pygame.Rect(cx, 34, 6, h - 40)
        pygame.draw.rect(s, (244, 236, 222), col)
        pygame.draw.line(s, pared_osc, (col.right - 1, col.y), (col.right - 1, col.bottom - 1))
        pygame.draw.rect(s, K, col, 1)
    # Techo rojo
    _techo(s, pygame.Rect(0, 3, w, 33), (208, 64, 56), (160, 40, 40), (240, 120, 104), K)
    pygame.draw.line(s, pared_osc, (5, 36), (w - 6, 36))
    # Emblema de Poké Ball en el techo
    c = (w // 2, 15)
    pygame.draw.circle(s, K, c, 10)
    pygame.draw.circle(s, (248, 248, 248), c, 9)
    pygame.draw.rect(s, (232, 72, 64), (c[0] - 9, c[1] - 9, 19, 9))
    pygame.draw.circle(s, K, c, 10, 1)
    # recortar el rojo fuera del círculo
    for yy in range(c[1] - 10, c[1]):
        for xx in range(c[0] - 10, c[0] + 11):
            if (xx - c[0]) ** 2 + (yy - c[1]) ** 2 > 90 and s.get_at((xx, yy))[:3] == (232, 72, 64):
                s.set_at((xx, yy), (208, 64, 56))
    pygame.draw.line(s, K, (c[0] - 9, c[1]), (c[0] + 9, c[1]))
    pygame.draw.circle(s, K, c, 3)
    pygame.draw.circle(s, (248, 248, 248), c, 2)
    # Cartel
    pygame.draw.rect(s, (136, 32, 32), (w // 2 - 24, 28, 48, 9))
    pygame.draw.rect(s, K, (w // 2 - 24, 28, 48, 9), 1)
    # Ventanas
    for vx in (27, 40, w - 52, w - 39):
        _ventana(s, pygame.Rect(vx, 44, 10, 12), K)
    # Puerta doble de madera
    puerta = pygame.Rect(puerta_x + 1, h - 22, 14, 22)
    pygame.draw.rect(s, (144, 96, 56), puerta)
    pygame.draw.line(s, (104, 64, 32), (puerta.centerx, puerta.y), (puerta.centerx, puerta.bottom))
    for yy in (puerta.y + 5, puerta.y + 12):
        pygame.draw.line(s, (176, 124, 76), (puerta.x + 1, yy), (puerta.right - 2, yy))
    pygame.draw.rect(s, (248, 208, 64), (puerta.centerx - 3, puerta.centery, 2, 2))
    pygame.draw.rect(s, (248, 208, 64), (puerta.centerx + 1, puerta.centery, 2, 2))
    pygame.draw.rect(s, K, puerta, 1)
    return s


def _dibujar_edificio(sup, e):
    r = e["rect"]
    w, h = r.w * PX, r.h * PX
    puerta_x = (e["puerta"][0] - r.x) * PX
    if e["tipo"] == "tienda":
        pequeño, texto, centro_cartel = _edificio_tienda(w, h, puerta_x), "TIENDA", (w // 2, 24.5)
    else:
        pequeño, texto, centro_cartel = _edificio_gimnasio(w, h, puerta_x), "GIMNASIO", (w // 2, 32.5)
    grande = pygame.transform.scale(pequeño, (w * ESCALA, h * ESCALA))
    ox, oy = r.x * TILE, r.y * TILE
    sup.blit(grande, (ox, oy))
    etiqueta = FUENTE_CHICA.render(texto, True, BLANCO)
    centro = (ox + int(centro_cartel[0] * ESCALA), oy + int(centro_cartel[1] * ESCALA))
    sup.blit(etiqueta, etiqueta.get_rect(center=centro))


_SUPERFICIE_MAPA = None


def superficie_mapa():
    """Dibuja el mapa completo una sola vez y lo guarda."""
    global _SUPERFICIE_MAPA
    if _SUPERFICIE_MAPA is None:
        sup = pygame.Surface((COLUMNAS * TILE, FILAS * TILE))
        for y in range(FILAS):
            for x in range(COLUMNAS):
                sup.blit(crear_tile(letra_en(x, y), zona_en(x, y), x, y), (x * TILE, y * TILE))
        for e in EDIFICIOS:
            _dibujar_edificio(sup, e)
        _SUPERFICIE_MAPA = sup
    return _SUPERFICIE_MAPA
