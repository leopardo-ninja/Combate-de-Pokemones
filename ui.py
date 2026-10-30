# ----------------- Parte Visual del Progreama -----------------
import os
import pygame

from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL, ANCHO_REAL, ALTO_REAL,
    BLANCO, NEGRO, GRIS_CLARO, GRIS_OSCURO, AZUL_DS, AZUL_OSCURO,
    ROJO_BOTON, VERDE_BOTON, AZUL_BOTON, BORDE_CAJA, AMARILLO_ALERTA, ROJO_ALERTA,
    COLORES_TIPO, FUENTE, FUENTE_CHICA, FUENTE_GRANDE,
)
from pokemons import SECCIONES_POKEMON, CATALOGO_POKEMONS, LISTA_PLANA_POKES
from escenarios import ESCENARIOS


# ----------------- UTILIDADES -----------------
_CACHE_SPRITES = {}


def obtener_sprite(nombre, vista, tamaño, color_respaldo=None):
    #Cargar las imagenes de los pokemons
    clave = (nombre, vista, tamaño)
    if clave not in _CACHE_SPRITES:
        ruta = f"assets/pokemons/{vista}/{nombre}.png"
        if os.path.exists(ruta):
            img = pygame.image.load(ruta).convert_alpha()
            _CACHE_SPRITES[clave] = pygame.transform.scale(img, tamaño)
        elif color_respaldo is not None:
            superficie = pygame.Surface(tamaño)
            superficie.fill(color_respaldo)
            _CACHE_SPRITES[clave] = superficie
        else:
            _CACHE_SPRITES[clave] = None
    return _CACHE_SPRITES[clave]


_HOJA_FONDOS = None
_CACHE_FONDOS = {}


def obtener_fondo(indice):
    #Recorta un fondo de la hoja (3 columnas x 4 filas), lo agranda 8 veces y lo sube 72 px
    global _HOJA_FONDOS
    if indice not in _CACHE_FONDOS:
        if _HOJA_FONDOS is None:
            _HOJA_FONDOS = pygame.image.load("assets/fondos/fondos.png").convert_alpha()
        fila, col = divmod(indice, 3)
        recorte = _HOJA_FONDOS.subsurface((col * 240, fila * 112, 240, 111))
        grande = pygame.transform.scale(recorte, (1920, 888))
        fondo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
        fondo.fill(tuple(recorte.get_at((239, 110)))[:3])   # el color de la franja inferior rellena lo que sobra abajo
        fondo.blit(grande, (0, -72))
        _CACHE_FONDOS[indice] = fondo
    return _CACHE_FONDOS[indice]


def pos_virtual(pos):
    #Posicion del mouse
    return (int(pos[0] * ANCHO_VIRTUAL / ANCHO_REAL), int(pos[1] * ALTO_VIRTUAL / ALTO_REAL))


def separar_texto_en_lineas(texto, fuente, max_ancho):
    palabras = texto.split(" ")
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        prueba = linea_actual + palabra + " "
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
        color = (255, 230, 50) if resaltado else BLANCO
        pygame.draw.rect(superficie, AZUL_OSCURO, self.rect, border_radius=12)
        pygame.draw.rect(superficie, color, self.rect, 4, border_radius=12)
        txt = FUENTE.render(self.texto, True, color)
        superficie.blit(txt, txt.get_rect(center=self.rect.center))


# ----------------- COMBATE -----------------
TEMAS_TIPO_COMBATE = {
    "Fuego": {"fondo_top": (70, 25, 15), "fondo_bot": (35, 12, 8), "suelo_rival": (110, 45, 25), "suelo_jug": (130, 55, 30), "principal": (235, 100, 40)},
    "Agua": {"fondo_top": (15, 40, 75), "fondo_bot": (8, 20, 40), "suelo_rival": (30, 80, 130), "suelo_jug": (40, 100, 160), "principal": (40, 130, 235)},
    "Planta": {"fondo_top": (25, 60, 30), "fondo_bot": (12, 30, 15), "suelo_rival": (50, 110, 60), "suelo_jug": (65, 135, 75), "principal": (50, 180, 70)},
    "Eléctrico": {"fondo_top": (75, 70, 20), "fondo_bot": (35, 32, 8), "suelo_rival": (120, 110, 30), "suelo_jug": (145, 135, 35), "principal": (240, 205, 30)},
    "Tierra": {"fondo_top": (65, 45, 25), "fondo_bot": (30, 20, 10), "suelo_rival": (100, 75, 45), "suelo_jug": (125, 95, 55), "principal": (170, 120, 60)},
}

# ----------------- ESCENARIOS, BASES Y CAJAS DE VIDA -----------------
# Posiciones del combate (coordenadas virtuales 1920x1080)

POS_POKEMON_IA = (1030, 160)          # Posicion Pokemon IA
POS_POKEMON_JUG = (300, 350)        # Posicion Pokemon Jugador
BASE_IA_CENTRO = (1300, 500)        # Posicion Arena IA
BASE_JUG_ARRIBA = (640, 700)        # Posicion Arena Jugador
ESCALA_BASE_IA = 5
ESCALA_BASE_JUG = 5

# Cajas de vida (Jugador y Rival)
ESCALA_CAJA = 1.5 #Dimesion
BARRA_CAJA = {"rival": (93, 40, 211, 49), "jugador": (116, 40, 233, 49)} #Barra de vida
POS_CAJA = {"rival": (600, 100), "jugador": (1200, 650)} #Posicion

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
        esc = ESCENARIOS[indice]
        fondo = None
        if esc["fondo"] is not None and os.path.exists("assets/fondos/fondos.png"):
            fondo = obtener_fondo(esc["fondo"])
        if fondo is None:
            fondo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
            arriba, abajo = esc["cielo"]
            horizonte = 640
            for y in range(horizonte):
                t = y / horizonte
                color = tuple(int(arriba[i] + (abajo[i] - arriba[i]) * t) for i in range(3))
                pygame.draw.line(fondo, color, (0, y), (ANCHO_VIRTUAL, y))
            pygame.draw.rect(fondo, esc["suelo"], (0, horizonte, ANCHO_VIRTUAL, ALTO_VIRTUAL - horizonte))
        _CACHE_ESCENARIOS[indice] = fondo
    return _CACHE_ESCENARIOS[indice]


def dibujar_bases(pantalla, indice):
    #Dibuja las dos bases (rival y jugador) del escenario sobre la superficie dada
    base_ia = obtener_base("rival", indice, ESCALA_BASE_IA)
    if base_ia:
        pantalla.blit(base_ia, base_ia.get_rect(center=BASE_IA_CENTRO))
    base_jug = obtener_base("jugador", indice, ESCALA_BASE_JUG)
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


# Zonas pulsables del combate (coordenadas virtuales 1920x1080)
RECT_LUCHAR = pygame.Rect(1200, 830, 280, 75)
RECT_CAMBIAR = pygame.Rect(1510, 830, 280, 75)
RECT_VOLVER = pygame.Rect(140, 940, 220, 55)
RECT_MENU_FIN = pygame.Rect(1310, 830, 480, 75)
OFFSET_NOMBRE = {"rival": (12, 11), "jugador": (36, 11)}    # Diferencia de posicion entre los nombres de los pokemons


def rect_habilidad(idx):
    return pygame.Rect(1200 if idx % 2 == 0 else 1510, 830 if idx < 2 else 920, 280, 75)


def rect_pokemon(idx):
    return pygame.Rect(1200 + idx * 200, 860, 180, 80)

# Dibuja el combate y maneja las animaciones
class EscenaCombate:
    
    def __init__(self, combate, escenario=0):
        self.combate = combate
        self.escenario = escenario  # índice en ESCENARIOS (fondo + bases)
        self.hp_visible = {}        # quien -> (nombre, hp mostrado) para animar el vaciado de la barra
        self.flash = {"ia": 0, "jugador": 0}
        self.texto_flotante = {"ia": ("", 0), "jugador": ("", 0)}
        self.seleccion = 0          # botón resaltado (índice en zonas_navegables)
        self._contexto = None       # (turno, sub_menu) para reiniciar la selección al cambiar de menú

    def _procesar_eventos(self):
        for tipo, objetivo, cantidad in self.combate.eventos:
            if tipo == "daño":
                self.flash[objetivo] = 20
                self.texto_flotante[objetivo] = (f"-{cantidad} HP", 45)
        self.combate.eventos.clear()

    def _dibujar_sprite(self, pantalla, sprite, pos, quien):
        if self.flash[quien] > 0:
            self.flash[quien] -= 1
            if (self.flash[quien] // 4) % 2 == 0:
                destello = sprite.copy()
                destello.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
                pantalla.blit(destello, pos)
                return
        pantalla.blit(sprite, pos)

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
        px, py = POS_CAJA[lado]
        if caja is None:
            return
        pantalla.blit(caja, (px, py))

        # Nombre y nivel en la parte superior de la caja
        ox, oy = OFFSET_NOMBRE[lado]
        txt_nombre = FUENTE.render(nombre.capitalize(), True, NEGRO)
        pantalla.blit(txt_nombre, (px + int(ox * ESCALA_CAJA), py + int(oy * ESCALA_CAJA)))
        #txt_lvl = FUENTE.render("Lv.70", True, NEGRO)
        #pantalla.blit(txt_lvl, (px + caja.get_width() - txt_lvl.get_width() - int(26 * ESCALA_CAJA), py + int(5 * ESCALA_CAJA)))

        # Barra de vida (se pinta sobre la pista blanca de la imagen)
        bx0, by0, bx1, by1 = BARRA_CAJA[lado]
        rx = px + int(bx0 * ESCALA_CAJA)
        ry = py + int(by0 * ESCALA_CAJA)
        rw = int((bx1 - bx0 + 1) * ESCALA_CAJA)
        rh = int((by1 - by0 + 1) * ESCALA_CAJA)
        visible = self._hp_visible(quien, nombre, hp, hp_max)
        proporcion = max(0.0, min(1.0, visible / hp_max))
        if proporcion > 0.5:
            color, brillo = (72, 200, 112), (150, 235, 170)
        elif proporcion > 0.2:
            color, brillo = (240, 200, 48), (255, 235, 130)
        else:
            color, brillo = (232, 64, 48), (255, 140, 120)
        ancho = int(rw * proporcion)
        if ancho > 0:
            pygame.draw.rect(pantalla, color, (rx, ry, ancho, rh), border_radius=4)
            pygame.draw.rect(pantalla, brillo, (rx + 2, ry + 2, max(0, ancho - 4), max(1, rh // 3)), border_radius=3)

        if mostrar_numeros:
            txt_hp = FUENTE_CHICA.render(f"{hp} / {hp_max}", True, NEGRO)
            x_num = px + int((bx0 + 120) * ESCALA_CAJA)   # borde derecho del texto
            y_num = py + int((by0 + 20) * ESCALA_CAJA)    # borde superior del texto
            pantalla.blit(txt_hp, (x_num - txt_hp.get_width(), y_num))

    def zonas_navegables(self):
        """Botones que se recorren con las flechas (VOLVER solo se pulsa con mouse; con teclado es ESC)."""
        return [z for z in self.zonas_clic() if z[0] != "volver"]

    def mover_seleccion(self, tecla):
        """Mueve el botón resaltado con las flechas."""
        self._sincronizar()
        n = len(self.zonas_navegables())
        if n <= 1:
            return
        c = self.combate
        if c.turno == "jugador" and c.sub_menu == "luchar":
            # Habilidades en cuadrícula 2x2: izquierda/derecha cambian de columna, arriba/abajo de fila
            if tecla in (pygame.K_LEFT, pygame.K_RIGHT):
                nuevo = self.seleccion ^ 1
            else:
                nuevo = (self.seleccion + 2) % 4
            if nuevo < n:
                self.seleccion = nuevo
        else:
            # Botones en una sola fila
            paso = 1 if tecla in (pygame.K_RIGHT, pygame.K_DOWN) else -1
            self.seleccion = (self.seleccion + paso) % n

    def accion_seleccionada(self):
        # Reactividad del bonton al hover
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

    def _dibujar_boton_volver(self, pantalla):
        pygame.draw.rect(pantalla, GRIS_OSCURO, RECT_VOLVER, border_radius=12)
        pygame.draw.rect(pantalla, NEGRO, RECT_VOLVER, 3, border_radius=12)
        txt = FUENTE.render("VOLVER", True, BLANCO)
        pantalla.blit(txt, txt.get_rect(center=RECT_VOLVER.center))

    def zonas_clic(self):
        # Zonas interactuables
        c = self.combate
        if c.turno == "fin":
            return [("menu", RECT_MENU_FIN)]
        if c.turno != "jugador":
            return []
        if c.sub_menu == "principal":
            return [("luchar", RECT_LUCHAR), ("cambiar", RECT_CAMBIAR)]
        if c.sub_menu == "luchar":
            zonas = [(("habilidad", i), rect_habilidad(i)) for i in range(len(c.p_data["habilidades"]))]
        elif c.sub_menu == "cambiar":
            zonas = [(("pokemon", i), rect_pokemon(i)) for i in range(len(c.eq_jugador))]
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

    def dibujar(self, pantalla):
        self._procesar_eventos()
        self._sincronizar()
        combate = self.combate
        tema = TEMAS_TIPO_COMBATE.get(combate.p_data["tipo"], TEMAS_TIPO_COMBATE["Fuego"])
        pokemon_ia = obtener_sprite(combate.i_nombre, "frente", (500, 500), (200, 50, 50))           #Pokemon rival tamano
        pokemon_jugador = obtener_sprite(combate.p_nombre, "espalda", (680, 680), (50, 100, 200))    #Pokemon aliado tamano

        pantalla.blit(obtener_fondo_escenario(self.escenario), (0, 0))
        dibujar_bases(pantalla, self.escenario)

        self._dibujar_sprite(pantalla, pokemon_ia, POS_POKEMON_IA, "ia") #Pokemon rival posicion
        self._dibujar_sprite(pantalla, pokemon_jugador, POS_POKEMON_JUG, "jugador") #Pokemon aliado posicion
        self._dibujar_texto_flotante(pantalla, "ia", 1360, 150)
        self._dibujar_texto_flotante(pantalla, "jugador", 500, 470)

        self._dibujar_caja_vida(pantalla, "rival", combate.i_nombre, combate.i_hp, combate.i_hp_max, False)
        self._dibujar_caja_vida(pantalla, "jugador", combate.p_nombre, combate.p_hp, combate.p_hp_max, True)

        pygame.draw.rect(pantalla, (20, 20, 30), (96, 796, 1728, 228), border_radius=16)
        pygame.draw.rect(pantalla, NEGRO, (100, 800, 1720, 220), border_radius=14)
        pygame.draw.rect(pantalla, GRIS_CLARO, (110, 810, 1700, 200), border_radius=10)
        txt_msj = FUENTE.render(combate.mensaje, True, NEGRO)
        pantalla.blit(txt_msj, (140, 880))

        if combate.turno == "jugador" and combate.sub_menu == "principal":
            pygame.draw.rect(pantalla, ROJO_BOTON, RECT_LUCHAR, border_radius=12)
            pygame.draw.rect(pantalla, NEGRO, RECT_LUCHAR, 3, border_radius=12)
            pantalla.blit(FUENTE_GRANDE.render("LUCHAR", True, BLANCO), (1265, 845))

            pygame.draw.rect(pantalla, VERDE_BOTON, RECT_CAMBIAR, border_radius=12)
            pygame.draw.rect(pantalla, NEGRO, RECT_CAMBIAR, 3, border_radius=12)
            txt_cambio = "CAMBIAR" if combate.modo == "3v3" else "POKÉMON"
            pantalla.blit(FUENTE_GRANDE.render(txt_cambio, True, BLANCO), (1570, 845))

        elif combate.turno == "jugador" and combate.sub_menu == "luchar":
            habilidades = combate.p_data["habilidades"]
            for idx, hab in enumerate(habilidades):
                nombre_h, pot, tipo_h = hab
                r = rect_habilidad(idx)
                bx, by = r.x, r.y
                pygame.draw.rect(pantalla, tema["principal"], r, border_radius=12)
                pygame.draw.rect(pantalla, NEGRO, r, 3, border_radius=12)
                txt_h = FUENTE.render(nombre_h, True, BLANCO)
                pantalla.blit(txt_h, (bx + 25, by + 22))
            self._dibujar_boton_volver(pantalla)

        elif combate.turno == "jugador" and combate.sub_menu == "cambiar":
            for idx, p_eq in enumerate(combate.eq_jugador):
                r = rect_pokemon(idx)
                bx, by = r.x, r.y
                hp_actual_poke = combate.hp_jugador[p_eq]
                col_sel = AZUL_BOTON if hp_actual_poke > 0 else (120, 120, 120)
                if idx == combate.idx_activo_j:
                    col_sel = GRIS_OSCURO

                pygame.draw.rect(pantalla, col_sel, r, border_radius=12)
                pygame.draw.rect(pantalla, NEGRO, r, 3, border_radius=12)
                txt_eq = FUENTE.render(p_eq[:10].capitalize(), True, BLANCO)
                pantalla.blit(txt_eq, (bx + 20, by + 25))
            self._dibujar_boton_volver(pantalla)

        elif combate.turno == "fin":
            txt_r = FUENTE_GRANDE.render("Presiona [ENTER] para volver al Menú Principal", True, ROJO_BOTON)
            pantalla.blit(txt_r, (140, 920))
            pygame.draw.rect(pantalla, AZUL_BOTON, RECT_MENU_FIN, border_radius=12)
            pygame.draw.rect(pantalla, NEGRO, RECT_MENU_FIN, 3, border_radius=12)
            txt_menu = FUENTE.render("VOLVER AL MENÚ", True, BLANCO)
            pantalla.blit(txt_menu, txt_menu.get_rect(center=RECT_MENU_FIN.center))

        if combate.turno == "jugador":
            ayuda = FUENTE_CHICA.render("Flechas: mover  |  ENTER: elegir  |  ESC: volver", True, GRIS_OSCURO)
            pantalla.blit(ayuda, (400, 960))

        # Borde amarillo en el botón seleccionado (con flechas o con el mouse)
        zonas = self.zonas_navegables()
        if 0 <= self.seleccion < len(zonas):
            pygame.draw.rect(pantalla, (255, 230, 50), zonas[self.seleccion][1], 4, border_radius=12)
        pos_mouse = pos_virtual(pygame.mouse.get_pos())
        for accion, rect in self.zonas_clic():
            if accion == "volver" and rect.collidepoint(pos_mouse):
                pygame.draw.rect(pantalla, (255, 230, 50), rect, 4, border_radius=12)


# ----------------- MODO ARENA: formato + escenario -----------------
COLUMNAS_ARENA = 6
CELDA_ARENA = (215, 150)
ORIGEN_ARENA = (60, 220)
RECT_FORMATOS = [pygame.Rect(60, 110, 300, 70), pygame.Rect(380, 110, 300, 70)]
FORMATOS = ["1v1", "3v3"]
TAM_VISTA_PREVIA = (480, 270)
POS_VISTA_PREVIA = (1380, 220)


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

    def mover(self, tecla):
        n = len(ESCENARIOS)
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
        elif tecla == pygame.K_RIGHT and self.escenario + 1 < n and col < COLUMNAS_ARENA - 1:
            self.escenario += 1
        elif tecla == pygame.K_DOWN:
            self.escenario = min(self.escenario + COLUMNAS_ARENA, n - 1)
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

    def pasar_mouse(self, pos_real):
        pos = pos_virtual(pos_real)
        for i, r in enumerate(RECT_FORMATOS):
            if r.collidepoint(pos):
                self.foco = "formato"
                self.formato = i
                return
        for i in range(len(ESCENARIOS)):
            if rect_celda_arena(i).collidepoint(pos):
                self.foco = "grid"
                self.escenario = i
                return

    def clic(self, pos_real):
        pos = pos_virtual(pos_real)
        for i, r in enumerate(RECT_FORMATOS):
            if r.collidepoint(pos):
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
        for i, r in enumerate(RECT_FORMATOS):
            activo = (i == self.formato)
            pygame.draw.rect(pantalla, VERDE_BOTON if activo else (45, 52, 75), r, border_radius=12)
            pygame.draw.rect(pantalla, BLANCO if activo else (90, 105, 140), r, 3, border_radius=12)
            etiqueta = "1 vs 1" if i == 0 else "3 vs 3"
            txt = FUENTE_GRANDE.render(etiqueta, True, BLANCO)
            pantalla.blit(txt, txt.get_rect(center=r.center))
            if self.foco == "formato" and activo:
                pygame.draw.rect(pantalla, (255, 230, 50), r, 5, border_radius=12)

        # Cuadrícula de escenarios
        for i, esc in enumerate(ESCENARIOS):
            r = rect_celda_arena(i)
            elegido = (i == self.escenario)
            pygame.draw.rect(pantalla, (55, 65, 100) if elegido else (35, 42, 60), r, border_radius=12)
            pygame.draw.rect(pantalla, (255, 230, 50) if (elegido and self.foco == "grid") else ((130, 150, 200) if elegido else (70, 85, 120)),
                             r, 4 if elegido else 2, border_radius=12)
            base = obtener_base("rival", i, 1.5)
            if base:
                pantalla.blit(base, base.get_rect(center=(r.centerx, r.y + 62)))
            txt = FUENTE_CHICA.render(esc["nombre"], True, BLANCO)
            pantalla.blit(txt, txt.get_rect(center=(r.centerx, r.bottom - 22)))

        # Vista previa del escenario elegido
        vx, vy = POS_VISTA_PREVIA
        pygame.draw.rect(pantalla, (40, 45, 65), (vx - 20, vy - 20, TAM_VISTA_PREVIA[0] + 40, 460), border_radius=15)
        pygame.draw.rect(pantalla, AZUL_DS, (vx - 20, vy - 20, TAM_VISTA_PREVIA[0] + 40, 460), 4, border_radius=15)
        pantalla.blit(obtener_vista_previa(self.escenario, TAM_VISTA_PREVIA), (vx, vy))
        pygame.draw.rect(pantalla, NEGRO, (vx, vy, TAM_VISTA_PREVIA[0], TAM_VISTA_PREVIA[1]), 3)
        nombre = FUENTE_GRANDE.render(ESCENARIOS[self.escenario]["nombre"], True, (255, 230, 50))
        pantalla.blit(nombre, nombre.get_rect(center=(vx + TAM_VISTA_PREVIA[0] // 2, vy + TAM_VISTA_PREVIA[1] + 50)))
        modo = FUENTE.render(f"Formato: {self.modo}", True, BLANCO)
        pantalla.blit(modo, modo.get_rect(center=(vx + TAM_VISTA_PREVIA[0] // 2, vy + TAM_VISTA_PREVIA[1] + 100)))

        ayuda = FUENTE.render("Flechas: mover  |  ENTER / clic: elegir escenario  |  ESC: volver", True, (180, 190, 210))
        pantalla.blit(ayuda, (60, 1020))


# ----------------- PANTALLAS -----------------
def dibujar_menu_principal(pantalla, botones, seleccion_idx):
    pantalla.fill((20, 35, 60))
    pygame.draw.rect(pantalla, AZUL_DS, (610, 240, 700, 600), border_radius=20)
    pygame.draw.rect(pantalla, BLANCO, (610, 240, 700, 600), 6, border_radius=20)

    titulo = FUENTE_GRANDE.render("POKÉMON AÑIL - DUELO", True, BLANCO)
    pantalla.blit(titulo, (720, 300))

    for idx, boton in enumerate(botones):
        boton.dibujar(pantalla, resaltado=(idx == seleccion_idx))

    sub_inf = FUENTE_CHICA.render("Usa Flechas ARRIBA/ABAJO y ENTER para seleccionar", True, (200, 220, 240))
    pantalla.blit(sub_inf, (710, 800))


def dibujar_seleccion(pantalla, equipo_seleccionado, seleccion_idx, scroll_offset_sel, modo_juego):
        pantalla.fill((25, 28, 40))

        meta_eq = 1 if modo_juego == "1v1" else 3
        txt_sel_info = FUENTE.render(f"SELECCIONA TUS POKÉMON ({len(equipo_seleccionado)}/{meta_eq}) - Modo {modo_juego}", True, BLANCO)
        pantalla.blit(txt_sel_info, (60, 40))

        pantalla.set_clip(pygame.Rect(60, 100, 700, 900))
        y_cursor = 120 - scroll_offset_sel
        for tipo_sec, pokes in SECCIONES_POKEMON.items():
            color_hdr = COLORES_TIPO.get(tipo_sec, BLANCO)
            txt_tipo = FUENTE.render(f"--- {tipo_sec} ---", True, color_hdr)
            pantalla.blit(txt_tipo, (60, y_cursor))
            y_cursor += 45

            for p_name in pokes:
                idx_global = LISTA_PLANA_POKES.index(p_name)
                is_sel = idx_global == seleccion_idx
                is_chosen = p_name in equipo_seleccionado

                color_txt = (255, 230, 50) if is_sel else ((100, 255, 100) if is_chosen else BLANCO)
                pref = "✔ " if is_chosen else ("> " if is_sel else "   ")

                txt_p = FUENTE.render(f"{pref}{p_name.capitalize()}", True, color_txt)
                pantalla.blit(txt_p, (60, y_cursor))
                y_cursor += 50
            y_cursor += 20
        pantalla.set_clip(None)

        poke_actual = LISTA_PLANA_POKES[seleccion_idx]
        pygame.draw.rect(pantalla, (40, 45, 65), (840, 100, 1000, 880), border_radius=15)
        pygame.draw.rect(pantalla, AZUL_DS, (840, 100, 1000, 880), 4, border_radius=15)

        img_f = obtener_sprite(poke_actual, "frente", (600, 600))
        if img_f:
            pantalla.blit(img_f, (1040, 200))

        t_name_prev = FUENTE_GRANDE.render(poke_actual.upper(), True, BLANCO)
        pantalla.blit(t_name_prev, (880, 130))


def dibujar_estadisticas(pantalla, equipo_seleccionado):
        pantalla.fill((30, 144, 255))
        pygame.draw.rect(pantalla, (240, 245, 255), (100, 80, 1720, 920), border_radius=15)
        pygame.draw.rect(pantalla, (20, 80, 160), (100, 80, 1720, 920), 5, border_radius=15)

        pygame.draw.rect(pantalla, (20, 80, 160), (100, 80, 1720, 70), border_top_left_radius=15, border_top_right_radius=15)
        txt_est_hdr = FUENTE.render("ESTADÍSTICAS DEL EQUIPO SELECCIONADO", True, BLANCO)
        pantalla.blit(txt_est_hdr, (140, 100))

        for i, p_elec in enumerate(equipo_seleccionado):
            data_p = CATALOGO_POKEMONS[p_elec]
            ox = 140 + (i * 560)
            oy = 180

            pygame.draw.rect(pantalla, BLANCO, (ox, oy, 500, 680), border_radius=12)
            pygame.draw.rect(pantalla, (100, 150, 200), (ox, oy, 500, 680), 3, border_radius=12)

            img_f = obtener_sprite(p_elec, "frente", (250, 250))
            if img_f:
                pantalla.blit(img_f, (ox + 125, oy + 20))

            t_p = FUENTE_GRANDE.render(p_elec.upper(), True, NEGRO)
            pantalla.blit(t_p, (ox + 30, oy + 290))

            t_tip = FUENTE.render(f"Tipo: {data_p['tipo']} | Nv. 70", True, AZUL_OSCURO)
            pantalla.blit(t_tip, (ox + 30, oy + 350))

            stats_texto = [
                f"HP: {data_p['hp']}", f"Ataque: {data_p['ataque']}", f"Defensa: {data_p['defensa']}",
                f"At. Esp: {data_p['atk_esp']}", f"Velocidad: {data_p['velocidad']}"
            ]
            for s_idx, st in enumerate(stats_texto):
                txt_st = FUENTE.render(st, True, NEGRO)
                pantalla.blit(txt_st, (ox + 30, oy + 420 + (s_idx * 45)))

        btn_rect = pygame.Rect(710, 900, 500, 70)
        pygame.draw.rect(pantalla, (40, 180, 90), btn_rect, border_radius=12)
        txt_comenzar = FUENTE.render("¡COMENZAR COMBATE!", True, BLANCO)
        txt_rect = txt_comenzar.get_rect(center=btn_rect.center)
        pantalla.blit(txt_comenzar, txt_rect)


def dibujar_biblioteca(pantalla, tipo_claves, scroll_offset_lib, lib_detalle, lib_sec_idx, lib_poke_idx):
        pantalla.fill((25, 28, 40))

        titulo_lib = FUENTE_GRANDE.render("BIBLIOTECA POKÉMON (Pokédex)", True, BLANCO)
        pantalla.blit(titulo_lib, (60, 30))

        if not lib_detalle:
            pantalla.set_clip(pygame.Rect(60, 100, 1800, 940))

            curr_y = 110 - scroll_offset_lib
            for r_idx, tipo_sec in enumerate(tipo_claves):
                col_t = COLORES_TIPO.get(tipo_sec, BLANCO)
                txt_tipo_hdr = FUENTE.render(f"--- {tipo_sec} ---", True, col_t)
                pantalla.blit(txt_tipo_hdr, (100, curr_y))
                curr_y += 50

                pokes = SECCIONES_POKEMON[tipo_sec]
                for c_idx, poke_name in enumerate(pokes):
                    columna = c_idx % 2
                    if columna == 0 and c_idx > 0:
                        curr_y += 190

                    cx = 100 + (columna * 880)
                    cy = curr_y

                    is_highlighted = (r_idx == lib_sec_idx and c_idx == lib_poke_idx)
                    bg_c = (55, 65, 100) if is_highlighted else (35, 42, 60)
                    b_c = (255, 230, 50) if is_highlighted else (70, 85, 120)
                    b_w = 4 if is_highlighted else 2

                    card_rect = pygame.Rect(cx, cy, 840, 170)
                    pygame.draw.rect(pantalla, bg_c, card_rect, border_radius=12)
                    pygame.draw.rect(pantalla, b_c, card_rect, b_w, border_radius=12)

                    img_c = obtener_sprite(poke_name, "frente", (140, 140))
                    if img_c:
                        pantalla.blit(img_c, (cx + 20, cy + 15))

                    txt_pn = FUENTE_GRANDE.render(poke_name.capitalize(), True, BLANCO)
                    pantalla.blit(txt_pn, (cx + 190, cy + 60))

                curr_y += 210

            pantalla.set_clip(None)

            inst_lib = FUENTE.render("Usa Flechas [ARRIBA/ABAJO/IZQ/DER] | [ENTER] Ver Detalles | [ESC] Volver", True, (180, 190, 210))
            pantalla.blit(inst_lib, (100, 1020))

        else:
            poke_sel = SECCIONES_POKEMON[tipo_claves[lib_sec_idx]][lib_poke_idx]
            data_lib = CATALOGO_POKEMONS[poke_sel]

            pygame.draw.rect(pantalla, (45, 50, 75), (260, 140, 1400, 800), border_radius=20)
            pygame.draw.rect(pantalla, AZUL_DS, (260, 140, 1400, 800), 5, border_radius=20)

            img_lib = obtener_sprite(poke_sel, "frente", (320, 320))
            if img_lib:
                pantalla.blit(img_lib, (320, 180))

            t_nom_lib = FUENTE_GRANDE.render(poke_sel.upper(), True, BLANCO)
            pantalla.blit(t_nom_lib, (700, 180))

            t_tip_lib = FUENTE.render(f"Tipo: {data_lib['tipo']} | HP: {data_lib['hp']}", True, (255, 220, 50))
            pantalla.blit(t_tip_lib, (700, 240))

            stats_det = f"Ataque: {data_lib['ataque']} | Defensa: {data_lib['defensa']} | Velocidad: {data_lib['velocidad']}"
            t_st_det = FUENTE.render(stats_det, True, (200, 220, 240))
            pantalla.blit(t_st_det, (700, 300))

            t_desc_tit = FUENTE.render("Descripción:", True, (200, 220, 250))
            pantalla.blit(t_desc_tit, (320, 540))

            lineas_desc = separar_texto_en_lineas(data_lib["desc"], FUENTE, 1200)
            for l_idx, linea in enumerate(lineas_desc):
                txt_l = FUENTE.render(linea, True, BLANCO)
                pantalla.blit(txt_l, (320, 600 + (l_idx * 40)))

            t_hab_tit = FUENTE.render("Habilidades:", True, (200, 220, 250))
            pantalla.blit(t_hab_tit, (320, 720))

            for h_idx, (hn, hp, ht) in enumerate(data_lib["habilidades"]):
                txt_h_lib = FUENTE.render(f"• {hn} (Potencia: {hp} | Tipo: {ht})", True, BLANCO)
                pantalla.blit(txt_h_lib, (350, 780 + (h_idx * 40)))

            nav_txt = FUENTE.render("Presiona [ESC] o [ENTER] para regresar", True, (180, 190, 210))
            pantalla.blit(nav_txt, (720, 870))