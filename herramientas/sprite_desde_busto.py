# ----------------- MUÑEQUITO DEL MAPA A PARTIR DEL RETRATO -----------------
# Crea assets/entrenadores/<nombre>/caminar.png (3 columnas x 4 filas de 32x48) usando:
#   - la CABEZA: el retrato (busto.png) reducido al tamaño del sprite, limpiado y con
#     ojos/gafas de estilo chibi encima. De ahí salen también la vista de espaldas y de perfil.
#   - el CUERPO: una plantilla con caminata (assets/entrenadores/cuerpo_base.png),
#     recoloreada con la ropa de cada personaje.
#
# Uso (desde la carpeta del proyecto):
#   .venv/bin/python herramientas/sprite_desde_busto.py            (los tres)
#   .venv/bin/python herramientas/sprite_desde_busto.py leopardo   (uno)
#
# Para un personaje nuevo: hacer su busto.png y agregar una entrada en PERSONAJES.

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from importar_ia import celdas_a_pixeles
from foto_a_pixel import paleta_mediana, mas_cercano

W, H = 32, 48
CARPETA = os.path.join(RAIZ, "assets", "entrenadores")
FILAS = ["abajo", "izquierda", "derecha", "arriba"]
ALTO_CABEZA = 24          # filas 0..23; el cuello del cuerpo empieza en la 24

# Colores de la plantilla del cuerpo -> rol de cada color
ROLES_CUERPO = {
    (30, 22, 24): "contorno",
    (250, 250, 250): "camiseta", (210, 212, 222): "camiseta_sombra",
    (72, 150, 92): "chaqueta", (46, 108, 64): "chaqueta_sombra",
    (56, 68, 108): "pantalon", (38, 46, 78): "pantalon_sombra",
    (246, 212, 186): "piel", (218, 172, 146): "piel_sombra",
    (112, 74, 48): "zapato", (62, 42, 30): "suela",
    (92, 62, 40): "cinturon", (206, 212, 220): "hebilla",
}

PERSONAJES = {
    "tortuga": {
        # caja de la cabeza en el busto (x0, y0, x1, y1), ancho de la cabeza en el sprite
        "caja": (22, 4, 106, 92), "ancho": 26,
        "ojos": ((52, 57), (78, 57)),            # posición de los ojos en el busto
        "gafas": ("redondas", (150, 156, 170), (214, 220, 230)),
        "colores": {
            "contorno": (30, 20, 34), "piel": (240, 190, 160), "piel_sombra": (209, 139, 116),
            "camiseta": (251, 251, 251), "camiseta_sombra": (200, 202, 214),
            "chaqueta": (105, 152, 99), "chaqueta_sombra": (75, 115, 76),
            "pantalon": (56, 68, 108), "pantalon_sombra": (38, 46, 78),
            "zapato": (112, 74, 48), "suela": (62, 42, 30), "cinturon": (92, 62, 40), "hebilla": (206, 212, 220),
        },
        "pelo": [(89, 67, 61), (59, 44, 45), (43, 27, 35), (140, 112, 100)],
        "extras": ["cadena"],
    },
    "leopardo": {
        "caja": (18, 6, 112, 100), "ancho": 28,
        "ojos": ((50, 66), (80, 66)),
        "gafas": ("cuadradas", (60, 56, 60), (107, 106, 107)),
        "colores": {
            "contorno": (26, 16, 24), "piel": (245, 192, 160), "piel_sombra": (203, 127, 101),
            "camiseta": (62, 100, 192), "camiseta_sombra": (44, 72, 150),
            "chaqueta": (56, 94, 184), "chaqueta_sombra": (35, 50, 120),
            "pantalon": (72, 82, 122), "pantalon_sombra": (52, 60, 92),
            "zapato": (240, 240, 240), "suela": (180, 182, 192), "cinturon": (35, 50, 120), "hebilla": (35, 50, 120),
        },
        "pelo": [(176, 86, 44), (120, 33, 30), (93, 26, 21), (214, 128, 70)],
        "extras": ["cordones", "capucha"],
    },
    "tullio": {
        "caja": (28, 10, 100, 98), "ancho": 24,
        "ojos": ((58, 60), (86, 61)),
        "gafas": None,
        "colores": {
            "contorno": (12, 10, 16), "piel": (240, 200, 164), "piel_sombra": (206, 154, 132),
            "camiseta": (44, 42, 50), "camiseta_sombra": (30, 28, 34),
            "chaqueta": (44, 42, 50), "chaqueta_sombra": (30, 28, 34),
            "pantalon": (36, 36, 42), "pantalon_sombra": (24, 24, 28),
            "zapato": (22, 22, 26), "suela": (70, 70, 76), "cinturon": (22, 22, 26), "hebilla": (166, 168, 170),
        },
        "pelo": [(63, 51, 48), (40, 34, 36), (24, 22, 26), (110, 92, 84)],
        "extras": ["cadena", "barba"],
    },
}


# ----------------- Cabeza -----------------
def _mayoria(pix, ancho, alto):
    nuevos = [fila[:] for fila in pix]
    for y in range(alto):
        for x in range(ancho):
            if pix[y][x] is None:
                continue
            vecinos = [pix[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                       if 0 <= x + dx < ancho and 0 <= y + dy < alto and pix[y + dy][x + dx] is not None]
            if vecinos and pix[y][x] not in vecinos:
                comun = max(set(vecinos), key=vecinos.count)
                if vecinos.count(comun) >= 3:
                    nuevos[y][x] = comun
    return nuevos


def cabeza_de_frente(nombre, cfg):
    """Reduce la cabeza del busto, la limpia y le pone contorno. Devuelve (superficie, ojos)."""
    busto = pygame.image.load(os.path.join(CARPETA, nombre, "busto.png"))
    x0, y0, x1, y1 = cfg["caja"]
    ancho, alto = cfg["ancho"], ALTO_CABEZA - 1
    pix = celdas_a_pixeles(busto.subsurface((x0, y0, x1 - x0, y1 - y0)), ancho, alto)
    opacos = [c[:3] for f in pix for c in f if c[3]]
    paleta = paleta_mediana(opacos, 10)
    pix = [[paleta[mas_cercano(c[:3], paleta)] if c[3] else None for c in f] for f in pix]
    pix = _mayoria(pix, ancho, alto)
    sup = pygame.Surface((ancho + 2, alto + 1), pygame.SRCALPHA)
    for y, f in enumerate(pix):
        for x, c in enumerate(f):
            if c:
                sup.set_at((x + 1, y), c)
    contorno = cfg["colores"]["contorno"]
    _contorno(sup, contorno)
    ojos = [(round((bx - x0) / (x1 - x0) * ancho) + 1, round((by - y0) / (y1 - y0) * alto)) for bx, by in cfg["ojos"]]
    return sup, ojos


def _contorno(sup, color):
    borde = []
    for y in range(sup.get_height()):
        for x in range(sup.get_width()):
            if sup.get_at((x, y)).a == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < sup.get_width() and 0 <= ny < sup.get_height() and sup.get_at((nx, ny)).a:
                        borde.append((x, y))
                        break
    for p in borde:
        sup.set_at(p, color)


def _ojo(sup, x, y, cfg, mirando=0):
    """Ojo chibi: 2x2 oscuro con un brillo. 'mirando' desplaza la pupila (perfil)."""
    c = cfg["colores"]
    oscuro = (34, 24, 28)
    for dx in (0, 1):
        for dy in (0, 1):
            sup.set_at((x + dx, y + dy), oscuro)
    sup.set_at((x + (1 if mirando > 0 else 0), y), (250, 250, 250))
    sup.set_at((x - 1, y - 1), c["contorno"])          # pestaña / párpado
    sup.set_at((x, y - 1), c["contorno"])
    sup.set_at((x + 1, y - 1), c["contorno"])


def _gafas(sup, x, y, cfg):
    tipo, marco, brillo = cfg["gafas"]
    r = pygame.Rect(x - 2, y - 2, 6, 5)
    if tipo == "redondas":
        puntos = [(r.x + 1, r.y), (r.x + 2, r.y), (r.x + 3, r.y), (r.x + 4, r.y),
                  (r.x, r.y + 1), (r.x, r.y + 2), (r.x, r.y + 3), (r.right - 1, r.y + 1), (r.right - 1, r.y + 2),
                  (r.right - 1, r.y + 3), (r.x + 1, r.bottom - 1), (r.x + 2, r.bottom - 1), (r.x + 3, r.bottom - 1),
                  (r.x + 4, r.bottom - 1)]
    else:
        puntos = [(xx, r.y) for xx in range(r.x, r.right)] + [(xx, r.y + 1) for xx in range(r.x, r.right)] + \
                 [(r.x, yy) for yy in range(r.y, r.bottom)] + [(r.right - 1, yy) for yy in range(r.y, r.bottom)] + \
                 [(xx, r.bottom - 1) for xx in range(r.x, r.right)]
    for p in puntos:
        sup.set_at(p, marco)
    sup.set_at((r.x + 1, r.y + (1 if tipo == "redondas" else 2)), brillo)


def preparar_cara(sup, ojos, cfg):
    """Limpia la zona de los ojos y dibuja ojos, gafas, boca (y barba) de estilo chibi."""
    c = cfg["colores"]
    (xi, yi), (xd, yd) = ojos
    y = round((yi + yd) / 2)
    # piel limpia alrededor de los ojos
    for x in range(xi - 2, xd + 4):
        for yy in range(y - 2, y + 3):
            p = sup.get_at((x, yy))
            if p.a and (p.r, p.g, p.b) != c["contorno"]:
                sup.set_at((x, yy), c["piel"])
    _ojo(sup, xi, y, cfg)
    _ojo(sup, xd, y, cfg)
    if cfg["gafas"]:
        _gafas(sup, xi, y, cfg)
        _gafas(sup, xd, y, cfg)
        for x in range(xi + 4, xd - 2):
            sup.set_at((x, y - 1), cfg["gafas"][1])        # puente
    cx = (xi + xd + 1) // 2
    sup.set_at((cx, y + 3), c["piel_sombra"])              # nariz
    sup.set_at((cx - 1, y + 5), (176, 96, 96))             # boca
    sup.set_at((cx, y + 5), (176, 96, 96))
    if "barba" in cfg["extras"]:
        barba = (150, 112, 96)
        for x in range(cx - 4, cx + 5):
            for yy in range(y + 4, sup.get_height() - 1):
                p = sup.get_at((x, yy))
                if p.a and (p.r, p.g, p.b) != c["contorno"] and (x + yy) % 2 == 0 and abs(x - cx) + (yy - y) > 5:
                    sup.set_at((x, yy), barba)
    return y


def _es_pelo(color, cfg):
    """True si el color se parece más al pelo que a la piel."""
    c = cfg["colores"]
    candidatos = [(k, 1) for k in cfg["pelo"]] + [(c["piel"], 0), (c["piel_sombra"], 0)]
    cercano = min(candidatos, key=lambda t: sum((a - b) ** 2 for a, b in zip(t[0], color)))
    return cercano[1] == 1


def _columnas_de_pelo(frente, cfg, y_limite):
    """Para cada columna, los colores de pelo de la vista de frente (de arriba hacia abajo)."""
    c = cfg["colores"]
    columnas = {}
    for x in range(frente.get_width()):
        pelo = []
        for y in range(y_limite):
            p = frente.get_at((x, y))
            if p.a and (p.r, p.g, p.b) != c["contorno"] and _es_pelo((p.r, p.g, p.b), cfg):
                pelo.append((p.r, p.g, p.b))
        columnas[x] = pelo
    return columnas


def _pelo_estirado(columna, y, y_ini, y_fin, cfg):
    """Color de pelo para la fila y, estirando la columna de frente entre y_ini e y_fin."""
    if not columna:
        return cfg["pelo"][1]
    t = (y - y_ini) / max(1, y_fin - y_ini)
    return columna[min(len(columna) - 1, int(t * len(columna)))]


def cabeza_de_espaldas(frente, y_ojos, cfg):
    """Vista de espaldas: todo pelo (con la textura del pelo de frente estirada), nuca abajo."""
    sup = frente.copy()
    c = cfg["colores"]
    w, h = sup.get_size()
    y_nuca = y_ojos + 5
    columnas = _columnas_de_pelo(frente, cfg, y_ojos - 2)      # solo el pelo por encima de las gafas
    for x in range(w):
        ys = [y for y in range(h) if sup.get_at((x, y)).a and tuple(sup.get_at((x, y)))[:3] != c["contorno"]]
        if not ys:
            continue
        y_ini = ys[0]
        for y in ys:
            if y <= y_nuca:
                sup.set_at((x, y), _pelo_estirado(columnas[x], y, y_ini, y_nuca, cfg))
            elif y == y_nuca + 1:
                sup.set_at((x, y), cfg["pelo"][1])               # puntas del pelo en la nuca
            else:
                sup.set_at((x, y), c["piel_sombra"])              # cuello
    return sup


def cabeza_de_perfil(frente, ojos, y_ojos, cfg):
    """Perfil mirando a la derecha: atrás pelo, delante la cara con un ojo y la nariz."""
    sup = frente.copy()
    c = cfg["colores"]
    w, h = sup.get_size()
    corte = w // 2 - 1
    columnas = _columnas_de_pelo(frente, cfg, y_ojos - 2)
    y_nuca = y_ojos + 5
    for x in range(w):
        ys = [y for y in range(h) if sup.get_at((x, y)).a and tuple(sup.get_at((x, y)))[:3] != c["contorno"]]
        if not ys:
            continue
        for y in ys:
            p = tuple(sup.get_at((x, y)))[:3]
            if x < corte:
                if y <= y_nuca:
                    sup.set_at((x, y), _pelo_estirado(columnas[x], y, ys[0], y_nuca, cfg))
                else:
                    sup.set_at((x, y), c["piel_sombra"])
            elif not _es_pelo(p, cfg) or y >= y_ojos - 2:
                # debajo de la línea de las gafas todo es cara (sin restos de gafas o capucha)
                sup.set_at((x, y), c["piel"] if x > corte + 1 else c["piel_sombra"])
    # barba de perfil
    if "barba" in cfg["extras"]:
        for x in range(corte + 2, w):
            for y in range(y_ojos + 4, h - 1):
                p = sup.get_at((x, y))
                if p.a and tuple(p)[:3] != c["contorno"] and (x + y) % 2 == 0:
                    sup.set_at((x, y), (150, 112, 96))
    # oreja
    for dy in range(-1, 3):
        sup.set_at((corte, y_ojos + dy), c["piel_sombra"])
        sup.set_at((corte + 1, y_ojos + dy), c["piel"])
    sup.set_at((corte + 1, y_ojos), c["piel_sombra"])
    # ojo, gafas, nariz y boca
    xo = w - 7
    _ojo(sup, xo, y_ojos, cfg, mirando=1)
    if cfg["gafas"]:
        tipo, marco, brillo = cfg["gafas"]
        for yy in range(y_ojos - 2, y_ojos + 3):
            sup.set_at((xo + 3, yy), marco)
            sup.set_at((xo - 2, yy), marco)
        for xx in range(xo - 2, xo + 4):
            sup.set_at((xx, y_ojos - 2), marco)
            sup.set_at((xx, y_ojos + 2), marco)
        for xx in range(corte + 2, xo - 2):
            sup.set_at((xx, y_ojos - 1), marco)                    # patilla hacia la oreja
    borde = max(x for x in range(w) if sup.get_at((x, y_ojos + 2)).a)
    sup.set_at((borde, y_ojos + 2), c["piel"])
    sup.set_at((borde + 1, y_ojos + 2), c["contorno"]) if borde + 1 < w else None
    sup.set_at((w - 5, y_ojos + 5), (176, 96, 96))
    return sup


# ----------------- Cuerpo -----------------
def cuerpo_recoloreado(cuadro, cfg, direccion):
    sup = cuadro.copy()
    colores = cfg["colores"]
    for y in range(sup.get_height()):
        for x in range(sup.get_width()):
            p = sup.get_at((x, y))
            if p.a:
                rol = ROLES_CUERPO.get((p.r, p.g, p.b))
                if rol and rol in colores:
                    sup.set_at((x, y), colores[rol])
    return sup


def extras_cuerpo(sup, cfg, direccion, bob):
    c = cfg["colores"]
    y0 = 25 + bob
    if "cadena" in cfg["extras"] and direccion == "abajo":
        plata = (196, 200, 210)
        for k in range(4):
            sup.set_at((12 + k, y0 + k), plata)
            sup.set_at((19 - k, y0 + k), plata)
        sup.set_at((15, y0 + 4), plata)
        sup.set_at((16, y0 + 4), plata)
    if "cordones" in cfg["extras"] and direccion == "abajo":
        for k in range(1, 4):
            sup.set_at((13, y0 + k), (240, 240, 240))
            sup.set_at((18, y0 + k), (240, 240, 240))
        sup.set_at((13, y0 + 4), (170, 172, 180))
        sup.set_at((18, y0 + 4), (170, 172, 180))
    if "capucha" in cfg["extras"]:
        for x in range(9, 23):
            p = sup.get_at((x, y0))
            if p.a and (p.r, p.g, p.b) != c["contorno"]:
                sup.set_at((x, y0), c["chaqueta_sombra"])
        if direccion == "arriba":
            for x in range(11, 21):
                for y in range(y0 + 1, y0 + 4):
                    sup.set_at((x, y), c["chaqueta_sombra"] if y == y0 + 3 or x in (11, 20) else c["chaqueta"])


def generar(nombre):
    cfg = PERSONAJES[nombre]
    plantilla = pygame.image.load(os.path.join(CARPETA, "cuerpo_base.png"))
    frente, ojos = cabeza_de_frente(nombre, cfg)
    y_ojos = preparar_cara(frente, ojos, cfg)
    cabezas = {
        "abajo": frente,
        "arriba": cabeza_de_espaldas(frente, y_ojos, cfg),
        "derecha": cabeza_de_perfil(frente, ojos, y_ojos, cfg),
    }
    cabezas["izquierda"] = pygame.transform.flip(cabezas["derecha"], True, False)

    hoja = pygame.Surface((W * 3, H * 4), pygame.SRCALPHA)
    for fila, d in enumerate(FILAS):
        for col in range(3):
            cuadro = plantilla.subsurface((col * W, fila * H, W, H))
            bob = 1 if col else 0
            sup = cuerpo_recoloreado(cuadro, cfg, d)
            sup.fill((0, 0, 0, 0), (0, 0, W, ALTO_CABEZA + bob))          # se quita la cabeza vieja
            extras_cuerpo(sup, cfg, d, bob)
            cab = cabezas[d]
            sup.blit(cab, ((W - cab.get_width()) // 2, bob))
            hoja.blit(sup, (col * W, fila * H))
    ruta = os.path.join(CARPETA, nombre, "caminar.png")
    pygame.image.save(hoja, ruta)
    print(f"Guardado {ruta}")


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    for n in sys.argv[1:] or list(PERSONAJES):
        generar(n)


if __name__ == "__main__":
    main()
