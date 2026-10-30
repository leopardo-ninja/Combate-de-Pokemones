# ----------------- IMPORTAR UNA HOJA DE CAMINAR HECHA CON IA -----------------
# Convierte una hoja de sprites generada por IA (Gemini, etc.) en caminar.png para el juego.
# Esas hojas suelen venir así: JPG con un fondo de cuadritos dibujado (no es transparencia
# de verdad), cuadros que no están en una cuadrícula exacta y "píxeles" de varios píxeles.
#
# Pasos:
#   1. Quita el fondo de cuadritos: relleno desde los bordes que solo avanza por grises.
#   2. Encuentra cada muñequito (zona conectada) y los agrupa en filas.
#   3. Pasa cada cuadro a la cuadrícula del juego (por defecto 64x96, el tamaño con que se dibuja
#      en el mapa, así no se pierde detalle), alineado por los pies, con una paleta común.
#   4. Arma la hoja del juego: filas abajo, izquierda, derecha, arriba.
#
# Uso (desde la carpeta del proyecto):
#   .venv/bin/python herramientas/importar_hoja_ia.py hoja.jpg assets/entrenadores/tortuga/caminar.png \
#       --filas abajo izquierda izquierda arriba
#
#   --filas   qué dirección mira cada fila de la imagen, de arriba a abajo. Si falta "derecha",
#             se hace reflejando "izquierda" (y al revés).
#   --cuadros elegir cuadro por cuadro (fila.cuadro, contando desde 1), cuando la IA mezcla
#             direcciones. Ej.: --cuadros abajo=1.1,1.2,1.3 izquierda=2.1,2.2,3.2 arriba=4.1,4.2,4.3
#   --completar-con  otra hoja (formato del juego) de donde sacar las direcciones que falten,
#             por ejemplo si la IA no dibujó la espalda.
#   --pantalon-negro  pasa a negro el pantalón azul (la IA a veces pone jeans aunque se pida negro).

import argparse
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from importar_ia import celdas_a_pixeles
from foto_a_pixel import paleta_mediana, mas_cercano

W, H = 64, 96          # tamaño de cada cuadro (el juego acepta cualquiera; se dibuja con 96 de alto)
ORDEN_JUEGO = ["abajo", "izquierda", "derecha", "arriba"]


def rango_del_fondo(imagen, gris=18):
    """Mira los bordes de la imagen: el fondo son grises (claros u oscuros) sin color."""
    w, h = imagen.get_size()
    valores = []
    for x in range(0, w, 3):
        for y in (0, 1, h - 2, h - 1):
            c = imagen.get_at((x, y))
            if max(c[:3]) - min(c[:3]) <= gris:
                valores.append(sum(c[:3]) / 3)
    for y in range(0, h, 3):
        for x in (0, 1, w - 2, w - 1):
            c = imagen.get_at((x, y))
            if max(c[:3]) - min(c[:3]) <= gris:
                valores.append(sum(c[:3]) / 3)
    # solo cuentan los grises que dominan el borde (los cuadritos); si un dibujo toca el
    # borde, sus colores aparecen poco y se ignoran
    cajones = {}
    for v in valores:
        cajones[int(v) // 8] = cajones.get(int(v) // 8, 0) + 1
    dominantes = [k for k, n in cajones.items() if n >= len(valores) * 0.08]
    return min(dominantes) * 8 - 14, max(dominantes) * 8 + 8 + 14


def es_fondo(c, minimo, maximo, gris=18):
    return max(c[:3]) - min(c[:3]) <= gris and minimo <= sum(c[:3]) / 3 <= maximo


def quitar_fondo(imagen):
    """Pone transparente el fondo de cuadritos conectado a los bordes. Devuelve una copia RGBA."""
    sup = imagen.convert_alpha()
    minimo, maximo = rango_del_fondo(sup)
    w, h = sup.get_size()
    visto = bytearray(w * h)
    pila = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + \
           [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    while pila:
        x, y = pila.pop()
        if not (0 <= x < w and 0 <= y < h) or visto[y * w + x]:
            continue
        if not es_fondo(tuple(sup.get_at((x, y))), minimo, maximo):
            continue
        visto[y * w + x] = 1
        sup.set_at((x, y), (0, 0, 0, 0))
        pila += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return sup


def buscar_figuras(sup, area_minima=800):
    """Rectángulos de las zonas no transparentes (cada muñequito)."""
    w, h = sup.get_size()
    visto = bytearray(w * h)
    figuras = []
    for y0 in range(0, h, 2):
        for x0 in range(0, w, 2):
            if visto[y0 * w + x0] or sup.get_at((x0, y0)).a == 0:
                continue
            pila, xs, ys, n = [(x0, y0)], [], [], 0
            while pila:
                x, y = pila.pop()
                if not (0 <= x < w and 0 <= y < h) or visto[y * w + x] or sup.get_at((x, y)).a == 0:
                    continue
                visto[y * w + x] = 1
                xs.append(x)
                ys.append(y)
                n += 1
                pila += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if n >= area_minima:
                figuras.append(pygame.Rect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
    return figuras


def agrupar_en_filas(figuras):
    figuras = sorted(figuras, key=lambda r: r.centery)
    filas = []
    for r in figuras:
        if filas and abs(filas[-1][0].centery - r.centery) < r.height * 0.5:
            filas[-1].append(r)
        else:
            filas.append([r])
    return [sorted(f, key=lambda r: r.x) for f in filas]


def pantalon_a_negro(sup, desde=0.55):
    """Oscurece los azules de la parte de abajo del cuadro (pantalón), conservando las sombras."""
    w, h = sup.get_size()
    for y in range(int(h * desde), h):
        for x in range(w):
            c = sup.get_at((x, y))
            if c.a and c.b > c.r + 15 and c.b >= c.g:
                v = int((c.r + c.g + c.b) / 3 * 0.5)
                sup.set_at((x, y), (v, v, v + 4))


def importar(entrada, direcciones, colores=48, elegidos=None, W=W, H=H, completar=None, pantalon_negro=False):
    imagen = pygame.image.load(entrada)
    sup = quitar_fondo(imagen)
    filas = agrupar_en_filas(buscar_figuras(sup))
    alto_max = max(r.height for f in filas for r in f)
    celda = alto_max / (H - 2)                     # tamaño de un "píxel" del dibujo
    if elegidos:                                   # {direccion: [(fila, cuadro), ...]} contando desde 1
        seleccion = {d: [filas[f - 1][c - 1] for f, c in lista] for d, lista in elegidos.items()}
    else:
        seleccion = {}
        for d, fila in zip(direcciones, filas):
            if d is not None and d not in seleccion:
                seleccion[d] = fila[:3]
    cuadros = {}
    for d, rects in seleccion.items():
        lista = []
        for r in rects:
            ancho_px, alto_px = int(W * celda), int(H * celda)
            caja = pygame.Surface((ancho_px, alto_px), pygame.SRCALPHA)
            caja.blit(sup, (0, 0), pygame.Rect(r.centerx - ancho_px // 2, r.bottom - alto_px, ancho_px, alto_px))
            lista.append(celdas_a_pixeles(caja, W, H))
        cuadros[d] = lista
    # paleta común para todos los cuadros
    opacos = [c[:3] for fr in cuadros.values() for pix in fr for fila in pix for c in fila if c[3]]
    paleta = paleta_mediana(opacos, colores)

    def a_superficie(pix):
        # cada píxel al color más cercano de la paleta (None = transparente)
        idx = [[mas_cercano(c[:3], paleta) if c[3] else None for c in fila] for fila in pix]
        # limpieza: un píxel suelto rodeado por 3-4 vecinos iguales toma su color (quita ruido del JPG)
        for _ in range(2):
            nuevo = [fila[:] for fila in idx]
            for y in range(H):
                for x in range(W):
                    if idx[y][x] is None:
                        continue
                    vecinos = [idx[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                               if 0 <= x + dx < W and 0 <= y + dy < H]
                    vecinos = [v for v in vecinos if v is not None]
                    if vecinos and idx[y][x] not in vecinos:
                        comun = max(set(vecinos), key=vecinos.count)
                        if vecinos.count(comun) >= 3:
                            nuevo[y][x] = comun
            idx = nuevo
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        for y, fila in enumerate(idx):
            for x, i in enumerate(fila):
                if i is not None:
                    s.set_at((x, y), paleta[i])
        return s

    sups = {d: [a_superficie(p) for p in lista] for d, lista in cuadros.items()}
    if pantalon_negro:
        for lista in sups.values():
            for sup_cuadro in lista:
                pantalon_a_negro(sup_cuadro)
    if "derecha" not in sups and "izquierda" in sups:
        sups["derecha"] = [pygame.transform.flip(s, True, False) for s in sups["izquierda"]]
    if "izquierda" not in sups and "derecha" in sups:
        sups["izquierda"] = [pygame.transform.flip(s, True, False) for s in sups["derecha"]]
    if completar:
        otra = pygame.image.load(completar)
        ow, oh = otra.get_width() // 3, otra.get_height() // 4
        for f, d in enumerate(ORDEN_JUEGO):
            if d not in sups:
                sups[d] = [pygame.transform.scale(otra.subsurface((c * ow, f * oh, ow, oh)), (W, H)) for c in range(3)]
                print(f"  '{d}' tomado de {completar}")
    faltan = [d for d in ORDEN_JUEGO if d not in sups]
    if faltan:
        raise SystemExit(f"Faltan direcciones: {faltan}. Usa --cuadros o --completar-con.")
    hoja = pygame.Surface((W * 3, H * 4), pygame.SRCALPHA)
    for f, d in enumerate(ORDEN_JUEGO):
        for c, s in enumerate(sups[d]):
            hoja.blit(s, (c * W, f * H))
    return hoja, filas


def main():
    ap = argparse.ArgumentParser(description="Importa una hoja de caminar hecha con IA.")
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--filas", nargs="+", default=["abajo", "izquierda", "derecha", "arriba"],
                    help="dirección de cada fila de la imagen (usar 'no' para ignorar una fila)")
    ap.add_argument("--cuadros", nargs="+", help="ej. abajo=1.1,1.2,1.3 izquierda=2.1,2.2,3.2")
    ap.add_argument("--completar-con", help="hoja de donde sacar las direcciones que falten")
    ap.add_argument("--pantalon-negro", action="store_true", help="pasa a negro el pantalón azul")
    ap.add_argument("--colores", type=int, default=48)
    ap.add_argument("--ancho", type=int, default=W, help="ancho de cada cuadro (por defecto 64)")
    ap.add_argument("--alto", type=int, default=H, help="alto de cada cuadro (por defecto 96)")
    args = ap.parse_args()
    pygame.init()
    pygame.display.set_mode((1, 1))
    direcciones = [None if d == "no" else d for d in args.filas]
    elegidos = None
    if args.cuadros:
        elegidos = {}
        for item in args.cuadros:
            d, lista = item.split("=")
            elegidos[d] = [tuple(int(n) for n in fc.split(".")) for fc in lista.split(",")]
    hoja, filas = importar(args.entrada, direcciones, args.colores, elegidos, args.ancho, args.alto,
                           args.completar_con, args.pantalon_negro)
    print("Figuras encontradas por fila:", [len(f) for f in filas])
    pygame.image.save(hoja, args.salida)
    print(f"Guardado {args.salida}")


if __name__ == "__main__":
    main()
