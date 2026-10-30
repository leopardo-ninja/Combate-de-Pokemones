# ----------------- EXPORTAR A PNG -----------------
# Guarda el dibujo actual de cada personaje como PNG en assets/entrenadores/<nombre>/,
# listo para abrirlo y retocarlo en Piskel / Aseprite / LibreSprite.
#
# Uso (desde la carpeta del proyecto):
#   .venv/bin/python herramientas/exportar_png.py            (los tres)
#   .venv/bin/python herramientas/exportar_png.py tortuga    (uno)
#
# También crea assets/entrenadores/plantilla_caminar.png con las guías de la hoja
# (3 columnas x 4 filas de 32x48). Si un PNG ya existe NO se sobrescribe, para no
# perder lo que hayan dibujado (bórrenlo a mano si quieren volver a exportarlo).

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

import datos_personajes as dp
import entrenadores

W, H = dp.ANCHO_SPRITE, dp.ALTO_SPRITE


def guardar_si_no_existe(sup, ruta):
    if os.path.exists(ruta):
        print(f"  ya existe, no se toca: {ruta}")
        return
    pygame.image.save(sup, ruta)
    print(f"  guardado: {ruta}")


def exportar(nombre):
    carpeta = os.path.join(entrenadores.CARPETA, nombre)
    os.makedirs(carpeta, exist_ok=True)
    datos = dp.cargar(nombre)
    print(nombre)
    if "BUSTO" in datos:
        guardar_si_no_existe(dp.filas_a_superficie(datos["BUSTO"], datos["PALETA_BUSTO"]),
                             os.path.join(carpeta, "busto.png"))
    if "SPRITES" in datos:
        cuadros = {d: [dp.filas_a_superficie(f, datos["PALETA_SPRITE"]) for f in datos["SPRITES"][d]]
                   for d in dp.DIRECCIONES}
        cuadros["izquierda"] = [pygame.transform.flip(s, True, False) for s in cuadros["derecha"]]
        hoja = pygame.Surface((W * 3, H * 4), pygame.SRCALPHA)
        for fila, d in enumerate(entrenadores.FILAS_HOJA):
            for col, s in enumerate(cuadros[d]):
                hoja.blit(s, (col * W, fila * H))
        guardar_si_no_existe(hoja, os.path.join(carpeta, "caminar.png"))


def plantilla():
    """Hoja vacía con marcos y la línea del suelo (pies) de cada cuadro."""
    hoja = pygame.Surface((W * 3, H * 4), pygame.SRCALPHA)
    for fila in range(4):
        for col in range(3):
            r = pygame.Rect(col * W, fila * H, W, H)
            pygame.draw.rect(hoja, (255, 0, 255, 90), r, 1)
            pygame.draw.line(hoja, (0, 200, 255, 120), (r.x + 2, r.bottom - 2), (r.right - 3, r.bottom - 2))
    os.makedirs(entrenadores.CARPETA, exist_ok=True)
    ruta = os.path.join(entrenadores.CARPETA, "plantilla_caminar.png")
    pygame.image.save(hoja, ruta)
    print(f"plantilla: {ruta}")


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    nombres = sys.argv[1:] or entrenadores.ORDEN_ENTRENADORES
    for n in nombres:
        exportar(n)
    plantilla()


if __name__ == "__main__":
    main()
