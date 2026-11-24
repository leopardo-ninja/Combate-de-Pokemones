# Recorta los sprites de las hojas de efectos de FireRed/LeafGreen y los guarda sueltos.
# Uso: python recortar_efectos.py [carpeta_con_los_PNG]   (por defecto, la carpeta actual)
# Genera: assets/efectos/ataque/aNNN.png  y  assets/efectos/stats/<stat>.png
# Requiere: pip install pillow numpy scipy
import glob
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

# Carpeta donde están las hojas PNG: el primer argumento del programa o la carpeta actual
CARPETA = sys.argv[1] if len(sys.argv) > 1 else "."
SALIDA = "assets/efectos"


def buscar(sufijo):
    # Busca en CARPETA el PNG cuyo nombre termina en el sufijo dado; si no existe, el programa termina con un aviso
    resultados = glob.glob(os.path.join(CARPETA, f"*{sufijo}.png"))
    if not resultados:
        sys.exit(f"No encuentro *{sufijo}.png en {CARPETA}")
    return resultados[0]


def transparente(imagen, color_fondo):
    # Devuelve la imagen con los píxeles del color de fondo convertidos en transparentes
    pixeles = np.array(imagen.convert("RGBA"))
    pixeles[(pixeles[:, :, :3] == np.array(color_fondo)).all(axis=2), 3] = 0
    return Image.fromarray(pixeles)


# Se crean las carpetas de salida si no existen
os.makedirs(f"{SALIDA}/ataque", exist_ok=True)
os.makedirs(f"{SALIDA}/stats", exist_ok=True)

# ---- Attack Effects: fondo verde (34,177,76) ----
hoja_ataques = Image.open(buscar("Attack_Effects")).convert("RGB")
pixeles_ataques = np.array(hoja_ataques)

# mascara_frente: True en los píxeles que NO son del verde de fondo (es decir, los que pertenecen a un sprite)
mascara_frente = ~(pixeles_ataques == np.array([34, 177, 76])).all(axis=2)
mascara_frente[560:, 670:] = False                      # cuadro de texto de créditos

# Se agrupan los píxeles vecinos (dilatando 2 px para unir las partes de un mismo sprite) y se numera cada grupo
etiquetas, _ = ndimage.label(ndimage.binary_dilation(mascara_frente, structure=np.ones((3, 3)), iterations=2))

# cajas: rectángulo (x0, y0, x1, y1) de cada sprite; se descartan los grupos con menos de 12 píxeles (ruido)
cajas = []
for numero, rebanada in enumerate(ndimage.find_objects(etiquetas)):
    if (mascara_frente[rebanada] & (etiquetas[rebanada] == numero + 1)).sum() >= 12:
        cajas.append((rebanada[1].start, rebanada[0].start, rebanada[1].stop, rebanada[0].stop))

# Se ordenan por columnas de izquierda a derecha (agrupando cada 40 px) y de arriba abajo dentro de cada columna
cajas.sort(key=lambda caja: (caja[0] // 40, caja[1]))

# Cada sprite se recorta de la hoja, se le quita el fondo verde y se guarda como aNNN.png
for k, (x0, y0, x1, y1) in enumerate(cajas):
    transparente(hoja_ataques.crop((x0, y0, x1, y1)), (34, 177, 76)).save(f"{SALIDA}/ataque/a{k:03d}.png")
print("ataque:", len(cajas), "sprites")

# ---- Stat Effects: 8 baldosas sobre fondo azul (0,0,128) ----
hoja_stats = Image.open(buscar("Stat_Effects")).convert("RGB")
pixeles_stats = np.array(hoja_stats)

# Se numera cada región que no sea el azul de fondo (cada baldosa es una región grande)
etiquetas, _ = ndimage.label(~(pixeles_stats == np.array([0, 0, 128])).all(axis=2))

# baldosas: (y0, x0, x1, y1) de cada región de al menos 250x250 px (las más pequeñas se ignoran)
baldosas = []
for rebanada in ndimage.find_objects(etiquetas):
    if rebanada[0].stop - rebanada[0].start >= 250 and rebanada[1].stop - rebanada[1].start >= 250:
        baldosas.append((rebanada[0].start, rebanada[1].start, rebanada[1].stop, rebanada[0].stop))

# Se ordenan por filas (cada 100 px) y de izquierda a derecha; ese orden coincide con la lista de nombres
baldosas.sort(key=lambda baldosa: (baldosa[0] // 100, baldosa[1]))
nombres = ["ataque", "defensa", "precision", "evasion", "velocidad", "atk_esp", "def_esp", "mezcla"]

# Cada baldosa se recorta de la hoja y se guarda con el nombre de su estadística
for nombre, (y0, x0, x1, y1) in zip(nombres, baldosas):
    hoja_stats.crop((x0, y0, x1, y1)).save(f"{SALIDA}/stats/{nombre}.png")
print("stats:", len(baldosas), "baldosas")
