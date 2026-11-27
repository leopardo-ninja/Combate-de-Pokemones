# ----------------- RECURSOS: carga, escalado y caché de imágenes -----------------
import os
import pygame

from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL
)
from escenarios import ESCENARIOS

# Bases del escenario (posición y escala en coordenadas virtuales 1920x1080)
BASE_IA_CENTRO = (1300, 500)        # Posicion Arena IA
BASE_JUG_ARRIBA = (640, 700)        # Posicion Arena Jugador
ESCALA_BASE_IA = 5
ESCALA_BASE_JUG = 5

# Cajas de vida
ESCALA_CAJA = 1.5                   # Dimension

# Barra de mensajes
RUTA_BARRA_MSJ = "assets/ui/barra_mensaje.png"
BARRA_MSJ_RECT = pygame.Rect(100, 850, 1500, 210)   # x, y, ancho, alto
BARRA_MSJ_CAP_IZQ = 14      # px de la imagen original que forman el extremo izquierdo
BARRA_MSJ_CAP_DER = 26      # px del extremo derecho (incluye la pestana gris)

# Cajas de los ataques
ESCALA_ATAQUE = 1.8                  # Tamaño de las cajas de ataque
TAM_ATAQUE = (int(124 * ESCALA_ATAQUE), int(55 * ESCALA_ATAQUE))

# Cajas del equipo (cambiar de pokemon)
ESCALA_EQUIPO = 2.4                    # Tamaño de las cajas
TAM_EQUIPO = (int(78 * ESCALA_EQUIPO), int(49 * ESCALA_EQUIPO))

# Bolas del equipo en el HUD (3 por lado): cuánto se agrandan los sprites (pixel art)
ESCALA_BOLAS_EQUIPO = 2

# Tipo del ataque -> archivo de la caja
CAJA_POR_TIPO = {"Normal": "normal", "Fuego": "fire", "Agua": "water", "Planta": "grass",
                 "Eléctrico": "electric", "Tierra": "ground", "Psíquico": "psychic", "Estado": "unknown"}

# Cachés de imágenes ya preparadas (para no leer el disco en cada frame)
_CACHE_POKEMONS = {}
_CACHE_FONDOS = {}
_CACHE_BASES = {}
_CACHE_CAJAS = {}
_CACHE_ESCENARIOS = {}
_CACHE_VISTA_PREVIA = {}
_CACHE_BARRA_MSJ = {}
_CACHE_ATAQUES = {}
_CACHE_EQUIPO = {}
_CACHE_BOLAS_EQUIPO = {}


def obtener_pokemon(nombre, vista, tamaño, color_respaldo=None):
    #Cargar las imagenes de los pokemons
    # La clave identifica la imagen: nombre del Pokémon, vista ("frente" o "espalda") y tamaño
    clave = (nombre, vista, tamaño)
    if clave not in _CACHE_POKEMONS:
        ruta = f"assets/pokemons/{vista}/{nombre}.png"
        # Si existe el PNG se carga y se escala al tamaño pedido
        if os.path.exists(ruta):
            img = pygame.image.load(ruta).convert_alpha()
            _CACHE_POKEMONS[clave] = pygame.transform.scale(img, tamaño)
        # Si falta el PNG y se dio un color de respaldo, se usa un cuadro de ese color
        elif color_respaldo is not None:
            superficie = pygame.Surface(tamaño)
            superficie.fill(color_respaldo)
            _CACHE_POKEMONS[clave] = superficie
        else:
            _CACHE_POKEMONS[clave] = None
    return _CACHE_POKEMONS[clave]


def obtener_fondo(indice):
    #Carga assets/fondos/fondo_XX.png, lo agranda 8 veces y lo sube 72 px. Devuelve None si no existe el archivo
    if indice not in _CACHE_FONDOS:
        ruta = f"assets/fondos/fondo_{indice:02d}.png"
        if not os.path.exists(ruta):
            _CACHE_FONDOS[indice] = None
        else:
            imagen_original = pygame.image.load(ruta).convert_alpha()
            imagen_grande = pygame.transform.scale(imagen_original, (1920, 888))
            # Lienzo del tamaño de la pantalla: se rellena con el color de la esquina inferior derecha y se pega encima la imagen agrandada, así no quedan bordes vacíos
            fondo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
            fondo.fill(tuple(imagen_original.get_at((imagen_original.get_width() - 1, imagen_original.get_height() - 1)))[:3])
            fondo.blit(imagen_grande, (0, -72))
            _CACHE_FONDOS[indice] = fondo
    return _CACHE_FONDOS[indice]


def obtener_base(lado, indice, escala):
    #Carga una base (lado = "rival" o "jugador") y la agranda sin suavizar (pixel art)
    clave = (lado, indice, escala)
    if clave not in _CACHE_BASES:
        ruta = f"assets/bases/{lado}_{indice:02d}.png"
        if os.path.exists(ruta):
            img = pygame.image.load(ruta).convert_alpha()
            _CACHE_BASES[clave] = pygame.transform.scale(img, (int(img.get_width() * escala), int(img.get_height() * escala)))
        else:
            _CACHE_BASES[clave] = None
    return _CACHE_BASES[clave]


def obtener_caja(lado):
    #Carga la caja de vida ("rival" o "jugador") ya escalada
    # Si existe caja_<lado>_hd.png se usa esa (más nítida); si no, la imagen normal.
    # Ambas se escalan al mismo tamaño en pantalla, así las coordenadas de las barras no cambian.
    if lado not in _CACHE_CAJAS:
        ruta = f"assets/ui/caja_{lado}.png"
        ruta_hd = f"assets/ui/caja_{lado}_hd.png"
        if os.path.exists(ruta_hd) and os.path.exists(ruta):
            ancho_logico, alto_logico = pygame.image.load(ruta).get_size()     # tamaño de la imagen normal
            img = pygame.image.load(ruta_hd).convert_alpha()
            tam = (int(ancho_logico * ESCALA_CAJA), int(alto_logico * ESCALA_CAJA))
            _CACHE_CAJAS[lado] = pygame.transform.smoothscale(img, tam)
        elif os.path.exists(ruta):
            img = pygame.image.load(ruta).convert_alpha()
            _CACHE_CAJAS[lado] = pygame.transform.smoothscale(img, (int(img.get_width() * ESCALA_CAJA), int(img.get_height() * ESCALA_CAJA)))
        else:
            _CACHE_CAJAS[lado] = None
    return _CACHE_CAJAS[lado]


def obtener_fondo_escenario(indice):
    #Fondo del escenario: usa fondos.png si el escenario tiene uno asignado; si no, un degradado
    if indice not in _CACHE_ESCENARIOS:
        datos_escenario = ESCENARIOS[indice]
        fondo = None
        # Si el escenario tiene imagen de fondo se usa esa
        if datos_escenario["fondo"] is not None:
            fondo = obtener_fondo(datos_escenario["fondo"])
        # Si no hay imagen, se dibuja un degradado de cielo y un rectángulo de suelo bajo el horizonte
        if fondo is None:
            fondo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
            color_arriba, color_abajo = datos_escenario["cielo"]
            horizonte = 640
            # Cada línea horizontal mezcla color_arriba y color_abajo según su altura (fraccion va de 0 a 1)
            for y in range(horizonte):
                fraccion = y / horizonte
                color = tuple(int(color_arriba[i] + (color_abajo[i] - color_arriba[i]) * fraccion) for i in range(3))
                pygame.draw.line(fondo, color, (0, y), (ANCHO_VIRTUAL, y))
            pygame.draw.rect(fondo, datos_escenario["suelo"], (0, horizonte, ANCHO_VIRTUAL, ALTO_VIRTUAL - horizonte))
        _CACHE_ESCENARIOS[indice] = fondo
    return _CACHE_ESCENARIOS[indice]


def dibujar_bases(pantalla, indice):
    #Dibuja las dos bases (rival y jugador) del escenario sobre la superficie dada
    #El número de base sale del campo "base" del escenario (ya no depende de su posición en la lista)
    num_base = ESCENARIOS[indice]["base"]
    base_ia = obtener_base("rival", num_base, ESCALA_BASE_IA)
    if base_ia:
        pantalla.blit(base_ia, base_ia.get_rect(center=BASE_IA_CENTRO))
    base_jug = obtener_base("jugador", num_base, ESCALA_BASE_JUG)
    if base_jug:
        pantalla.blit(base_jug, base_jug.get_rect(midtop=BASE_JUG_ARRIBA))


def obtener_vista_previa(indice, tamaño):
    #Miniatura del escenario (fondo + bases) para la pantalla de la arena
    clave = (indice, tamaño)
    if clave not in _CACHE_VISTA_PREVIA:
        escena = obtener_fondo_escenario(indice).copy()
        dibujar_bases(escena, indice)
        _CACHE_VISTA_PREVIA[clave] = pygame.transform.smoothscale(escena, tamaño)
    return _CACHE_VISTA_PREVIA[clave]


# Escala la barra por tramos con 'nearest' (pixel art nitido): los extremos conservan su
# proporcion y solo se estira el centro blanco, asi los bordes no se deforman ni se difuminan.
def obtener_barra_mensaje(ancho, alto):
    clave = (ancho, alto)
    if clave not in _CACHE_BARRA_MSJ:
        # Sin la imagen devuelve None (entonces se dibuja una barra de respaldo)
        if not os.path.exists(RUTA_BARRA_MSJ):
            _CACHE_BARRA_MSJ[clave] = None
            return None
        img = pygame.image.load(RUTA_BARRA_MSJ).convert_alpha()
        ancho_original, alto_original = img.get_size()
        # Esquinas claras de 1 px que sobran en la imagen: se hacen transparentes
        for (x_esquina, y_esquina) in ((0, 0), (1, 0), (0, 1), (ancho_original - 1, 0), (ancho_original - 2, 0), (ancho_original - 1, 1),
                         (0, alto_original - 1), (1, alto_original - 1), (0, alto_original - 2), (ancho_original - 1, alto_original - 1), (ancho_original - 2, alto_original - 1), (ancho_original - 1, alto_original - 2)):
            if img.get_at((x_esquina, y_esquina))[:3] != (74, 66, 66):
                img.set_at((x_esquina, y_esquina), (0, 0, 0, 0))
        # Cuánto se agranda la altura; los extremos usan el mismo factor para no deformarse
        factor_escala = alto / alto_original
        borde_izq = round(BARRA_MSJ_CAP_IZQ * factor_escala)
        borde_der = round(BARRA_MSJ_CAP_DER * factor_escala)
        # Se escalan por separado el extremo izquierdo, el derecho y el centro (solo el centro se estira a lo ancho)
        parte_izq = pygame.transform.scale(img.subsurface((0, 0, BARRA_MSJ_CAP_IZQ, alto_original)), (borde_izq, alto))
        parte_der = pygame.transform.scale(img.subsurface((ancho_original - BARRA_MSJ_CAP_DER, 0, BARRA_MSJ_CAP_DER, alto_original)), (borde_der, alto))
        parte_centro = pygame.transform.scale(img.subsurface((BARRA_MSJ_CAP_IZQ, 0, ancho_original - BARRA_MSJ_CAP_IZQ - BARRA_MSJ_CAP_DER, alto_original)),
                                        (ancho - borde_izq - borde_der, alto))
        # Se pegan las tres partes en una superficie transparente
        barra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        barra.blit(parte_izq, (0, 0))
        barra.blit(parte_centro, (borde_izq, 0))
        barra.blit(parte_der, (ancho - borde_der, 0))
        _CACHE_BARRA_MSJ[clave] = barra
    return _CACHE_BARRA_MSJ[clave]


# Imagen de la caja de ataque según el tipo de la habilidad (usa la de Normal si el tipo no está en la tabla)
def obtener_caja_ataque(tipo):
    clave = CAJA_POR_TIPO.get(tipo, "normal")
    if clave not in _CACHE_ATAQUES:
        ruta = f"assets/ui/ataque_{clave}.png"
        if os.path.exists(ruta):
            _CACHE_ATAQUES[clave] = pygame.transform.smoothscale(pygame.image.load(ruta).convert_alpha(), TAM_ATAQUE)
        else:
            _CACHE_ATAQUES[clave] = None
    return _CACHE_ATAQUES[clave]


# Bolas del indicador de equipo ("jugador" o "rival"). Lee assets/ui/bolas_<lado>.png: una tira con 3 cuadros
# iguales (vivo, caído en grises, vacío) y devuelve {"vivo": imagen, "caido": imagen, "vacio": imagen} ya agrandadas
def obtener_bolas_equipo(lado):
    if lado not in _CACHE_BOLAS_EQUIPO:
        ruta = f"assets/ui/bolas_{lado}.png"
        if os.path.exists(ruta):
            tira = pygame.image.load(ruta).convert_alpha()
            tam = tira.get_height()                                 # cada cuadro es cuadrado
            tam_final = (tam * ESCALA_BOLAS_EQUIPO, tam * ESCALA_BOLAS_EQUIPO)
            _CACHE_BOLAS_EQUIPO[lado] = {}
            for i, estado in enumerate(("vivo", "caido", "vacio")):
                cuadro = tira.subsurface((i * tam, 0, tam, tam))
                _CACHE_BOLAS_EQUIPO[lado][estado] = pygame.transform.scale(cuadro, tam_final)
        else:
            _CACHE_BOLAS_EQUIPO[lado] = None
    return _CACHE_BOLAS_EQUIPO[lado]


def obtener_caja_equipo(seleccionada, apagada=False):
    #Caja del equipo ya escalada. "apagada" la oscurece (Pokémon debilitado o que ya está combatiendo)
    clave = (seleccionada, apagada)
    if clave not in _CACHE_EQUIPO:
        ruta = f"assets/ui/equipo_{'seleccionado' if seleccionada else 'normal'}.png"
        if os.path.exists(ruta):
            img = pygame.transform.scale(pygame.image.load(ruta).convert_alpha(), TAM_EQUIPO)
            if apagada:
                img.fill((120, 120, 120, 255), special_flags=pygame.BLEND_RGBA_MULT)
            _CACHE_EQUIPO[clave] = img
        else:
            _CACHE_EQUIPO[clave] = None
    return _CACHE_EQUIPO[clave]