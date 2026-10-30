# ----------------- DATOS DE LOS PERSONAJES -----------------
# Cada personaje se guarda en personajes/<nombre>.py como código Python:
#
#   PALETA_BUSTO  = {"a": (r, g, b), ...}       letra -> color ("." es transparente)
#   BUSTO         = ["....", ...]               112 filas de 112 letras
#   PALETA_SPRITE = {...}
#   SPRITES       = {"abajo": [f0, f1, f2], "arriba": [...], "derecha": [...]}
#                   cada frame son 48 filas de 32 letras (izquierda = derecha en espejo)
#   FOTO          = {"archivo": "tortuga.jpg", "x": 8, "y": 320, "lado": 712}
#   MASCARA       = [(x, y), ...]   contorno de la persona en el busto (lo de fuera es fondo)
#
# Esos archivos los escriben las herramientas (herramientas/foto_a_pixel.py),
# pero se pueden leer y retocar a mano. Si existen PNG en assets/entrenadores/, se usan esos.

import importlib
import os
import string

import pygame

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personajes")
TAM_BUSTO = 112
ANCHO_SPRITE, ALTO_SPRITE = 32, 48
DIRECCIONES = ("abajo", "arriba", "derecha")

# Letras disponibles para los colores de una paleta
LETRAS = string.ascii_letters + string.digits + "!#$%&*+-/:;<=>?@^_~"


def ruta(nombre):
    return os.path.join(CARPETA, f"{nombre}.py")


def cargar(nombre):
    """Devuelve un dict con las claves del archivo del personaje (o {} si no existe)."""
    if not os.path.exists(ruta(nombre)):
        return {}
    modulo = importlib.import_module(f"personajes.{nombre}")
    modulo = importlib.reload(modulo)
    return {k: getattr(modulo, k) for k in ("PALETA_BUSTO", "BUSTO", "PALETA_SPRITE", "SPRITES", "FOTO", "MASCARA")
            if hasattr(modulo, k)}


def guardar(nombre, datos):
    """Escribe personajes/<nombre>.py con el formato de arriba."""
    os.makedirs(CARPETA, exist_ok=True)
    lineas = [f"# Datos de pixel art de '{nombre}'. Generado por las herramientas del proyecto;",
              "# se puede retocar a mano (cada letra es un color de la paleta, '.' es transparente).", ""]
    if "FOTO" in datos:
        lineas.append(f"FOTO = {datos['FOTO']!r}")
        lineas.append("")
    if datos.get("MASCARA"):
        lineas.append(f"MASCARA = {[tuple(p) for p in datos['MASCARA']]!r}")
        lineas.append("")
    for clave in ("PALETA_BUSTO", "PALETA_SPRITE"):
        if clave in datos:
            lineas.append(f"{clave} = {{")
            for letra, color in datos[clave].items():
                lineas.append(f"    {letra!r}: {tuple(color)!r},")
            lineas.append("}")
            lineas.append("")
    if "BUSTO" in datos:
        lineas.append("BUSTO = [")
        lineas += [f"    {fila!r}," for fila in datos["BUSTO"]]
        lineas.append("]")
        lineas.append("")
    if "SPRITES" in datos:
        lineas.append("SPRITES = {")
        for direccion in DIRECCIONES:
            lineas.append(f"    {direccion!r}: [")
            for frame in datos["SPRITES"][direccion]:
                lineas.append("        [")
                lineas += [f"            {fila!r}," for fila in frame]
                lineas.append("        ],")
            lineas.append("    ],")
        lineas.append("}")
        lineas.append("")
    with open(ruta(nombre), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))


# ----------------- Conversión entre letras y superficies -----------------
def filas_a_superficie(filas, paleta):
    alto, ancho = len(filas), len(filas[0])
    sup = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for y, fila in enumerate(filas):
        for x, letra in enumerate(fila):
            if letra != "." and letra in paleta:
                sup.set_at((x, y), paleta[letra])
    return sup


def superficie_a_filas(sup, paleta):
    """Convierte una superficie en filas de letras; agrega a la paleta los colores nuevos."""
    por_color = {tuple(c): letra for letra, c in paleta.items()}
    filas = []
    for y in range(sup.get_height()):
        fila = []
        for x in range(sup.get_width()):
            c = sup.get_at((x, y))
            if c.a < 128:
                fila.append(".")
                continue
            rgb = (c.r, c.g, c.b)
            if rgb not in por_color:
                libres = [l for l in LETRAS if l not in paleta]
                if not libres:   # paleta llena: usar el color más parecido
                    rgb = min(por_color, key=lambda k: sum((a - b) ** 2 for a, b in zip(k, rgb)))
                else:
                    paleta[libres[0]] = rgb
                    por_color[rgb] = libres[0]
            fila.append(por_color[rgb])
        filas.append("".join(fila))
    return filas
