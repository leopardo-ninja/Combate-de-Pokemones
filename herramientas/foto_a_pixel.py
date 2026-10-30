# ----------------- FOTO -> PIXEL ART -----------------
# Convierte la foto de un integrante del equipo en el busto (112x112) de su personaje.
#
# Uso (desde la carpeta del proyecto):
#   .venv/bin/python herramientas/foto_a_pixel.py tortuga herramientas/fotos/tortuga.jpg --x 8 --y 320 --lado 712
#
#   --x --y --lado   recorte cuadrado de la foto (en píxeles de la foto) que se convierte
#   --colores        cuántos colores tendrá la paleta (por defecto 28)
#
# Pasos: recortar -> reducir a 112x112 -> más contraste y color -> paleta limitada
# (corte por la mediana) -> limpiar píxeles sueltos. El fondo se quita con la MASCARA
# (contorno de la persona) guardada en personajes/<nombre>.py.

import argparse
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

import datos_personajes as dp


# ----------------- Ajuste de color -----------------
def realzar(c, saturacion=1.2, contraste=1.12):
    color = pygame.Color(*c)
    h, s, v, a = color.hsva
    s = min(100, s * saturacion)
    v = max(0, min(100, 50 + (v - 50) * contraste))
    color.hsva = (h, s, v, a)
    return (color.r, color.g, color.b)


# ----------------- Paleta por corte de la mediana -----------------
def paleta_mediana(colores, cantidad):
    """Reparte los colores en 'cantidad' cajas partiendo siempre la caja más ancha por la mediana."""
    cajas = [list(colores)]
    while len(cajas) < cantidad:
        def rango(caja):
            return max(max(c[i] for c in caja) - min(c[i] for c in caja) for i in range(3))
        caja = max((c for c in cajas if len(c) > 1), key=rango, default=None)
        if caja is None:
            break
        canal = max(range(3), key=lambda i: max(c[i] for c in caja) - min(c[i] for c in caja))
        caja.sort(key=lambda c: c[canal])
        mitad = len(caja) // 2
        cajas.remove(caja)
        cajas += [caja[:mitad], caja[mitad:]]
    return [tuple(sum(c[i] for c in caja) // len(caja) for i in range(3)) for caja in cajas]


def mas_cercano(c, paleta):
    return min(range(len(paleta)), key=lambda i: (c[0] - paleta[i][0]) ** 2 * 3 + (c[1] - paleta[i][1]) ** 2 * 4
               + (c[2] - paleta[i][2]) ** 2 * 2)


# ----------------- Limpieza -----------------
def limpiar(indices, ancho, alto, pasadas=2):
    """Quita píxeles sueltos: si un píxel es distinto de sus vecinos y 3 de ellos coinciden, toma ese color."""
    for _ in range(pasadas):
        nuevos = [fila[:] for fila in indices]
        for y in range(alto):
            for x in range(ancho):
                vecinos = [indices[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                           if 0 <= x + dx < ancho and 0 <= y + dy < alto]
                if indices[y][x] not in vecinos:
                    mas_comun = max(set(vecinos), key=vecinos.count)
                    if vecinos.count(mas_comun) >= 3:
                        nuevos[y][x] = mas_comun
        indices = nuevos
    return indices


def mayoria(indices, ancho, alto, pasadas=2):
    """Filtro de mayoría 3x3: cada píxel toma el color más repetido a su alrededor (zonas planas)."""
    for _ in range(pasadas):
        nuevos = [fila[:] for fila in indices]
        for y in range(1, alto - 1):
            for x in range(1, ancho - 1):
                zona = [indices[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
                mas_comun = max(set(zona), key=zona.count)
                if zona.count(mas_comun) >= 5:
                    nuevos[y][x] = mas_comun
        indices = nuevos
    return indices


def luminancia(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def contornos(indices, paleta, ancho, alto, umbral=38):
    """Marca con un color oscuro el lado oscuro de los bordes fuertes (estilo pixel art)."""
    oscuro = min(range(len(paleta)), key=lambda i: luminancia(paleta[i]))
    marcar = set()
    for y in range(alto):
        for x in range(ancho):
            a = luminancia(paleta[indices[y][x]])
            for dx, dy in ((1, 0), (0, 1)):
                if x + dx < ancho and y + dy < alto:
                    b = luminancia(paleta[indices[y + dy][x + dx]])
                    if abs(a - b) > umbral:
                        marcar.add((x, y) if a < b else (x + dx, y + dy))
    for x, y in marcar:
        # se oscurece al tono más oscuro cercano (no siempre negro: queda más suave)
        c = paleta[indices[y][x]]
        objetivo = (c[0] * 0.55, c[1] * 0.5, c[2] * 0.5)
        indices[y][x] = min(range(len(paleta)), key=lambda i: sum((paleta[i][k] - objetivo[k]) ** 2 for k in range(3)))
        if luminancia(paleta[indices[y][x]]) > luminancia(c) - 15:
            indices[y][x] = oscuro
    return indices


def mascara_de(poligono, tam):
    """Conjunto de píxeles dentro del polígono (la persona); None = sin máscara."""
    if not poligono:
        return None
    sup = pygame.Surface((tam, tam))
    sup.fill((0, 0, 0))
    pygame.draw.polygon(sup, (255, 255, 255), poligono)
    return {(i, j) for j in range(tam) for i in range(tam) if sup.get_at((i, j))[0]}


def convertir(foto, x, y, lado, colores=16, tam=dp.TAM_BUSTO, umbral_contorno=38, mascara=None):
    imagen = pygame.image.load(foto)
    recorte = pygame.Surface((lado, lado))
    recorte.fill((0, 0, 0))
    recorte.blit(imagen, (-x, -y))
    pequeña = pygame.transform.smoothscale(recorte, (tam, tam))
    pixeles = [[realzar(tuple(pequeña.get_at((i, j)))[:3]) for i in range(tam)] for j in range(tam)]
    dentro = mascara_de(mascara, tam)
    persona = [pixeles[j][i] for j in range(tam) for i in range(tam) if dentro is None or (i, j) in dentro]
    paleta = paleta_mediana(persona, colores)
    indices = [[mas_cercano(c, paleta) for c in fila] for fila in pixeles]
    indices = mayoria(indices, tam, tam)
    indices = limpiar(indices, tam, tam)
    if umbral_contorno:
        indices = contornos(indices, paleta, tam, tam, umbral_contorno)
    # Paleta ordenada de oscuro a claro (más cómoda en el editor)
    orden = sorted(range(len(paleta)), key=lambda i: sum(paleta[i]))
    letra = {i: dp.LETRAS[k] for k, i in enumerate(orden)}
    paleta_letras = {letra[i]: paleta[i] for i in orden}
    filas = ["".join(letra[i] for i in fila) for fila in indices]
    if dentro is not None:
        # fuera de la máscara: transparente; borde de la silueta: contorno oscuro
        oscura = dp.LETRAS[0]
        filas = [[c if (i, j) in dentro else "." for i, c in enumerate(fila)] for j, fila in enumerate(filas)]
        borde = [(i, j) for j in range(tam) for i in range(tam) if filas[j][i] != "." and any(
            not (0 <= i + dx < tam and 0 <= j + dy < tam) or filas[j + dy][i + dx] == "."
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for i, j in borde:
            if j < tam - 1:                       # el borde de abajo (cortado por el marco) no lleva contorno
                filas[j][i] = oscura
        filas = ["".join(f) for f in filas]
    return paleta_letras, filas


def main():
    ap = argparse.ArgumentParser(description="Convierte una foto en el busto de pixel art de un personaje.")
    ap.add_argument("nombre")
    ap.add_argument("foto")
    ap.add_argument("--x", type=int, default=0)
    ap.add_argument("--y", type=int, default=0)
    ap.add_argument("--lado", type=int, required=True)
    ap.add_argument("--colores", type=int, default=16)
    ap.add_argument("--contorno", type=int, default=38, help="umbral de los contornos (0 = sin contornos)")
    args = ap.parse_args()

    pygame.init()
    pygame.display.set_mode((1, 1))
    datos = dp.cargar(args.nombre)          # conserva sprites y máscara si ya existen
    mascara = datos.get("MASCARA")
    paleta, filas = convertir(args.foto, args.x, args.y, args.lado, args.colores,
                              umbral_contorno=args.contorno, mascara=mascara)
    datos["PALETA_BUSTO"] = paleta
    datos["BUSTO"] = filas
    datos["FOTO"] = {"archivo": os.path.basename(args.foto), "x": args.x, "y": args.y, "lado": args.lado}
    dp.guardar(args.nombre, datos)
    print(f"Busto de {args.nombre} guardado en {dp.ruta(args.nombre)} ({len(paleta)} colores).")


if __name__ == "__main__":
    main()
