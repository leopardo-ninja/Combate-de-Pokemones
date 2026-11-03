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

CARPETA = sys.argv[1] if len(sys.argv) > 1 else "."
SALIDA = "assets/efectos"


def buscar(sufijo):
    r = glob.glob(os.path.join(CARPETA, f"*{sufijo}.png"))
    if not r:
        sys.exit(f"No encuentro *{sufijo}.png en {CARPETA}")
    return r[0]


def transparente(img, color):
    a = np.array(img.convert("RGBA"))
    a[(a[:, :, :3] == np.array(color)).all(axis=2), 3] = 0
    return Image.fromarray(a)


os.makedirs(f"{SALIDA}/ataque", exist_ok=True)
os.makedirs(f"{SALIDA}/stats", exist_ok=True)

# ---- Attack Effects: fondo verde (34,177,76) ----
im = Image.open(buscar("Attack_Effects")).convert("RGB")
a = np.array(im)
fg = ~(a == np.array([34, 177, 76])).all(axis=2)
fg[560:, 670:] = False                      # cuadro de texto de créditos
lab, _ = ndimage.label(ndimage.binary_dilation(fg, structure=np.ones((3, 3)), iterations=2))
cajas = []
for i, sl in enumerate(ndimage.find_objects(lab)):
    if (fg[sl] & (lab[sl] == i + 1)).sum() >= 12:
        cajas.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
cajas.sort(key=lambda r: (r[0] // 40, r[1]))   # columnas de izquierda a derecha
for k, (x0, y0, x1, y1) in enumerate(cajas):
    transparente(im.crop((x0, y0, x1, y1)), (34, 177, 76)).save(f"{SALIDA}/ataque/a{k:03d}.png")
print("ataque:", len(cajas), "sprites")

# ---- Stat Effects: 8 baldosas sobre fondo azul (0,0,128) ----
st = Image.open(buscar("Stat_Effects")).convert("RGB")
s = np.array(st)
lab, _ = ndimage.label(~(s == np.array([0, 0, 128])).all(axis=2))
tiles = []
for sl in ndimage.find_objects(lab):
    if sl[0].stop - sl[0].start >= 250 and sl[1].stop - sl[1].start >= 250:
        tiles.append((sl[0].start, sl[1].start, sl[1].stop, sl[0].stop))
tiles.sort(key=lambda t: (t[0] // 100, t[1]))
nombres = ["ataque", "defensa", "precision", "evasion", "velocidad", "atk_esp", "def_esp", "mezcla"]
for nom, (y0, x0, x1, y1) in zip(nombres, tiles):
    st.crop((x0, y0, x1, y1)).save(f"{SALIDA}/stats/{nom}.png")
print("stats:", len(tiles), "baldosas")
