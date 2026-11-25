# ----------------- Parte Visual del Programa -----------------
import os
import pygame

import sonido
import efectos
from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL, ANCHO_REAL, ALTO_REAL,
    BLANCO, NEGRO, GRIS_CLARO, GRIS_OSCURO, AZUL_DS, AZUL_OSCURO,
    ROJO_BOTON, VERDE_BOTON, AZUL_BOTON, BORDE_CAJA, AMARILLO_ALERTA, ROJO_ALERTA,
    COLORES_TIPO, FUENTE, FUENTE_CHICA, FUENTE_GRANDE, FUENTE_HABILIDAD, RUTA_FUENTE
)
from pokemons import SECCIONES_POKEMON, CATALOGO_POKEMONS, LISTA_PLANA_POKES
from escenarios import ESCENARIOS


# ----------------- UTILIDADES -----------------
# Caché de imágenes de pokémons ya cargadas y escaladas, para no leer el disco en cada frame
_CACHE_POKEMONS = {}


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


# Caché de los fondos ya preparados
_CACHE_FONDOS = {}


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


# Convierte la posición del mouse de la pantalla real a la virtual (1920x1080), porque todo se dibuja en la virtual y luego se escala
def pos_virtual(pos):
    #Posicion del mouse
    return (int(pos[0] * ANCHO_VIRTUAL / ANCHO_REAL), int(pos[1] * ALTO_VIRTUAL / ALTO_REAL))


# ----------------- RESALTADO UNICO DE BOTONES -----------------
COLOR_RESALTE = (222, 239, 255)        # linea interior (plateado)
COLOR_RESALTE_BORDE = (30, 30, 30)     # contorno exterior oscuro


def dibujar_resalte(pantalla, rect, radio=12):
    """Resalte unico de todo el juego: borde doble, oscuro por fuera y plateado por dentro."""
    pygame.draw.rect(pantalla, COLOR_RESALTE_BORDE, rect.inflate(8, 8), 8, border_radius=radio + 2)
    pygame.draw.rect(pantalla, COLOR_RESALTE, rect.inflate(4, 4), 4, border_radius=radio)


# Parte un texto largo en líneas que quepan en max_ancho píxeles (para mensajes y descripciones)
def separar_texto_en_lineas(texto, fuente, max_ancho):
    # Se arma cada línea palabra por palabra
    palabras = texto.split(" ")
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        prueba = linea_actual + palabra + " "
        # Si la palabra cabe, se añade a la línea; si no, se cierra la línea y se empieza otra
        if fuente.size(prueba)[0] < max_ancho:
            linea_actual = prueba
        else:
            lineas.append(linea_actual)
            linea_actual = palabra + " "
    lineas.append(linea_actual)
    return lineas


class Boton:
    # Botón rectangular reactivo con texto

    def __init__(self, x, y, ancho, alto, texto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto

    def contiene(self, pos_real):
        """True si la posición del mouse (pantalla real) cae sobre el botón."""
        return self.rect.collidepoint(pos_virtual(pos_real))

    def dibujar(self, superficie, resaltado=False):
        color = BLANCO
        # Fondo azul con borde blanco; si el botón está resaltado se añade el borde doble del resalte
        pygame.draw.rect(superficie, AZUL_OSCURO, self.rect, border_radius=12)
        pygame.draw.rect(superficie, color, self.rect, 4, border_radius=12)
        if resaltado:
            dibujar_resalte(superficie, self.rect)
        txt = FUENTE.render(self.texto, True, color)
        superficie.blit(txt, txt.get_rect(center=self.rect.center))


# ----------------- COMBATE -----------------
# Paleta de colores por tipo de Pokémon (se usa como respaldo si falta alguna imagen del combate)
TEMAS_TIPO_COMBATE = {
    "Fuego": {"fondo_top": (70, 25, 15), "fondo_bot": (35, 12, 8), "suelo_rival": (110, 45, 25), "suelo_jug": (130, 55, 30), "principal": (235, 100, 40)},
    "Agua": {"fondo_top": (15, 40, 75), "fondo_bot": (8, 20, 40), "suelo_rival": (30, 80, 130), "suelo_jug": (40, 100, 160), "principal": (40, 130, 235)},
    "Planta": {"fondo_top": (25, 60, 30), "fondo_bot": (12, 30, 15), "suelo_rival": (50, 110, 60), "suelo_jug": (65, 135, 75), "principal": (50, 180, 70)},
    "Eléctrico": {"fondo_top": (75, 70, 20), "fondo_bot": (35, 32, 8), "suelo_rival": (120, 110, 30), "suelo_jug": (145, 135, 35), "principal": (240, 205, 30)},
    "Tierra": {"fondo_top": (65, 45, 25), "fondo_bot": (30, 20, 10), "suelo_rival": (100, 75, 45), "suelo_jug": (125, 95, 55), "principal": (170, 120, 60)},
}

# ----------------- ESCENARIOS, BASES Y CAJAS DE VIDA -----------------
# Posiciones del combate (coordenadas virtuales 1920x1080)

POS_POKEMON_IA = (1030, 160)        # Posicion Pokemon IA
POS_POKEMON_JUG = (300, 350)        # Posicion Pokemon Jugador
BASE_IA_CENTRO = (1300, 500)        # Posicion Arena IA
BASE_JUG_ARRIBA = (640, 700)        # Posicion Arena Jugador
ESCALA_BASE_IA = 5
ESCALA_BASE_JUG = 5

# Cajas de vida (Jugador y Rival)
ESCALA_CAJA = 1.5 #Dimesion
BARRA_CAJA = {"rival": (93, 40, 211, 49), "jugador": (116, 40, 233, 49)}        #Barra de vida
POS_CAJA = {"rival": (600, 100), "jugador": (1200, 650)}                        #Posicion caja de vida

# Cachés de imágenes ya preparadas: bases, cajas de vida, fondos de escenario y miniaturas
_CACHE_BASES = {}
_CACHE_CAJAS = {}
_CACHE_ESCENARIOS = {}
_CACHE_VISTA_PREVIA = {}


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
    if lado not in _CACHE_CAJAS:
        ruta = f"assets/ui/caja_{lado}.png"
        if os.path.exists(ruta):
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


# ----------------- DIBUJAR PANTALLA DE COMBATE RESPONSIVA -----------------


# Botones pantalla combate (x, y, ancho, alto)
RECT_LUCHAR = pygame.Rect(900, 880, 260, 60)                # LUCHAR 
RECT_CAMBIAR = pygame.Rect(1200, 880, 260, 60)              # POKEMON
RECT_VOLVER = pygame.Rect(150, 925, 220, 55)                # VOLVER
RECT_MENU_FIN = pygame.Rect(1200, 925, 260, 60)             # MENU
OFFSET_NOMBRE = {"rival": (12, 11), "jugador": (36, 11)}    # Diferencia de posicion entre los nombres de los pokemons


# Cajas de los ataques
ESCALA_ATAQUE = 1.8                  # Tamaño de las cajas de ataque
ORIGEN_ATAQUES = (545, 905)          # Esquina superior izquierda de la fila de 4 cajas
SEP_ATAQUES = (20, 10)               # Separación horizontal entre cajas (el vertical ya no se usa)
TAM_ATAQUE = (int(124 * ESCALA_ATAQUE), int(55 * ESCALA_ATAQUE))

# Barra de mensajes
RUTA_BARRA_MSJ = "assets/ui/barra_mensaje.png"
BARRA_MSJ_RECT = pygame.Rect(100, 850, 1500, 210)   # x, y, ancho, alto
BARRA_MSJ_CAP_IZQ = 14      # px de la imagen original que forman el extremo izquierdo
BARRA_MSJ_CAP_DER = 26      # px del extremo derecho (incluye la pestana gris)
_CACHE_BARRA_MSJ = {}


# Cajas del equipo (cambiar de pokemon)
ESCALA_EQUIPO = 2.4                    # Tamaño de las cajas
ORIGEN_EQUIPO = (900, 895)             # Esquina superior izquierda de la primera caja (x, y)
SEP_EQUIPO = 15                        # Espacio entre cajas
TAM_EQUIPO = (int(78 * ESCALA_EQUIPO), int(49 * ESCALA_EQUIPO))
BARRA_EQUIPO = (24, 33, 48, 3)         # Barra de vida dentro de la caja: x, y, ancho, alto (píxeles originales)
FUENTE_EQUIPO = pygame.font.Font(RUTA_FUENTE, 17)   # Vida en número
_CACHE_EQUIPO = {}


def obtener_barra_mensaje(ancho, alto):
    """Escala la barra por tramos con 'nearest' (pixel art nitido): los extremos conservan su
    proporcion y solo se estira el centro blanco, asi los bordes no se deforman ni se difuminan."""
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


# Tipo del ataque -> archivo de la caja
CAJA_POR_TIPO = {"Normal": "normal", "Fuego": "fire", "Agua": "water", "Planta": "grass",
                 "Eléctrico": "electric", "Tierra": "ground", "Psíquico": "psychic", "Estado": "unknown"}
_CACHE_ATAQUES = {}


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


def rect_habilidad(idx):
    # Las 4 habilidades en una sola fila
    return pygame.Rect(ORIGEN_ATAQUES[0] + idx * (TAM_ATAQUE[0] + SEP_ATAQUES[0]),
                       ORIGEN_ATAQUES[1],
                       TAM_ATAQUE[0], TAM_ATAQUE[1])


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


# Rectángulo en pantalla de la caja del Pokémon número idx del equipo (las cajas van en fila)
def rect_pokemon(idx):
    return pygame.Rect(ORIGEN_EQUIPO[0] + idx * (TAM_EQUIPO[0] + SEP_EQUIPO), ORIGEN_EQUIPO[1], TAM_EQUIPO[0], TAM_EQUIPO[1])

# Dibuja el combate y maneja las animaciones
class EscenaCombate:
    
    def __init__(self, combate, escenario=0):
        # Motor de combate (la lógica) que esta escena dibuja
        self.combate = combate
        self.escenario = escenario  # índice en ESCENARIOS (fondo + bases)
        self.hp_visible = {}        # quien -> (nombre, hp mostrado) para animar el vaciado de la barra
        # Frames que le quedan al parpadeo blanco de cada lado cuando recibe daño
        self.flash = {"ia": 0, "jugador": 0}
        self.gestor = efectos.GestorEfectos()   # animaciones de las habilidades
        # Texto de daño que sube sobre cada Pokémon: (texto, frames restantes)
        self.texto_flotante = {"ia": ("", 0), "jugador": ("", 0)}
        self.seleccion = 0          # botón resaltado (índice en zonas_navegables)
        self._contexto = None       # (turno, sub_menu) para reiniciar la selección al cambiar de menú

    def ocupado(self):
        """True mientras se reproduce la animación de una habilidad."""
        return self.gestor.ocupado()

    def lanzar_habilidad(self, quien, habilidad, al_impactar, mensaje=None):
        """Anima la habilidad; 'al_impactar' (aplicar el daño en el motor) se llama en el golpe."""
        nombre, _potencia, tipo = habilidad
        if mensaje:
            self.combate.mensaje = mensaje
        self.combate.sub_menu = "principal"
        self.gestor.lanzar(quien, nombre, tipo, al_impactar)

    # Lee los eventos que dejó el motor (daño recibido): activa parpadeo, texto flotante y sonido según la eficacia, y los borra
    def _procesar_eventos(self):
        for tipo, objetivo, cantidad, multiplicador in self.combate.eventos:
            if tipo == "daño":
                self.flash[objetivo] = 20
                self.texto_flotante[objetivo] = (f"-{cantidad} HP", 45)
                if multiplicador >= 2.0:
                    sonido.efecto("efectos/hit_super_effective")            # Efecto sonido golpe eficaz
                elif multiplicador <= 0.5 and multiplicador > 0:
                    sonido.efecto("efectos/hit_weak_not_very_effective")    # Efecto sonido golpe poco eficaz
                elif multiplicador > 0:
                    sonido.efecto("efectos/hit_normal_damage")              # Efecto sonido golpe normal
        self.combate.eventos.clear()

    # Dibuja un Pokémon; si acaba de recibir daño parpadea, alternando con una copia blanca cada 4 frames
    def _dibujar_pokemon(self, pantalla, imagen_pokemon, pos, quien):
        if self.flash[quien] > 0:
            self.flash[quien] -= 1
            if (self.flash[quien] // 4) % 2 == 0:
                destello = imagen_pokemon.copy()
                destello.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
                pantalla.blit(destello, pos)
                return
        pantalla.blit(imagen_pokemon, pos)

    # Dibuja el texto de daño subiendo poco a poco mientras dura su contador
    def _dibujar_texto_flotante(self, pantalla, quien, x, y_base):
        texto, timer = self.texto_flotante[quien]
        if timer > 0:
            timer -= 1
            self.texto_flotante[quien] = (texto, timer)
            txt = FUENTE_GRANDE.render(texto, True, (255, 80, 80))
            pantalla.blit(txt, (x, y_base - (45 - timer)))

    def _sincronizar(self):
        """Si cambió de menú, la selección vuelve al primer botón."""
        contexto = (self.combate.turno, self.combate.sub_menu)
        if contexto != self._contexto:
            self._contexto = contexto
            self.seleccion = 0

    def _hp_visible(self, quien, nombre, hp, hp_max):
        """HP que se muestra en la barra: se acerca poco a poco al real para animar el daño."""
        guardado = self.hp_visible.get(quien)
        if guardado is None or guardado[0] != nombre:
            valor = hp
        else:
            valor = guardado[1]
            # Velocidad de la animación: la barra tarda unos 90 frames en vaciarse
            paso = max(0.5, hp_max / 90)
            if valor > hp:
                valor = max(hp, valor - paso)
            elif valor < hp:
                valor = min(hp, valor + paso)
        self.hp_visible[quien] = (nombre, valor)
        return valor

    # Configuracion de la caja de vida Jugador y IA
    def _dibujar_caja_vida(self, pantalla, lado, nombre, hp, hp_max, mostrar_numeros):
        caja = obtener_caja(lado)
        quien = "ia" if lado == "rival" else "jugador"
        # Posición en pantalla de la caja de este lado ("rival" o "jugador")
        caja_x, caja_y = POS_CAJA[lado]
        if caja is None:
            return
        pantalla.blit(caja, (caja_x, caja_y))

        # Nombre y nivel en la parte superior de la caja
        desfase_x, desfase_y = OFFSET_NOMBRE[lado]
        txt_nombre = FUENTE.render(nombre.capitalize(), True, NEGRO)
        pantalla.blit(txt_nombre, (caja_x + int(desfase_x * ESCALA_CAJA), caja_y + int(desfase_y * ESCALA_CAJA)))
        #txt_lvl = FUENTE.render("Lv.70", True, NEGRO)
        #pantalla.blit(txt_lvl, (caja_x + caja.get_width() - txt_lvl.get_width() - int(26 * ESCALA_CAJA), caja_y + int(5 * ESCALA_CAJA)))

        # Barra de vida (se pinta sobre la pista blanca de la imagen)
        barra_x0, barra_y0, barra_x1, barra_y1 = BARRA_CAJA[lado]
        barra_x = caja_x + int(barra_x0 * ESCALA_CAJA)
        barra_y = caja_y + int(barra_y0 * ESCALA_CAJA)
        barra_ancho = int((barra_x1 - barra_x0 + 1) * ESCALA_CAJA)
        barra_alto = int((barra_y1 - barra_y0 + 1) * ESCALA_CAJA)
        hp_mostrado = self._hp_visible(quien, nombre, hp, hp_max)
        proporcion = max(0.0, min(1.0, hp_mostrado / hp_max))
        # Color de la barra según la vida restante: verde si queda más del 50%, amarillo más del 20%, rojo el resto
        if proporcion > 0.5:
            color, brillo = (72, 200, 112), (150, 235, 170)
        elif proporcion > 0.2:
            color, brillo = (240, 200, 48), (255, 235, 130)
        else:
            color, brillo = (232, 64, 48), (255, 140, 120)
        ancho = int(barra_ancho * proporcion)
        # Se dibuja la barra y, encima, una franja más clara para dar brillo
        if ancho > 0:
            pygame.draw.rect(pantalla, color, (barra_x, barra_y, ancho, barra_alto), border_radius=4)
            pygame.draw.rect(pantalla, brillo, (barra_x + 2, barra_y + 2, max(0, ancho - 4), max(1, barra_alto // 3)), border_radius=3)

        # Solo la caja del jugador muestra la vida en números
        if mostrar_numeros:
            txt_hp = FUENTE_CHICA.render(f"{hp} / {hp_max}", True, NEGRO)
            x_num = caja_x + int((barra_x0 + 120) * ESCALA_CAJA)   # borde derecho del texto
            y_num = caja_y + int((barra_y0 + 20) * ESCALA_CAJA)    # borde superior del texto
            pantalla.blit(txt_hp, (x_num - txt_hp.get_width(), y_num))

    def zonas_navegables(self):
        """Botones que se recorren con las flechas (VOLVER solo se pulsa con mouse; con teclado es ESC)."""
        return [z for z in self.zonas_clic() if z[0] != "volver"]

    def mover_seleccion(self, tecla):
        """Mueve el botón resaltado con las flechas."""
        self._sincronizar()
        cantidad_botones = len(self.zonas_navegables())
        if cantidad_botones <= 1:
            return
        # Botones y habilidades van en una sola fila
        paso = 1 if tecla in (pygame.K_RIGHT, pygame.K_DOWN) else -1
        # Con el módulo la selección da la vuelta de un extremo al otro
        self.seleccion = (self.seleccion + paso) % cantidad_botones

    def accion_seleccionada(self):
        # Devuelve la acción del botón resaltado (la que ejecuta ENTER)
        self._sincronizar()
        zonas = self.zonas_navegables()
        if 0 <= self.seleccion < len(zonas):
            return zonas[self.seleccion][0]
        return None

    def seleccionar_en(self, pos_real):
        """Resalta el botón que está bajo el mouse (si hay uno)."""
        self._sincronizar()
        pos = pos_virtual(pos_real)
        for i, (_, rect) in enumerate(self.zonas_navegables()):
            if rect.collidepoint(pos):
                self.seleccion = i

    # Dibuja el botón gris VOLVER de los submenús
    def _dibujar_boton_volver(self, pantalla):
        pygame.draw.rect(pantalla, GRIS_OSCURO, RECT_VOLVER, border_radius=12)
        pygame.draw.rect(pantalla, NEGRO, RECT_VOLVER, 3, border_radius=12)
        txt = FUENTE.render("VOLVER", True, BLANCO)
        pantalla.blit(txt, txt.get_rect(center=RECT_VOLVER.center))

    def zonas_clic(self):
        # Zonas interactuables
        combate = self.combate
        # Combate terminado: solo queda el botón MENU
        if combate.turno == "fin":
            return [("menu", RECT_MENU_FIN)]
        # Mientras juega el rival no hay botones
        if combate.turno != "jugador":
            return []
        # Menú principal: LUCHAR y CAMBIAR
        if combate.sub_menu == "principal":
            return [("luchar", RECT_LUCHAR), ("cambiar", RECT_CAMBIAR)]
        # Submenús: una zona por habilidad o por Pokémon del equipo, más VOLVER (cada zona es (acción, rectángulo))
        if combate.sub_menu == "luchar":
            zonas = [(("habilidad", i), rect_habilidad(i)) for i in range(len(combate.datos_jugador["habilidades"]))]
        elif combate.sub_menu == "cambiar":
            zonas = [(("pokemon", i), rect_pokemon(i)) for i in range(len(combate.equipo_jugador))]
        else:
            return []
        return zonas + [("volver", RECT_VOLVER)]

    def accion_en(self, pos_real):
        """Acción del botón que está bajo la posición del mouse, o None."""
        pos = pos_virtual(pos_real)
        for accion, rect in self.zonas_clic():
            if rect.collidepoint(pos):
                return accion
        return None

    # Dibuja un frame completo del combate. Orden: fondo y bases, pokémons, efectos, cajas de vida, barra de mensajes y botones
    def dibujar(self, pantalla):
        # Avanza un frame la animación activa y procesa el daño recién ocurrido
        self.gestor.actualizar()
        self._procesar_eventos()
        self._sincronizar()
        combate = self.combate
        tema = TEMAS_TIPO_COMBATE.get(combate.datos_jugador["tipo"], TEMAS_TIPO_COMBATE["Fuego"])
        pokemon_ia = obtener_pokemon(combate.nombre_ia, "frente", (500, 500), (200, 50, 50))           #Pokemon rival tamano
        pokemon_jugador = obtener_pokemon(combate.nombre_jugador, "espalda", (680, 680), (50, 100, 200))    #Pokemon aliado tamano

        # Fondo y bases del escenario elegido
        pantalla.blit(obtener_fondo_escenario(self.escenario), (0, 0))
        dibujar_bases(pantalla, self.escenario)

        # Cuánto se mueve cada Pokémon durante la animación (embestida, sacudida...) y su posición final
        desplazamiento_ia = self.gestor.desplazamiento("ia")
        desplazamiento_jugador = self.gestor.desplazamiento("jugador")
        pos_ia = (POS_POKEMON_IA[0] + desplazamiento_ia[0], POS_POKEMON_IA[1] + desplazamiento_ia[1])
        pos_jug = (POS_POKEMON_JUG[0] + desplazamiento_jugador[0], POS_POKEMON_JUG[1] + desplazamiento_jugador[1])
        self._dibujar_pokemon(pantalla, pokemon_ia, pos_ia, "ia") #Pokemon rival posicion
        self._dibujar_pokemon(pantalla, pokemon_jugador, pos_jug, "jugador") #Pokemon aliado posicion
        # Efectos de las habilidades (baldosas de stats sobre la silueta y partículas)
        self.gestor.dibujar_sobre_pokemons(pantalla, {"ia": (pokemon_ia, pos_ia), "jugador": (pokemon_jugador, pos_jug)})
        self.gestor.dibujar(pantalla)
        # Texto de daño sobre cada Pokémon
        self._dibujar_texto_flotante(pantalla, "ia", 1360, 150)
        self._dibujar_texto_flotante(pantalla, "jugador", 500, 470)

        # Cajas de vida: la del rival sin números y la del jugador con ellos
        self._dibujar_caja_vida(pantalla, "rival", combate.nombre_ia, combate.hp_actual_ia, combate.hp_max_ia, False)
        self._dibujar_caja_vida(pantalla, "jugador", combate.nombre_jugador, combate.hp_actual_jugador, combate.hp_max_jugador, True)

        eligiendo_ataque = combate.turno == "jugador" and combate.sub_menu == "luchar"
        # La barra de mensajes se ve siempre, tambien al elegir habilidad
        barra = obtener_barra_mensaje(BARRA_MSJ_RECT.w, BARRA_MSJ_RECT.h)

        # Vida baja = menos del 20% de la vida máxima del Pokémon del jugador (no cuenta al terminar el combate)
        en_peligro = (combate.turno != "fin"
              and 0 < combate.hp_actual_jugador <= combate.hp_max_jugador * 0.2)
        
        if en_peligro:      # Reproduce un sonido si la vida esta baja en bucle
            sonido.loop("efectos/health_low_loop")
        else:
            sonido.parar_loop("efectos/health_low_loop")

        # Dibuja la barra de mensajes o, si falta la imagen, un rectángulo de respaldo
        if barra:
            pantalla.blit(barra, BARRA_MSJ_RECT.topleft)
        else:   # respaldo si falta assets/ui/barra_mensaje.png
            pygame.draw.rect(pantalla, (20, 20, 30), (96, 796, 1728, 228), border_radius=16)
            pygame.draw.rect(pantalla, NEGRO, (100, 800, 1720, 220), border_radius=14)
            pygame.draw.rect(pantalla, GRIS_CLARO, (110, 810, 1700, 200), border_radius=10)
        # Texto dentro de la zona blanca
        if not (combate.turno == "jugador" and combate.sub_menu in ("luchar", "cambiar")):   # al elegir habilidad o Pokémon la barra queda sin mensaje
            # Se parte el mensaje en líneas y el bloque se centra verticalmente en la barra
            lineas = [linea.strip() for linea in separar_texto_en_lineas(combate.mensaje, FUENTE, 1020) if linea.strip()]
            alto_linea = FUENTE.get_linesize()
            y_txt = BARRA_MSJ_RECT.centery - len(lineas) * alto_linea // 2
            for linea in lineas:
                pantalla.blit(FUENTE.render(linea, True, NEGRO), (BARRA_MSJ_RECT.x + 80, y_txt))
                y_txt += alto_linea

        # Menú principal: botones LUCHAR y CAMBIAR/POKÉMON (en 1v1 se llama POKÉMON porque no hay a quién cambiar)
        if combate.turno == "jugador" and combate.sub_menu == "principal" and not self.gestor.ocupado():
            # Texto boton LUCHAR
            pygame.draw.rect(pantalla, ROJO_BOTON, RECT_LUCHAR, border_radius=12)
            pygame.draw.rect(pantalla, NEGRO, RECT_LUCHAR, 3, border_radius=12)
            txt_luchar = FUENTE_GRANDE.render("LUCHAR", True, BLANCO)
            pantalla.blit(txt_luchar, txt_luchar.get_rect(center=RECT_LUCHAR.center)) #900, 880

            # Texto boton POKEMON
            pygame.draw.rect(pantalla, VERDE_BOTON, RECT_CAMBIAR, border_radius=12)
            pygame.draw.rect(pantalla, NEGRO, RECT_CAMBIAR, 3, border_radius=12)
            etiqueta_cambiar = "CAMBIAR" if combate.modo == "3v3" else "POKÉMON"
            texto_cambiar = FUENTE_GRANDE.render(etiqueta_cambiar, True, BLANCO)
            pantalla.blit(texto_cambiar, texto_cambiar.get_rect(center=RECT_CAMBIAR.center))

        # Submenú de habilidades: una caja por habilidad, con su nombre y su potencia
        elif combate.turno == "jugador" and combate.sub_menu == "luchar":
            habilidades = combate.datos_jugador["habilidades"]
            for idx, habilidad in enumerate(habilidades):
                nombre_habilidad, potencia, tipo_habilidad = habilidad
                rect_boton = rect_habilidad(idx)
                caja = obtener_caja_ataque(tipo_habilidad)
                if caja:
                    pantalla.blit(caja, rect_boton.topleft)
                else:   # respaldo si falta la imagen
                    pygame.draw.rect(pantalla, tema["principal"], rect_boton, border_radius=12)
                    pygame.draw.rect(pantalla, NEGRO, rect_boton, 3, border_radius=12)
                # Nombre del ataque en la mitad de arriba de la caja
                texto_habilidad = FUENTE_HABILIDAD .render(nombre_habilidad, True, NEGRO)
                max_ancho = int(100 * ESCALA_ATAQUE)
                if texto_habilidad.get_width() > max_ancho:   # si no cabe, se reduce
                    texto_habilidad = pygame.transform.smoothscale(texto_habilidad, (max_ancho, int(texto_habilidad.get_height() * max_ancho / texto_habilidad.get_width())))
                pantalla.blit(texto_habilidad, texto_habilidad.get_rect(midleft=(rect_boton.x + int(12 * ESCALA_ATAQUE), rect_boton.y + int(19 * ESCALA_ATAQUE))))
                # Potencia, en el lugar donde iba "PP /"
                txt_pot = FUENTE_HABILIDAD .render(f"Pot. {potencia}" if potencia > 0 else "Pot. -", True, (60, 75, 60))
                pantalla.blit(txt_pot, txt_pot.get_rect(midleft=(rect_boton.x + int(53 * ESCALA_ATAQUE), rect_boton.y + int(36 * ESCALA_ATAQUE))))
            self._dibujar_boton_volver(pantalla)

        # Submenú del equipo: una caja por Pokémon con miniatura, nombre y vida
        elif combate.turno == "jugador" and combate.sub_menu == "cambiar":
            escala_equipo = ESCALA_EQUIPO
            for idx, pokemon_equipo in enumerate(combate.equipo_jugador):
                rect_boton = rect_pokemon(idx)
                hp_actual = combate.hp_jugador[pokemon_equipo]
                hp_max = CATALOGO_POKEMONS[pokemon_equipo]["hp"]
                elegido = (idx == self.seleccion)
                # Se oscurece al Pokémon debilitado o al que ya está combatiendo
                apagado = hp_actual <= 0 or idx == combate.idx_activo_jugador
                caja = obtener_caja_equipo(elegido, apagado)
                if caja:
                    pantalla.blit(caja, rect_boton.topleft)
                else:   # respaldo si falta la imagen
                    pygame.draw.rect(pantalla, GRIS_OSCURO if apagado else AZUL_BOTON, rect_boton, border_radius=12)
                    pygame.draw.rect(pantalla, NEGRO, rect_boton, 3, border_radius=12)

                # Miniatura del Pokémon (arriba a la izquierda)
                lado_miniatura = int(26 * escala_equipo)
                miniatura = obtener_pokemon(pokemon_equipo, "frente", (lado_miniatura, lado_miniatura), (90, 90, 90))
                if miniatura:
                    if hp_actual <= 0:
                        miniatura = miniatura.copy()
                        miniatura.fill((110, 110, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)
                    pantalla.blit(miniatura, (rect_boton.x + int(3 * escala_equipo), rect_boton.y + int(3 * escala_equipo)))

                # Nombre (a la derecha de la miniatura; se reduce si no cabe)
                txt_nombre = FUENTE_CHICA.render(pokemon_equipo.capitalize(), True, (20, 40, 80) if elegido else BLANCO)
                max_ancho = int(44 * escala_equipo)
                if txt_nombre.get_width() > max_ancho:
                    txt_nombre = pygame.transform.smoothscale(txt_nombre, (max_ancho, int(txt_nombre.get_height() * max_ancho / txt_nombre.get_width())))
                pantalla.blit(txt_nombre, txt_nombre.get_rect(midleft=(rect_boton.x + int(31 * escala_equipo), rect_boton.y + int(15 * escala_equipo))))

                # Barra de vida (sobre la pista de la imagen)
                barra_x, barra_y, barra_ancho, barra_alto = BARRA_EQUIPO
                proporcion_vida = max(0.0, min(1.0, hp_actual / hp_max))
                if proporcion_vida > 0.5:
                    color, brillo = (72, 200, 112), (150, 235, 170)
                elif proporcion_vida > 0.2:
                    color, brillo = (240, 200, 48), (255, 235, 130)
                else:
                    color, brillo = (232, 64, 48), (255, 140, 120)
                ancho_relleno = int(barra_ancho * escala_equipo * proporcion_vida)
                if ancho_relleno > 0:
                    relleno_x, relleno_y, relleno_alto = rect_boton.x + int(barra_x * escala_equipo), rect_boton.y + int(barra_y * escala_equipo), int(barra_alto * escala_equipo)
                    pygame.draw.rect(pantalla, color, (relleno_x, relleno_y, ancho_relleno, relleno_alto))
                    pygame.draw.rect(pantalla, brillo, (relleno_x, relleno_y, ancho_relleno, max(1, relleno_alto // 3)))

                # Vida actual en número, debajo de la barra
                txt_hp = FUENTE_EQUIPO.render(f"{hp_actual} / {hp_max}", True, NEGRO)
                pantalla.blit(txt_hp, txt_hp.get_rect(midright=(rect_boton.x + int(74 * escala_equipo), rect_boton.y + int(42 * escala_equipo))))
            self._dibujar_boton_volver(pantalla)

        elif combate.turno == "fin":
            # Fin del combate, volver al menu
            pygame.draw.rect(pantalla, AZUL_BOTON, RECT_MENU_FIN, border_radius=12)
            pygame.draw.rect(pantalla, NEGRO, RECT_MENU_FIN, 3, border_radius=12)
            txt_menu = FUENTE.render("MENU", True, BLANCO)
            pantalla.blit(txt_menu, txt_menu.get_rect(center=RECT_MENU_FIN.center))

        # Borde en el botón seleccionado (con flechas o con el mouse)
        zonas = self.zonas_navegables()
        if 0 <= self.seleccion < len(zonas) and not self.gestor.ocupado():
            # En el cambio de Pokémon la propia caja seleccionada ya marca la selección
            es_equipo = combate.turno == "jugador" and combate.sub_menu == "cambiar" and isinstance(zonas[self.seleccion][0], tuple)
            if not es_equipo:
                dibujar_resalte(pantalla, zonas[self.seleccion][1])
        # VOLVER no se navega con flechas: solo se resalta cuando el mouse está encima
        pos_mouse = pos_virtual(pygame.mouse.get_pos())
        for accion, rect in self.zonas_clic():
            if accion == "volver" and rect.collidepoint(pos_mouse):
                dibujar_resalte(pantalla, rect)


# ----------------- MODO ARENA: formato + escenario -----------------
# Modo Arena: columnas de la cuadrícula de escenarios, tamaño y origen de cada celda, botones de formato y vista previa
COLUMNAS_ARENA = 6
CELDA_ARENA = (215, 150)
ORIGEN_ARENA = (60, 220)
RECT_FORMATOS = [pygame.Rect(60, 110, 300, 70), pygame.Rect(380, 110, 300, 70)]
FORMATOS = ["1v1", "3v3"]
TAM_VISTA_PREVIA = (480, 270)
POS_VISTA_PREVIA = (1380, 220)


# Rectángulo de la celda número idx de la cuadrícula (fila y columna salen con divmod)
def rect_celda_arena(idx):
    fila, col = divmod(idx, COLUMNAS_ARENA)
    return pygame.Rect(ORIGEN_ARENA[0] + col * CELDA_ARENA[0], ORIGEN_ARENA[1] + fila * CELDA_ARENA[1],
                       CELDA_ARENA[0] - 10, CELDA_ARENA[1] - 10)


class EscenaArena:
    """Pantalla del modo Arena: se elige el formato (1v1 / 3v3) y el escenario."""

    def __init__(self):
        self.formato = 0          # índice en FORMATOS
        self.escenario = 0        # índice en ESCENARIOS
        self.foco = "grid"        # "formato" o "grid": dónde están las flechas

    @property
    def modo(self):
        return FORMATOS[self.formato]

    # Flechas. Con el foco en "formato": izquierda/derecha cambian 1v1/3v3 y abajo baja a la cuadrícula.
    # En la cuadrícula: se mueve entre escenarios y, desde la primera fila, arriba sube al formato
    def mover(self, tecla):
        cantidad_escenarios = len(ESCENARIOS)
        if self.foco == "formato":
            if tecla == pygame.K_LEFT:
                self.formato = 0
            elif tecla == pygame.K_RIGHT:
                self.formato = 1
            elif tecla == pygame.K_DOWN:
                self.foco = "grid"
            return
        fila, col = divmod(self.escenario, COLUMNAS_ARENA)
        if tecla == pygame.K_LEFT and col > 0:
            self.escenario -= 1
        elif tecla == pygame.K_RIGHT and self.escenario + 1 < cantidad_escenarios and col < COLUMNAS_ARENA - 1:
            self.escenario += 1
        elif tecla == pygame.K_DOWN:
            self.escenario = min(self.escenario + COLUMNAS_ARENA, cantidad_escenarios - 1)
        elif tecla == pygame.K_UP:
            if fila == 0:
                self.foco = "formato"
            else:
                self.escenario -= COLUMNAS_ARENA

    def elegir(self):
        """ENTER: en el formato baja a los escenarios; en un escenario continúa. Devuelve 'continuar' o None."""
        if self.foco == "formato":
            self.foco = "grid"
            return None
        return "continuar"

    # Mouse encima: el foco pasa al formato o escenario que esté bajo el cursor
    def pasar_mouse(self, pos_real):
        pos = pos_virtual(pos_real)
        for i, rect_boton in enumerate(RECT_FORMATOS):
            if rect_boton.collidepoint(pos):
                self.foco = "formato"
                self.formato = i
                return
        for i in range(len(ESCENARIOS)):
            if rect_celda_arena(i).collidepoint(pos):
                self.foco = "grid"
                self.escenario = i
                return

    # Clic sobre un formato lo elige; sobre un escenario lo elige y devuelve "continuar"
    def clic(self, pos_real):
        pos = pos_virtual(pos_real)
        for i, rect_boton in enumerate(RECT_FORMATOS):
            if rect_boton.collidepoint(pos):
                self.foco = "formato"
                self.formato = i
                return None
        for i in range(len(ESCENARIOS)):
            if rect_celda_arena(i).collidepoint(pos):
                self.foco = "grid"
                self.escenario = i
                return "continuar"
        return None

    def dibujar(self, pantalla):
        pantalla.fill((25, 28, 40))
        pantalla.blit(FUENTE_GRANDE.render("MODO ARENA", True, BLANCO), (60, 30))

        # Formato
        for i, rect_formato in enumerate(RECT_FORMATOS):
            activo = (i == self.formato)
            pygame.draw.rect(pantalla, VERDE_BOTON if activo else (45, 52, 75), rect_formato, border_radius=12)
            pygame.draw.rect(pantalla, BLANCO if activo else (90, 105, 140), rect_formato, 3, border_radius=12)
            etiqueta = "1 vs 1" if i == 0 else "3 vs 3"
            txt = FUENTE_GRANDE.render(etiqueta, True, BLANCO)
            pantalla.blit(txt, txt.get_rect(center=rect_formato.center))
            if self.foco == "formato" and activo:
                dibujar_resalte(pantalla, rect_formato)

        # Cuadrícula de escenarios
        for i, datos_escenario in enumerate(ESCENARIOS):
            rect_celda = rect_celda_arena(i)
            elegido = (i == self.escenario)
            pygame.draw.rect(pantalla, (55, 65, 100) if elegido else (35, 42, 60), rect_celda, border_radius=12)
            pygame.draw.rect(pantalla, (130, 150, 200) if elegido else (70, 85, 120),
                             rect_celda, 4 if elegido else 2, border_radius=12)
            if elegido and self.foco == "grid":
                dibujar_resalte(pantalla, rect_celda)
            base = obtener_base("rival", datos_escenario["base"], 1.5)
            if base:
                pantalla.blit(base, base.get_rect(center=(rect_celda.centerx, rect_celda.y + 62)))
            txt = FUENTE_CHICA.render(datos_escenario["nombre"], True, BLANCO)
            pantalla.blit(txt, txt.get_rect(center=(rect_celda.centerx, rect_celda.bottom - 22)))

        # Vista previa del escenario elegido
        vista_x, vista_y = POS_VISTA_PREVIA
        pygame.draw.rect(pantalla, (40, 45, 65), (vista_x - 20, vista_y - 20, TAM_VISTA_PREVIA[0] + 40, 460), border_radius=15)
        pygame.draw.rect(pantalla, AZUL_DS, (vista_x - 20, vista_y - 20, TAM_VISTA_PREVIA[0] + 40, 460), 4, border_radius=15)
        pantalla.blit(obtener_vista_previa(self.escenario, TAM_VISTA_PREVIA), (vista_x, vista_y))
        pygame.draw.rect(pantalla, NEGRO, (vista_x, vista_y, TAM_VISTA_PREVIA[0], TAM_VISTA_PREVIA[1]), 3)
        nombre = FUENTE_GRANDE.render(ESCENARIOS[self.escenario]["nombre"], True, (255, 230, 50))
        pantalla.blit(nombre, nombre.get_rect(center=(vista_x + TAM_VISTA_PREVIA[0] // 2, vista_y + TAM_VISTA_PREVIA[1] + 50)))
        modo = FUENTE.render(f"Formato: {self.modo}", True, BLANCO)
        pantalla.blit(modo, modo.get_rect(center=(vista_x + TAM_VISTA_PREVIA[0] // 2, vista_y + TAM_VISTA_PREVIA[1] + 100)))

        # Texto de ayuda con los controles
        ayuda = FUENTE.render("Flechas: mover  |  ENTER / clic: elegir escenario  |  ESC: volver", True, (180, 190, 210))
        pantalla.blit(ayuda, (60, 1020))


# ----------------- PANTALLAS -----------------
# Dibuja el menú principal: panel azul, título y botones (el seleccionado lleva resalte)
def dibujar_menu_principal(pantalla, botones, seleccion_idx):
    pantalla.fill((20, 35, 60))
    pygame.draw.rect(pantalla, AZUL_DS, (610, 240, 700, 600), border_radius=20)
    pygame.draw.rect(pantalla, BLANCO, (610, 240, 700, 600), 6, border_radius=20)

    titulo = FUENTE_GRANDE.render("POKÉMON AÑIL - DUELO", True, BLANCO)
    pantalla.blit(titulo, (720, 300))

    for idx, boton in enumerate(botones):
        boton.dibujar(pantalla, resaltado=(idx == seleccion_idx))

    texto_ayuda = FUENTE_CHICA.render("Usa Flechas ARRIBA/ABAJO y ENTER para seleccionar", True, (200, 220, 240))
    pantalla.blit(texto_ayuda, (710, 800))


# ----------------- SELECCIÓN DE POKÉMONS (cuadrícula) -----------------
# Misma idea que la arena: cuadrícula de celdas con foco por flechas/mouse y panel de vista previa a la derecha
COLUMNAS_SEL = 6
CELDA_SEL = (215, 150)
ORIGEN_SEL = (60, 120)
FILAS_VISIBLES_SEL = 5                     # filas que caben en pantalla; si hay más, la cuadrícula se desplaza
RECT_PANEL_SEL = pygame.Rect(1360, 120, 520, 800)
TAM_SPRITE_CELDA = (96, 96)
TAM_SPRITE_PANEL = (400, 400)


class EscenaSeleccion:
    """Pantalla para elegir el equipo: cuadrícula de pokémons (cada tipo empieza en una fila nueva)."""

    def __init__(self, modo):
        self.modo = modo
        self.meta = 1 if modo == "1v1" else 3     # cuántos pokémons hay que elegir
        self.equipo = []                          # nombres elegidos, en orden
        self.idx = 0                              # pokémon resaltado (índice en self.lista)
        self.scroll = 0                           # primera fila visible

        # Se recorre SECCIONES_POKEMON y a cada pokémon se le asigna (fila, columna); cada tipo empieza una fila nueva
        self.lista = []
        self.tipos = []
        self.pos = []
        fila = 0
        for tipo, pokes in SECCIONES_POKEMON.items():
            for k, nombre in enumerate(pokes):
                self.lista.append(nombre)
                self.tipos.append(tipo)
                self.pos.append((fila + k // COLUMNAS_SEL, k % COLUMNAS_SEL))
            fila += (len(pokes) + COLUMNAS_SEL - 1) // COLUMNAS_SEL
        self.filas = fila
        self.mapa = {p: i for i, p in enumerate(self.pos)}    # (fila, columna) -> índice

    # Rectángulo de la celda i en pantalla (tiene en cuenta el scroll)
    def _rect(self, i):
        fila, col = self.pos[i]
        return pygame.Rect(ORIGEN_SEL[0] + col * CELDA_SEL[0], ORIGEN_SEL[1] + (fila - self.scroll) * CELDA_SEL[1],
                           CELDA_SEL[0] - 10, CELDA_SEL[1] - 10)

    def _visible(self, i):
        return self.scroll <= self.pos[i][0] < self.scroll + FILAS_VISIBLES_SEL

    # Mueve el scroll lo justo para que la fila resaltada siempre se vea
    def _ajustar_scroll(self):
        fila = self.pos[self.idx][0]
        if fila < self.scroll:
            self.scroll = fila
        elif fila >= self.scroll + FILAS_VISIBLES_SEL:
            self.scroll = fila - FILAS_VISIBLES_SEL + 1

    # Flechas: se mueve por la cuadrícula; al subir/bajar a una fila más corta se queda en su última celda
    def mover(self, tecla):
        fila, col = self.pos[self.idx]
        nueva = None
        if tecla == pygame.K_LEFT:
            nueva = self.mapa.get((fila, col - 1))
        elif tecla == pygame.K_RIGHT:
            nueva = self.mapa.get((fila, col + 1))
        elif tecla in (pygame.K_UP, pygame.K_DOWN):
            f = fila + (-1 if tecla == pygame.K_UP else 1)
            while col >= 0 and (f, col) not in self.mapa and 0 <= f < self.filas:
                col -= 1
            nueva = self.mapa.get((f, col))
        if nueva is not None:
            self.idx = nueva
            self._ajustar_scroll()

    # Rueda del mouse: desplaza la cuadrícula de fila en fila
    def desplazar(self, pasos):
        maximo = max(0, self.filas - FILAS_VISIBLES_SEL)
        self.scroll = max(0, min(maximo, self.scroll - pasos))

    # Mouse encima: el resaltado pasa a la celda que esté bajo el cursor
    def pasar_mouse(self, pos_real):
        pos = pos_virtual(pos_real)
        for i in range(len(self.lista)):
            if self._visible(i) and self._rect(i).collidepoint(pos):
                self.idx = i
                return

    # Marca/desmarca el pokémon resaltado. Devuelve "completo" cuando el equipo ya tiene los que pide el modo
    def elegir(self):
        nombre = self.lista[self.idx]
        if nombre in self.equipo:
            self.equipo.remove(nombre)
            return "quitado"
        self.equipo.append(nombre)
        return "completo" if len(self.equipo) == self.meta else "elegido"

    # Clic sobre una celda: la resalta y la elige. Devuelve lo mismo que elegir() o None si no se pulsó ninguna
    def clic(self, pos_real):
        pos = pos_virtual(pos_real)
        for i in range(len(self.lista)):
            if self._visible(i) and self._rect(i).collidepoint(pos):
                self.idx = i
                return self.elegir()
        return None

    def dibujar(self, pantalla):
        pantalla.fill((25, 28, 40))
        titulo = FUENTE_GRANDE.render(f"SELECCIONA TUS POKÉMON ({len(self.equipo)}/{self.meta}) - Modo {self.modo}", True, BLANCO)
        pantalla.blit(titulo, (60, 30))

        # Cuadrícula (recortada para que las filas ocultas por el scroll no se vean)
        pantalla.set_clip(pygame.Rect(0, ORIGEN_SEL[1] - 12, 1350, FILAS_VISIBLES_SEL * CELDA_SEL[1] + 12))
        for i, nombre in enumerate(self.lista):
            if not self._visible(i):
                continue
            rect = self._rect(i)
            elegido = nombre in self.equipo
            resaltado = (i == self.idx)
            pygame.draw.rect(pantalla, (55, 65, 100) if resaltado else (35, 42, 60), rect, border_radius=12)
            # Borde: verde si ya está en el equipo; si no, el color de su tipo
            color_borde = (100, 255, 100) if elegido else COLORES_TIPO.get(self.tipos[i], (70, 85, 120))
            pygame.draw.rect(pantalla, color_borde, rect, 4 if (elegido or resaltado) else 2, border_radius=12)
            if resaltado:
                dibujar_resalte(pantalla, rect)
            imagen = obtener_pokemon(nombre, "frente", TAM_SPRITE_CELDA)
            if imagen:
                pantalla.blit(imagen, imagen.get_rect(midtop=(rect.centerx, rect.y + 8)))
            txt = FUENTE_CHICA.render(nombre.capitalize(), True, (100, 255, 100) if elegido else BLANCO)
            pantalla.blit(txt, txt.get_rect(center=(rect.centerx, rect.bottom - 22)))
            # Insignia con el orden en que se eligió
            if elegido:
                centro = (rect.right - 24, rect.y + 24)
                pygame.draw.circle(pantalla, VERDE_BOTON, centro, 16)
                pygame.draw.circle(pantalla, BLANCO, centro, 16, 2)
                num = FUENTE_CHICA.render(str(self.equipo.index(nombre) + 1), True, BLANCO)
                pantalla.blit(num, num.get_rect(center=centro))
        pantalla.set_clip(None)

        # Panel de vista previa del pokémon resaltado
        nombre = self.lista[self.idx]
        datos = CATALOGO_POKEMONS[nombre]
        pygame.draw.rect(pantalla, (40, 45, 65), RECT_PANEL_SEL, border_radius=15)
        pygame.draw.rect(pantalla, AZUL_DS, RECT_PANEL_SEL, 4, border_radius=15)
        imagen = obtener_pokemon(nombre, "frente", TAM_SPRITE_PANEL)
        if imagen:
            pantalla.blit(imagen, imagen.get_rect(midtop=(RECT_PANEL_SEL.centerx, RECT_PANEL_SEL.y + 20)))
        txt = FUENTE_GRANDE.render(nombre.upper(), True, (255, 230, 50))
        pantalla.blit(txt, txt.get_rect(center=(RECT_PANEL_SEL.centerx, RECT_PANEL_SEL.y + 450)))
        txt = FUENTE.render(f"Tipo: {datos['tipo']} | HP: {datos['hp']}", True, (255, 220, 50))
        pantalla.blit(txt, txt.get_rect(center=(RECT_PANEL_SEL.centerx, RECT_PANEL_SEL.y + 500)))

        # Equipo elegido hasta ahora
        pantalla.blit(FUENTE.render(f"Equipo ({len(self.equipo)}/{self.meta}):", True, (200, 220, 250)), (RECT_PANEL_SEL.x + 30, RECT_PANEL_SEL.y + 560))
        for k, elegido_nombre in enumerate(self.equipo):
            pantalla.blit(FUENTE.render(f"{k + 1}. {elegido_nombre.capitalize()}", True, (100, 255, 100)),
                          (RECT_PANEL_SEL.x + 30, RECT_PANEL_SEL.y + 605 + k * 40))

        ayuda = "Flechas + ENTER para elegir (otra vez para quitar) | ESC para volver"
        if self.filas > FILAS_VISIBLES_SEL:
            ayuda += " | Rueda del mouse para desplazar"
        pantalla.blit(FUENTE_CHICA.render(ayuda, True, (200, 220, 240)), (60, 1015))


# Muestra las estadísticas de cada Pokémon del equipo antes de empezar el combate
def dibujar_estadisticas(pantalla, equipo_seleccionado):
        pantalla.fill((30, 144, 255))
        pygame.draw.rect(pantalla, (240, 245, 255), (100, 80, 1720, 920), border_radius=15)
        pygame.draw.rect(pantalla, (20, 80, 160), (100, 80, 1720, 920), 5, border_radius=15)

        pygame.draw.rect(pantalla, (20, 80, 160), (100, 80, 1720, 70), border_top_left_radius=15, border_top_right_radius=15)
        texto_encabezado = FUENTE.render("ESTADÍSTICAS DEL EQUIPO SELECCIONADO", True, BLANCO)
        pantalla.blit(texto_encabezado, (140, 100))

        # Una tarjeta por Pokémon, separadas 560 px entre sí
        for i, pokemon_elegido in enumerate(equipo_seleccionado):
            datos_pokemon = CATALOGO_POKEMONS[pokemon_elegido]
            tarjeta_x = 140 + (i * 560)
            tarjeta_y = 180

            pygame.draw.rect(pantalla, BLANCO, (tarjeta_x, tarjeta_y, 500, 680), border_radius=12)
            pygame.draw.rect(pantalla, (100, 150, 200), (tarjeta_x, tarjeta_y, 500, 680), 3, border_radius=12)

            imagen_frente = obtener_pokemon(pokemon_elegido, "frente", (250, 250))
            if imagen_frente:
                pantalla.blit(imagen_frente, (tarjeta_x + 125, tarjeta_y + 20))

            texto_nombre = FUENTE_GRANDE.render(pokemon_elegido.upper(), True, NEGRO)
            pantalla.blit(texto_nombre, (tarjeta_x + 30, tarjeta_y + 290))

            texto_tipo = FUENTE.render(f"Tipo: {datos_pokemon['tipo']} | Nv. 70", True, AZUL_OSCURO)
            pantalla.blit(texto_tipo, (tarjeta_x + 30, tarjeta_y + 350))

            lineas_estadisticas = [
                f"HP: {datos_pokemon['hp']}", f"Ataque: {datos_pokemon['ataque']}", f"Defensa: {datos_pokemon['defensa']}",
                f"At. Esp: {datos_pokemon['atk_esp']}", f"Velocidad: {datos_pokemon['velocidad']}"
            ]
            for indice_estadistica, linea in enumerate(lineas_estadisticas):
                texto_estadistica = FUENTE.render(linea, True, NEGRO)
                pantalla.blit(texto_estadistica, (tarjeta_x + 30, tarjeta_y + 420 + (indice_estadistica * 45)))

        # Botón COMENZAR (visual; se confirma con ENTER o ESPACIO)
        rect_boton = pygame.Rect(710, 900, 500, 70)
        pygame.draw.rect(pantalla, (40, 180, 90), rect_boton, border_radius=12)
        texto_comenzar = FUENTE.render("¡COMENZAR COMBATE!", True, BLANCO)
        rect_texto = texto_comenzar.get_rect(center=rect_boton.center)
        pantalla.blit(texto_comenzar, rect_texto)


# Pokédex: tarjetas de pokémons agrupadas por tipo o, si lib_detalle es True, la ficha detallada del resaltado
def dibujar_biblioteca(pantalla, tipo_claves, scroll_offset_lib, lib_detalle, lib_seccion_idx, lib_pokemon_idx):
        pantalla.fill((25, 28, 40))

        titulo_biblioteca = FUENTE_GRANDE.render("BIBLIOTECA POKÉMON (Pokédex)", True, BLANCO)
        pantalla.blit(titulo_biblioteca, (60, 30))

        # Vista de lista
        if not lib_detalle:
            pantalla.set_clip(pygame.Rect(60, 100, 1800, 940))

            y_actual = 110 - scroll_offset_lib
            for indice_seccion, tipo_seccion in enumerate(tipo_claves):
                color_tipo = COLORES_TIPO.get(tipo_seccion, BLANCO)
                texto_encabezado = FUENTE.render(f"--- {tipo_seccion} ---", True, color_tipo)
                pantalla.blit(texto_encabezado, (100, y_actual))
                y_actual += 50

                pokemons_seccion = SECCIONES_POKEMON[tipo_seccion]
                for indice_pokemon, nombre_pokemon in enumerate(pokemons_seccion):
                    # Dos columnas: al volver a la primera se baja una fila (190 px)
                    columna = indice_pokemon % 2
                    if columna == 0 and indice_pokemon > 0:
                        y_actual += 190

                    tarjeta_x = 100 + (columna * 880)
                    tarjeta_y = y_actual

                    esta_resaltado = (indice_seccion == lib_seccion_idx and indice_pokemon == lib_pokemon_idx)
                    color_fondo = (55, 65, 100) if esta_resaltado else (35, 42, 60)
                    color_borde = (130, 150, 200) if esta_resaltado else (70, 85, 120)
                    grosor_borde = 4 if esta_resaltado else 2

                    rect_tarjeta = pygame.Rect(tarjeta_x, tarjeta_y, 840, 170)
                    pygame.draw.rect(pantalla, color_fondo, rect_tarjeta, border_radius=12)
                    pygame.draw.rect(pantalla, color_borde, rect_tarjeta, grosor_borde, border_radius=12)
                    if esta_resaltado:
                        dibujar_resalte(pantalla, rect_tarjeta)

                    imagen_frente = obtener_pokemon(nombre_pokemon, "frente", (140, 140))
                    if imagen_frente:
                        pantalla.blit(imagen_frente, (tarjeta_x + 20, tarjeta_y + 15))

                    texto_nombre = FUENTE_GRANDE.render(nombre_pokemon.capitalize(), True, BLANCO)
                    pantalla.blit(texto_nombre, (tarjeta_x + 190, tarjeta_y + 60))

                y_actual += 210

            pantalla.set_clip(None)

            texto_instrucciones = FUENTE.render("Usa Flechas [ARRIBA/ABAJO/IZQ/DER] | [ENTER] Ver Detalles | [ESC] Volver", True, (180, 190, 210))
            pantalla.blit(texto_instrucciones, (100, 1020))

        else:
            # Vista de detalle: ficha completa del Pokémon elegido (tipo, estadísticas, descripción y habilidades)
            pokemon_seleccionado = SECCIONES_POKEMON[tipo_claves[lib_seccion_idx]][lib_pokemon_idx]
            datos_pokemon = CATALOGO_POKEMONS[pokemon_seleccionado]

            pygame.draw.rect(pantalla, (45, 50, 75), (260, 140, 1400, 800), border_radius=20)
            pygame.draw.rect(pantalla, AZUL_DS, (260, 140, 1400, 800), 5, border_radius=20)

            imagen_frente = obtener_pokemon(pokemon_seleccionado, "frente", (320, 320))
            if imagen_frente:
                pantalla.blit(imagen_frente, (320, 180))

            texto_nombre = FUENTE_GRANDE.render(pokemon_seleccionado.upper(), True, BLANCO)
            pantalla.blit(texto_nombre, (700, 180))

            texto_tipo = FUENTE.render(f"Tipo: {datos_pokemon['tipo']} | HP: {datos_pokemon['hp']}", True, (255, 220, 50))
            pantalla.blit(texto_tipo, (700, 240))

            estadisticas_detalle = f"Ataque: {datos_pokemon['ataque']} | Defensa: {datos_pokemon['defensa']} | Velocidad: {datos_pokemon['velocidad']}"
            texto_estadisticas = FUENTE.render(estadisticas_detalle, True, (200, 220, 240))
            pantalla.blit(texto_estadisticas, (700, 300))

            texto_titulo_descripcion = FUENTE.render("Descripción:", True, (200, 220, 250))
            pantalla.blit(texto_titulo_descripcion, (320, 540))

            # La descripción se parte en líneas de máximo 1200 px
            lineas_descripcion = separar_texto_en_lineas(datos_pokemon["desc"], FUENTE, 1200)
            for indice_linea, linea in enumerate(lineas_descripcion):
                texto_linea = FUENTE.render(linea, True, BLANCO)
                pantalla.blit(texto_linea, (320, 600 + (indice_linea * 40)))

            texto_titulo_habilidades = FUENTE.render("Habilidades:", True, (200, 220, 250))
            pantalla.blit(texto_titulo_habilidades, (320, 720))

            for indice_habilidad, (nombre_habilidad, potencia, tipo_habilidad) in enumerate(datos_pokemon["habilidades"]):
                texto_habilidad = FUENTE.render(f"• {nombre_habilidad} (Potencia: {potencia} | Tipo: {tipo_habilidad})", True, BLANCO)
                pantalla.blit(texto_habilidad, (350, 780 + (indice_habilidad * 40)))

            texto_navegacion = FUENTE.render("Presiona [ESC] o [ENTER] para regresar", True, (180, 190, 210))
            pantalla.blit(texto_navegacion, (720, 870))