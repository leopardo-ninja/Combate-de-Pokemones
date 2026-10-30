# ----------------- IMPORTAR ARTE GENERADO CON IA -----------------
# Las imágenes de pixel art generadas por IA vienen grandes (ej. 1024x1024) y cada
# "píxel" del dibujo ocupa varios píxeles reales, con bordes un poco borrosos.
# Este script las convierte en pixel art de verdad para el juego:
#   1. Divide la imagen en una cuadrícula (ej. 112x112) y en cada celda toma el color
#      que más se repite en su centro (así no se mezclan los bordes).
#   2. Reduce la paleta (corte por la mediana) para que los colores queden limpios.
#   3. Quita el fondo liso: borra los píxeles conectados a los bordes cuyo color se
#      parece al de las esquinas.
#
# Uso (desde la carpeta del proyecto):
#   .venv/bin/python herramientas/importar_ia.py retrato.png assets/entrenadores/tortuga/busto.png --tam 112
#
#   --ensanchar 1.12   ensancha la imagen un 12% (personaje menos flaco)
#   --acercar 0.84     se queda con el 84% de arriba-centro de la imagen (encuadre más cerca)

import argparse
import os
import sys
from collections import Counter

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from foto_a_pixel import paleta_mediana, mas_cercano


def celdas_a_pixeles(imagen, ancho, alto):
    """Color dominante del centro de cada celda de la cuadrícula."""
    w, h = imagen.get_size()
    cw, ch = w / ancho, h / alto
    salida = []
    for j in range(alto):
        fila = []
        for i in range(ancho):
            x0, x1 = int(i * cw + cw * 0.25), int(i * cw + cw * 0.75) + 1
            y0, y1 = int(j * ch + ch * 0.25), int(j * ch + ch * 0.75) + 1
            votos = Counter()
            for y in range(y0, min(y1, h)):
                for x in range(x0, min(x1, w)):
                    c = imagen.get_at((x, y))
                    votos[(c.r // 4 * 4, c.g // 4 * 4, c.b // 4 * 4, 255 if c.a > 127 else 0)] += 1
            fila.append(votos.most_common(1)[0][0])
        salida.append(fila)
    return salida


def quitar_fondo(pix, tolerancia=40):
    """Borra el fondo liso conectado a los bordes (color parecido al de las esquinas)."""
    alto, ancho = len(pix), len(pix[0])
    esquinas = [pix[0][0], pix[0][-1], pix[-1][0], pix[-1][-1]]
    fondo = Counter(esquinas).most_common(1)[0][0]

    def parecido(c):
        return c[3] == 0 or sum(abs(c[k] - fondo[k]) for k in range(3)) <= tolerancia

    vistos = set()
    pila = [(x, y) for x in range(ancho) for y in (0, alto - 1)] + [(x, y) for y in range(alto) for x in (0, ancho - 1)]
    while pila:
        x, y = pila.pop()
        if (x, y) in vistos or not (0 <= x < ancho and 0 <= y < alto) or not parecido(pix[y][x]):
            continue
        vistos.add((x, y))
        pila += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for x, y in vistos:
        pix[y][x] = (0, 0, 0, 0)
    return pix


def ajustar_encuadre(imagen, ensanchar=1.0, acercar=1.0, margen_arriba=0.01):
    """Ensancha en horizontal y recorta un cuadrado centrado (pegado arriba) para acercar."""
    w, h = imagen.get_size()
    if ensanchar != 1.0:
        imagen = pygame.transform.smoothscale(imagen, (int(w * ensanchar), h))
    if acercar != 1.0 or ensanchar != 1.0:
        lado = int(min(w, h) * acercar)
        recorte = pygame.Surface((lado, lado), pygame.SRCALPHA)
        recorte.blit(imagen, (-(imagen.get_width() - lado) // 2, -int(h * margen_arriba)))
        imagen = recorte
    return imagen


def convertir(entrada, ancho, alto, colores=32, tolerancia=40, con_fondo=False, ensanchar=1.0, acercar=1.0):
    imagen = ajustar_encuadre(pygame.image.load(entrada), ensanchar, acercar)
    pix = celdas_a_pixeles(imagen, ancho, alto)
    if not con_fondo:
        pix = quitar_fondo(pix, tolerancia)
    opacos = [c[:3] for fila in pix for c in fila if c[3]]
    paleta = paleta_mediana(opacos, colores)
    sup = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for j, fila in enumerate(pix):
        for i, c in enumerate(fila):
            if c[3]:
                sup.set_at((i, j), paleta[mas_cercano(c[:3], paleta)])
    return sup


def main():
    ap = argparse.ArgumentParser(description="Convierte pixel art generado con IA en pixel art limpio para el juego.")
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--tam", type=int, default=112, help="lado de la cuadrícula (ancho = alto)")
    ap.add_argument("--ancho", type=int)
    ap.add_argument("--alto", type=int)
    ap.add_argument("--colores", type=int, default=32)
    ap.add_argument("--tolerancia", type=int, default=40, help="cuánto se puede alejar del color de fondo")
    ap.add_argument("--con-fondo", action="store_true", help="no quitar el fondo")
    ap.add_argument("--ensanchar", type=float, default=1.0, help="ej. 1.12 = 12%% más ancho")
    ap.add_argument("--acercar", type=float, default=1.0, help="ej. 0.84 = encuadre más cerca")
    args = ap.parse_args()
    pygame.init()
    pygame.display.set_mode((1, 1))
    sup = convertir(args.entrada, args.ancho or args.tam, args.alto or args.tam,
                    args.colores, args.tolerancia, args.con_fondo, args.ensanchar, args.acercar)
    os.makedirs(os.path.dirname(os.path.abspath(args.salida)), exist_ok=True)
    pygame.image.save(sup, args.salida)
    print(f"Guardado {args.salida} ({sup.get_width()}x{sup.get_height()})")


if __name__ == "__main__":
    main()
