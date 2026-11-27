import os
import unicodedata
import pygame
from config import COLORES_TIPO
from pokemons import CATALOGO_POKEMONS

pygame.init()

CARPETA_EFECTOS = "assets/efectos"
os.makedirs(CARPETA_EFECTOS, exist_ok=True)


def normalizar_nombre(texto):
    # Convierte "Rayo Hielo" -> "rayo_hielo" (ajusta si en tu efectos.py usan espacios o tildes)
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto.strip().lower().replace(" ", "_")


def dibujar_efecto(tipo, color, tamano=(128, 128)):
    surf = pygame.Surface(tamano, pygame.SRCALPHA)
    cx, cy = tamano[0] // 2, tamano[1] // 2
    r, g, b = color
    claro = (min(255, r + 65), min(255, g + 65), min(255, b + 65))
    oscuro = (max(0, r - 50), max(0, g - 50), max(0, b - 50))

    # Halo exterior translúcido
    pygame.draw.circle(surf, (r, g, b, 70), (cx, cy), 54)
    pygame.draw.circle(surf, (r, g, b, 140), (cx, cy), 38)

    tipo_u = tipo.upper()
    if tipo_u in ("FUEGO", "DRAGÓN"):
        puntos = [(cx, 12), (cx + 28, cy), (cx + 14, 110), (cx - 14, 110), (cx - 28, cy)]
        pygame.draw.polygon(surf, color, puntos)
        pygame.draw.polygon(surf, claro, [(cx, 28), (cx + 14, cy + 6), (cx, 96), (cx - 14, cy + 6)])
    elif tipo_u in ("ELÉCTRICO", "PSÍQUICO"):
        rayo = [(cx + 10, 14), (cx - 22, cy + 6), (cx - 2, cy + 6), (cx - 12, 114), (cx + 24, cy - 6), (cx + 4, cy - 6)]
        pygame.draw.polygon(surf, color, rayo)
        pygame.draw.polygon(surf, claro, rayo, 3)
    elif tipo_u in ("AGUA", "HIELO", "VENENO"):
        for dx, dy, rad in [(-18, -12, 16), (20, -6, 14), (0, 18, 22), (-14, 22, 11), (18, 20, 12)]:
            pygame.draw.circle(surf, color, (cx + dx, cy + dy), rad)
            pygame.draw.circle(surf, claro, (cx + dx - 4, cy + dy - 4), max(3, rad // 3))
    elif tipo_u in ("TIERRA", "LUCHA"):
        roca = [(cx - 32, cy - 18), (cx, cy - 36), (cx + 34, cy - 14), (cx + 26, cy + 28), (cx - 24, cy + 30)]
        pygame.draw.polygon(surf, oscuro, roca)
        pygame.draw.polygon(surf, color, [(x * 0.85 + cx * 0.15, y * 0.85 + cy * 0.15) for x, y in roca])
    else:
        # Planta, Bicho, Normal, Fantasma: destello de 4 puntas
        estrella = [
            (cx, 14), (cx + 12, cy - 12), (114, cy), (cx + 12, cy + 12),
            (cx, 114), (cx - 12, cy + 12), (14, cy), (cx - 12, cy - 12)
        ]
        pygame.draw.polygon(surf, color, estrella)
        pygame.draw.circle(surf, claro, (cx, cy), 14)

    return surf


creados = 0
for poke_id, datos in CATALOGO_POKEMONS.items():
    for ataque in datos.get("habilidades", []):
        nombre_ataque = ataque["nombre"] if isinstance(ataque, dict) else str(ataque)
        tipo_ataque = (ataque.get("tipo") if isinstance(ataque, dict) else None) or datos.get("tipo", "NORMAL")
        archivo = f"{normalizar_nombre(nombre_ataque)}.png"
        ruta = os.path.join(CARPETA_EFECTOS, archivo)

        # No sobrescribe los efectos que ya dibujaste/tenías antes
        if not os.path.exists(ruta):
            color = COLORES_TIPO.get(tipo_ataque.upper(), (200, 200, 200))
            img = dibujar_efecto(tipo_ataque, color)
            pygame.image.save(img, ruta)
            creados += 1
            print(f"[CREADO] {archivo} ({tipo_ataque})")

print(f"\nListo: {creados} efectos nuevos generados en {CARPETA_EFECTOS}/")