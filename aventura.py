# ----------------- MODO AVENTURA -----------------
# Escenas del modo aventura: elegir entrenador, explorar el mapa, tienda, mochila y gimnasio.
# Cada escena tiene manejar_evento(evento), actualizar(...) y dibujar(pantalla).
# Cuando una escena necesita que el juego cambie de pantalla, deja una "peticion":
#   ("elegido", nombre)                    -> se eligió entrenador
#   ("combate", rival, zona, tipo)         -> empezar un combate ("salvaje" o "gimnasio")
#   ("menu",)                              -> volver al menú principal

import random
import pygame

import mapa
from mapa import TILE
from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL, BLANCO, NEGRO, GRIS_CLARO, GRIS_OSCURO, AZUL_DS, AZUL_OSCURO,
    VERDE_BOTON, AMARILLO_ALERTA, ROJO_ALERTA, BORDE_CAJA, FUENTE, FUENTE_CHICA, FUENTE_GRANDE,
)
from entrenadores import ENTRENADORES, ORDEN_ENTRENADORES, crear_sprites, crear_busto
from pokemons import CATALOGO_POKEMONS
from ui import pos_virtual, obtener_sprite, separar_texto_en_lineas

AMARILLO_SEL = (255, 230, 50)

DINERO_INICIAL = 500
VELOCIDAD_CAMINAR = 4      # píxeles por frame (una casilla = 64 px)
VELOCIDAD_CORRER = 8

LIDER_GIMNASIO = "Líder Añil"
EQUIPO_LIDER = ["electabuzz", "magmar", "staryu"]
PREMIO_GIMNASIO = 1000
PREMIO_REVANCHA = 300

# (nombre visible, clave en la mochila, precio, descripción)
ARTICULOS_TIENDA = [
    ("Poké Ball", "pokeball", 200, "Sirve para capturar Pokémon (llega en la próxima versión)."),
    ("Poción", "pocion", 300, "Cura 50 HP a un Pokémon. Se puede usar en combate."),
    ("Curar equipo", "curar", 100, "Restaura toda la vida de tu equipo."),
    ("Salir", None, 0, "Volver al mapa."),
]

DIRECCIONES = {
    pygame.K_UP: ("arriba", 0, -1), pygame.K_w: ("arriba", 0, -1),
    pygame.K_DOWN: ("abajo", 0, 1), pygame.K_s: ("abajo", 0, 1),
    pygame.K_LEFT: ("izquierda", -1, 0), pygame.K_a: ("izquierda", -1, 0),
    pygame.K_RIGHT: ("derecha", 1, 0), pygame.K_d: ("derecha", 1, 0),
}


# ----------------- Utilidades de dibujo -----------------
def dibujar_panel(pantalla, rect, color=GRIS_CLARO, borde=BORDE_CAJA):
    pygame.draw.rect(pantalla, (20, 20, 30), rect.inflate(8, 8), border_radius=16)
    pygame.draw.rect(pantalla, color, rect, border_radius=12)
    pygame.draw.rect(pantalla, borde, rect, 3, border_radius=12)


def dibujar_barra_hp(pantalla, x, y, ancho, hp, hp_max):
    proporcion = hp / hp_max if hp_max else 0
    color = VERDE_BOTON
    if proporcion <= 0.5:
        color = AMARILLO_ALERTA
    if proporcion <= 0.2:
        color = ROJO_ALERTA
    pygame.draw.rect(pantalla, GRIS_OSCURO, (x, y, ancho, 14), border_radius=5)
    pygame.draw.rect(pantalla, color, (x, y, max(0, int(ancho * proporcion)), 14), border_radius=5)


# ----------------- Jugador -----------------
class Jugador:
    def __init__(self, entrenador, equipo):
        self.entrenador = entrenador
        self.equipo = list(equipo)
        self.hp = {p: CATALOGO_POKEMONS[p]["hp"] for p in self.equipo}
        self.dinero = DINERO_INICIAL
        self.mochila = {"pokeball": 0, "pocion": 1}
        self.medallas = 0

        self.x, self.y = mapa.INICIO
        self.direccion = "abajo"
        self.moviendo = False
        self.progreso = 0            # píxeles avanzados hacia la siguiente casilla
        self.destino = (self.x, self.y)
        self.pie = 1                 # alterna 1 y 2 para el paso izquierdo/derecho

    @property
    def nombre(self):
        return ENTRENADORES[self.entrenador]["nombre"]

    def curar_equipo(self):
        for p in self.equipo:
            self.hp[p] = CATALOGO_POKEMONS[p]["hp"]

    def equipo_debilitado(self):
        return all(self.hp[p] <= 0 for p in self.equipo)

    def volver_al_inicio(self):
        self.x, self.y = mapa.INICIO
        self.destino = (self.x, self.y)
        self.moviendo = False
        self.progreso = 0
        self.direccion = "abajo"

    def posicion_px(self):
        """Posición en píxeles del mundo (esquina superior izquierda de su casilla)."""
        px, py = self.x * TILE, self.y * TILE
        if self.moviendo:
            dx, dy = self.destino[0] - self.x, self.destino[1] - self.y
            px += dx * self.progreso
            py += dy * self.progreso
        return px, py

    def frame_actual(self):
        if self.moviendo and self.progreso < TILE // 2:
            return self.pie
        return 0

    def casilla_de_los_pies(self):
        if self.moviendo and self.progreso >= TILE // 2:
            return self.destino
        return (self.x, self.y)


# ----------------- Elegir entrenador -----------------
class EscenaElegirEntrenador:
    def __init__(self):
        self.indice = 0
        self.peticion = None
        self.tarjetas = [pygame.Rect(150 + i * 560, 200, 500, 680) for i in range(len(ORDEN_ENTRENADORES))]

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RIGHT, pygame.K_d):
                self.indice = (self.indice + 1) % len(ORDEN_ENTRENADORES)
            elif evento.key in (pygame.K_LEFT, pygame.K_a):
                self.indice = (self.indice - 1) % len(ORDEN_ENTRENADORES)
            elif evento.key == pygame.K_RETURN:
                self.peticion = ("elegido", ORDEN_ENTRENADORES[self.indice])
            elif evento.key == pygame.K_ESCAPE:
                self.peticion = ("menu",)
        elif evento.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.tarjetas):
                if r.collidepoint(pos_virtual(evento.pos)):
                    self.indice = i
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                for i, r in enumerate(self.tarjetas):
                    if r.collidepoint(pos_virtual(evento.pos)):
                        self.peticion = ("elegido", ORDEN_ENTRENADORES[i])
            elif evento.button == 3:
                self.peticion = ("menu",)

    def dibujar(self, pantalla):
        pantalla.fill((20, 35, 60))
        titulo = FUENTE_GRANDE.render("ELIGE A TU ENTRENADOR", True, BLANCO)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_VIRTUAL // 2, 110)))

        animacion = (pygame.time.get_ticks() // 250) % 4
        for i, (nombre, r) in enumerate(zip(ORDEN_ENTRENADORES, self.tarjetas)):
            elegido = i == self.indice
            fondo = (45, 70, 120) if elegido else (35, 45, 70)
            pygame.draw.rect(pantalla, fondo, r, border_radius=20)
            pygame.draw.rect(pantalla, AMARILLO_SEL if elegido else (80, 100, 140), r, 6 if elegido else 3, border_radius=20)

            # Retrato grande (busto.png ajustado a 448x448) en una ventana con degradado
            ventana = pygame.Rect(r.x + 26, r.y + 22, 448, 448)
            for k in range(0, 448, 8):
                tono = 70 + k // 8 if elegido else 50 + k // 10
                pygame.draw.rect(pantalla, (tono // 2, tono // 2 + 20, tono + 40), (ventana.x, ventana.y + k, 448, 8))
            pantalla.blit(crear_busto(nombre, 448), ventana)
            pygame.draw.rect(pantalla, AMARILLO_SEL if elegido else (80, 100, 140), ventana, 4)

            datos = ENTRENADORES[nombre]
            txt_nombre = FUENTE_GRANDE.render(datos["nombre"].upper(), True, AMARILLO_SEL if elegido else BLANCO)
            pantalla.blit(txt_nombre, txt_nombre.get_rect(center=(r.centerx, r.y + 500)))
            txt_frase = FUENTE_CHICA.render(datos["frase"], True, (200, 215, 240))
            pantalla.blit(txt_frase, txt_frase.get_rect(center=(r.centerx, r.y + 540)))

            # Cuerpo entero en las cuatro direcciones (el elegido camina en su sitio)
            sprites = crear_sprites(nombre, 96)
            frame = [0, 1, 0, 2][animacion] if elegido else 0
            for j, d in enumerate(("abajo", "izquierda", "arriba", "derecha")):
                pantalla.blit(sprites[d][frame], (r.centerx - 152 + j * 80, r.y + 570))

        ayuda = FUENTE_CHICA.render("Flechas IZQ/DER: cambiar  |  ENTER o clic: elegir  |  ESC: volver", True, (180, 195, 220))
        pantalla.blit(ayuda, ayuda.get_rect(center=(ANCHO_VIRTUAL // 2, 960)))


# ----------------- Mapa (exploración) -----------------
class EscenaMapa:
    def __init__(self, jugador):
        self.jugador = jugador
        self.peticion = None
        self.sub = None              # None, "tienda" o "mochila"
        self.dialogo = None          # (texto, accion_al_aceptar o None, se_puede_cancelar)
        self.transicion = 0          # frames del destello antes de un combate
        self.combate_pendiente = None
        self.tipo_combate = None
        self.sel_tienda = 0
        self.msg_tienda = "¡Bienvenido! ¿Qué deseas comprar?"
        self.sel_mochila = 0
        self.msg_mochila = ""
        self._hierba_delante = {}
        self.rects_tienda = [pygame.Rect(360, 260 + i * 110, 700, 90) for i in range(len(ARTICULOS_TIENDA))]
        self.rects_mochila = [pygame.Rect(900, 300 + i * 150, 760, 130) for i in range(len(jugador.equipo))]

        mapa.superficie_mapa()       # se dibuja el mundo una vez al empezar

    # ---------- Eventos ----------
    def manejar_evento(self, evento):
        if self.transicion > 0:
            return
        if self.dialogo is not None:
            self._evento_dialogo(evento)
        elif self.sub == "tienda":
            self._evento_tienda(evento)
        elif self.sub == "mochila":
            self._evento_mochila(evento)
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_m:
                self.abrir_mochila()
            elif evento.key == pygame.K_ESCAPE:
                self.dialogo = ("¿Volver al menú principal? Se perderá el progreso de la aventura.",
                                lambda: setattr(self, "peticion", ("menu",)), True)

    def _evento_dialogo(self, evento):
        texto, accion, cancelable = self.dialogo
        aceptar = (evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_SPACE)) or \
                  (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)
        cancelar = (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE) or \
                   (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 3)
        if aceptar:
            self.dialogo = None
            if accion:
                accion()
        elif cancelar:
            self.dialogo = None
            if not cancelable and accion:
                accion()

    def _evento_tienda(self, evento):
        n = len(ARTICULOS_TIENDA)
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_DOWN, pygame.K_s):
                self.sel_tienda = (self.sel_tienda + 1) % n
            elif evento.key in (pygame.K_UP, pygame.K_w):
                self.sel_tienda = (self.sel_tienda - 1) % n
            elif evento.key == pygame.K_RETURN:
                self.comprar(self.sel_tienda)
            elif evento.key == pygame.K_ESCAPE:
                self.sub = None
        elif evento.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects_tienda):
                if r.collidepoint(pos_virtual(evento.pos)):
                    self.sel_tienda = i
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                for i, r in enumerate(self.rects_tienda):
                    if r.collidepoint(pos_virtual(evento.pos)):
                        self.sel_tienda = i
                        self.comprar(i)
            elif evento.button == 3:
                self.sub = None

    def _evento_mochila(self, evento):
        n = len(self.jugador.equipo)
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_DOWN, pygame.K_s):
                self.sel_mochila = (self.sel_mochila + 1) % n
            elif evento.key in (pygame.K_UP, pygame.K_w):
                self.sel_mochila = (self.sel_mochila - 1) % n
            elif evento.key == pygame.K_RETURN:
                self.usar_pocion(self.sel_mochila)
            elif evento.key in (pygame.K_ESCAPE, pygame.K_m):
                self.sub = None
        elif evento.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects_mochila):
                if r.collidepoint(pos_virtual(evento.pos)):
                    self.sel_mochila = i
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                for i, r in enumerate(self.rects_mochila):
                    if r.collidepoint(pos_virtual(evento.pos)):
                        self.sel_mochila = i
                        self.usar_pocion(i)
            elif evento.button == 3:
                self.sub = None

    # ---------- Acciones ----------
    def abrir_mochila(self):
        self.sub = "mochila"
        self.sel_mochila = 0
        self.msg_mochila = "Elige un Pokémon para darle una Poción."

    def comprar(self, indice):
        nombre, clave, precio, _ = ARTICULOS_TIENDA[indice]
        j = self.jugador
        if clave is None:
            self.sub = None
            return
        if clave == "curar" and all(j.hp[p] == CATALOGO_POKEMONS[p]["hp"] for p in j.equipo):
            self.msg_tienda = "Tu equipo ya está en plena forma."
            return
        if j.dinero < precio:
            self.msg_tienda = f"No te alcanza el dinero para {nombre} (cuesta ${precio})."
            return
        j.dinero -= precio
        if clave == "curar":
            j.curar_equipo()
            self.msg_tienda = "¡Tu equipo está como nuevo!"
        else:
            j.mochila[clave] += 1
            self.msg_tienda = f"¡Compraste 1 {nombre}! Ahora tienes {j.mochila[clave]}."

    def usar_pocion(self, idx):
        j = self.jugador
        nombre = j.equipo[idx]
        hp_max = CATALOGO_POKEMONS[nombre]["hp"]
        if j.mochila["pocion"] <= 0:
            self.msg_mochila = "No tienes Pociones. Cómpralas en la tienda."
        elif j.hp[nombre] <= 0:
            self.msg_mochila = f"{nombre.capitalize()} está debilitado. Cúralo en la tienda."
        elif j.hp[nombre] >= hp_max:
            self.msg_mochila = f"{nombre.capitalize()} ya tiene la vida llena."
        else:
            curado = min(50, hp_max - j.hp[nombre])
            j.hp[nombre] += curado
            j.mochila["pocion"] -= 1
            self.msg_mochila = f"{nombre.capitalize()} recuperó {curado} HP."

    def entrar_edificio(self, edificio):
        if edificio["tipo"] == "tienda":
            self.sub = "tienda"
            self.sel_tienda = 0
            self.msg_tienda = "¡Bienvenido! ¿Qué deseas comprar?"
        else:
            if self.jugador.equipo_debilitado():
                self.dialogo = (f"{LIDER_GIMNASIO}: Tu equipo está agotado. Cúralo en la tienda y vuelve.", None, True)
                return
            if self.jugador.medallas:
                texto = f"{LIDER_GIMNASIO}: ¿Vienes por la revancha? ¡Adelante! (ENTER: pelear, ESC: salir)"
            else:
                texto = f"{LIDER_GIMNASIO}: ¡Bienvenido al Gimnasio! ¿Te atreves a retarme? (ENTER: pelear, ESC: salir)"
            self.dialogo = (texto, lambda: self._iniciar_combate(list(EQUIPO_LIDER), "gimnasio", "gimnasio"), True)

    def _iniciar_combate(self, rival, zona, tipo):
        self.combate_pendiente = (rival, zona, tipo)
        self.transicion = 45

    def terminar_combate(self, combate):
        """Aplica el resultado de un combate del modo aventura."""
        j = self.jugador
        for p in j.equipo:
            j.hp[p] = combate.hp_jugador[p]
        if combate.resultado == "victoria":
            if self.tipo_combate == "gimnasio":
                premio = PREMIO_REVANCHA if j.medallas else PREMIO_GIMNASIO
                if not j.medallas:
                    j.medallas = 1
                    texto = f"¡Venciste a {LIDER_GIMNASIO}! Ganaste la Medalla Añil y ${premio}."
                else:
                    texto = f"¡Venciste otra vez a {LIDER_GIMNASIO}! Ganaste ${premio}."
            else:
                premio = random.randint(100, 200)
                texto = f"¡Ganaste el combate! Recibiste ${premio}."
            j.dinero += premio
        else:
            perdida = j.dinero // 2
            j.dinero -= perdida
            j.curar_equipo()
            j.volver_al_inicio()
            texto = f"Tu equipo cayó... Volviste corriendo al pueblo y perdiste ${perdida}."
        self.dialogo = (texto, None, True)
        self.tipo_combate = None

    # ---------- Lógica por frame ----------
    def actualizar(self, teclas):
        if self.transicion > 0:
            self.transicion -= 1
            if self.transicion == 0 and self.combate_pendiente:
                rival, zona, tipo = self.combate_pendiente
                self.combate_pendiente = None
                self.tipo_combate = tipo
                self.peticion = ("combate", rival, zona, tipo)
            return
        if self.dialogo is not None or self.sub is not None:
            return

        j = self.jugador
        if j.moviendo:
            velocidad = VELOCIDAD_CORRER if teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT] else VELOCIDAD_CAMINAR
            j.progreso += velocidad
            if j.progreso >= TILE:
                j.x, j.y = j.destino
                j.moviendo = False
                j.progreso = 0
                j.pie = 2 if j.pie == 1 else 1
                self._al_pisar_casilla()
            return

        for tecla, (direccion, dx, dy) in DIRECCIONES.items():
            if teclas[tecla]:
                j.direccion = direccion
                destino = (j.x + dx, j.y + dy)
                edificio = mapa.puerta_en(*destino)
                if edificio:
                    self.entrar_edificio(edificio)
                elif not mapa.es_solido(*destino):
                    j.destino = destino
                    j.moviendo = True
                break

    def _al_pisar_casilla(self):
        j = self.jugador
        if mapa.letra_en(j.x, j.y) != "H":
            return
        if random.random() >= mapa.PROBABILIDAD_ENCUENTRO:
            return
        if j.equipo_debilitado():
            self.dialogo = ("¡Algo se mueve en la hierba! Pero tu equipo está agotado... cúralo en la tienda.", None, True)
            return
        zona = mapa.zona_en(j.x, j.y)
        salvaje = random.choice(mapa.ENCUENTROS_POR_ZONA[zona])
        self._iniciar_combate([salvaje], zona, "salvaje")

    # ---------- Dibujo ----------
    def _camara(self):
        px, py = self.jugador.posicion_px()
        ancho_mundo, alto_mundo = mapa.COLUMNAS * TILE, mapa.FILAS * TILE
        cx = min(max(0, px + TILE // 2 - ANCHO_VIRTUAL // 2), ancho_mundo - ANCHO_VIRTUAL)
        cy = min(max(0, py + TILE // 2 - ALTO_VIRTUAL // 2), alto_mundo - ALTO_VIRTUAL)
        return int(cx), int(cy)

    def _hierba(self, zona):
        if zona not in self._hierba_delante:
            self._hierba_delante[zona] = mapa.crear_hierba_delante(zona)
        return self._hierba_delante[zona]

    def dibujar(self, pantalla):
        j = self.jugador
        cx, cy = self._camara()
        pantalla.blit(mapa.superficie_mapa(), (0, 0), pygame.Rect(cx, cy, ANCHO_VIRTUAL, ALTO_VIRTUAL))

        # Jugador (96 px de alto, con los pies en la parte baja de su casilla)
        px, py = j.posicion_px()
        sprite = crear_sprites(j.entrenador, 96)[j.direccion][j.frame_actual()]
        sx, sy = px - cx - (sprite.get_width() - TILE) // 2, py - cy - (sprite.get_height() - TILE)
        sombra = pygame.Surface((56, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 70), sombra.get_rect())
        pantalla.blit(sombra, (px - cx + 4, py - cy + TILE - 14))
        pantalla.blit(sprite, (sx, sy))

        # Si está en la hierba alta, la hierba tapa sus pies
        hx, hy = j.casilla_de_los_pies()
        if mapa.letra_en(hx, hy) == "H":
            pantalla.blit(self._hierba(mapa.zona_en(hx, hy)), (hx * TILE - cx, hy * TILE - cy))

        self._dibujar_hud(pantalla)

        if self.sub == "tienda":
            self._dibujar_tienda(pantalla)
        elif self.sub == "mochila":
            self._dibujar_mochila(pantalla)

        if self.dialogo is not None:
            self._dibujar_dialogo(pantalla, self.dialogo[0])

        if self.transicion > 0:
            # Destello blanco/negro antes del combate
            velo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
            velo.fill(BLANCO if (self.transicion // 6) % 2 == 0 else NEGRO)
            velo.set_alpha(150 if self.transicion > 12 else 255)
            pantalla.blit(velo, (0, 0))

    def _dibujar_hud(self, pantalla):
        j = self.jugador
        zona = mapa.zona_en(j.x, j.y)

        caja = pygame.Rect(30, 30, 500, 150)
        dibujar_panel(pantalla, caja)
        marco = pygame.Rect(caja.x + 11, caja.y + 11, 128, 128)
        pygame.draw.rect(pantalla, (150, 180, 220), marco, border_radius=8)
        pantalla.blit(crear_busto(j.entrenador, 128), marco)
        pygame.draw.rect(pantalla, BORDE_CAJA, marco, 3, border_radius=8)
        x_txt = caja.x + 158
        pantalla.blit(FUENTE.render(j.nombre, True, NEGRO), (x_txt, caja.y + 18))
        pantalla.blit(FUENTE_CHICA.render(mapa.NOMBRES_ZONA[zona], True, AZUL_OSCURO), (x_txt, caja.y + 58))
        pantalla.blit(FUENTE_CHICA.render(f"Dinero: ${j.dinero}", True, NEGRO), (x_txt, caja.y + 88))
        medalla = "Medalla Añil" if j.medallas else "Sin medallas"
        pantalla.blit(FUENTE_CHICA.render(medalla, True, (170, 120, 20) if j.medallas else GRIS_OSCURO),
                      (x_txt, caja.y + 116))

        equipo = pygame.Rect(ANCHO_VIRTUAL - 430, 30, 400, 40 + 70 * len(j.equipo))
        dibujar_panel(pantalla, equipo)
        for i, p in enumerate(j.equipo):
            y = equipo.y + 20 + i * 70
            icono = obtener_sprite(p, "frente", (64, 64))
            if icono:
                pantalla.blit(icono, (equipo.x + 10, y - 6))
            color = NEGRO if j.hp[p] > 0 else GRIS_OSCURO
            pantalla.blit(FUENTE_CHICA.render(p.capitalize(), True, color), (equipo.x + 84, y))
            hp_max = CATALOGO_POKEMONS[p]["hp"]
            dibujar_barra_hp(pantalla, equipo.x + 84, y + 32, 200, j.hp[p], hp_max)
            pantalla.blit(FUENTE_CHICA.render(f"{j.hp[p]}", True, color), (equipo.x + 300, y + 22))

        if self.sub is None and self.dialogo is None:
            ayuda = FUENTE_CHICA.render("Flechas/WASD: caminar  |  Shift: correr  |  M: mochila  |  ESC: menú", True, BLANCO)
            fondo = ayuda.get_rect(center=(ANCHO_VIRTUAL // 2, ALTO_VIRTUAL - 40)).inflate(30, 14)
            velo = pygame.Surface(fondo.size, pygame.SRCALPHA)
            velo.fill((0, 0, 0, 140))
            pantalla.blit(velo, fondo)
            pantalla.blit(ayuda, ayuda.get_rect(center=fondo.center))

    def _dibujar_dialogo(self, pantalla, texto):
        caja = pygame.Rect(100, 820, 1720, 200)
        dibujar_panel(pantalla, caja)
        for i, linea in enumerate(separar_texto_en_lineas(texto, FUENTE, 1640)):
            pantalla.blit(FUENTE.render(linea, True, NEGRO), (caja.x + 40, caja.y + 36 + i * 42))
        flecha = FUENTE_CHICA.render("ENTER ▼", True, GRIS_OSCURO)
        pantalla.blit(flecha, (caja.right - 140, caja.bottom - 44))

    def _dibujar_tienda(self, pantalla):
        j = self.jugador
        velo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL), pygame.SRCALPHA)
        velo.fill((0, 0, 0, 150))
        pantalla.blit(velo, (0, 0))

        panel = pygame.Rect(300, 120, 1320, 860)
        dibujar_panel(pantalla, panel, (235, 242, 255), (30, 75, 160))
        pygame.draw.rect(pantalla, (50, 110, 210), (panel.x, panel.y, panel.w, 90),
                         border_top_left_radius=12, border_top_right_radius=12)
        pantalla.blit(FUENTE_GRANDE.render("TIENDA", True, BLANCO), (panel.x + 40, panel.y + 22))
        txt_dinero = FUENTE.render(f"Tu dinero: ${j.dinero}", True, BLANCO)
        pantalla.blit(txt_dinero, txt_dinero.get_rect(topright=(panel.right - 40, panel.y + 28)))

        for i, ((nombre, clave, precio, _), r) in enumerate(zip(ARTICULOS_TIENDA, self.rects_tienda)):
            sel = i == self.sel_tienda
            pygame.draw.rect(pantalla, (255, 250, 220) if sel else BLANCO, r, border_radius=12)
            pygame.draw.rect(pantalla, AMARILLO_SEL if sel else (150, 170, 210), r, 4 if sel else 2, border_radius=12)
            self._icono_articulo(pantalla, clave, (r.x + 50, r.centery))
            pantalla.blit(FUENTE.render(nombre, True, NEGRO), (r.x + 100, r.y + 26))
            if clave is not None:
                txt_precio = FUENTE.render(f"${precio}", True, AZUL_OSCURO)
                pantalla.blit(txt_precio, txt_precio.get_rect(midright=(r.right - 30, r.centery)))
            if clave in ("pokeball", "pocion"):
                pantalla.blit(FUENTE_CHICA.render(f"Tienes: {j.mochila[clave]}", True, GRIS_OSCURO), (r.x + 380, r.y + 30))

        # Descripción del artículo y mensaje del vendedor
        desc = ARTICULOS_TIENDA[self.sel_tienda][3]
        info = pygame.Rect(1100, 260, 480, 420)
        pygame.draw.rect(pantalla, BLANCO, info, border_radius=12)
        pygame.draw.rect(pantalla, (150, 170, 210), info, 2, border_radius=12)
        for k, linea in enumerate(separar_texto_en_lineas(desc, FUENTE_CHICA, 430)):
            pantalla.blit(FUENTE_CHICA.render(linea, True, NEGRO), (info.x + 24, info.y + 24 + k * 32))
        for k, linea in enumerate(separar_texto_en_lineas(self.msg_tienda, FUENTE, 1200)):
            pantalla.blit(FUENTE.render(linea, True, (30, 75, 160)), (panel.x + 60, panel.bottom - 120 + k * 40))
        ayuda = FUENTE_CHICA.render("Flechas: elegir  |  ENTER: comprar  |  ESC: salir", True, GRIS_OSCURO)
        pantalla.blit(ayuda, (panel.x + 60, panel.bottom - 40))

    def _icono_articulo(self, pantalla, clave, centro):
        x, y = centro
        if clave == "pokeball":
            pygame.draw.circle(pantalla, BLANCO, centro, 24)
            pygame.draw.rect(pantalla, (210, 40, 40), (x - 24, y - 24, 48, 24), border_top_left_radius=24, border_top_right_radius=24)
            pygame.draw.circle(pantalla, NEGRO, centro, 24, 3)
            pygame.draw.line(pantalla, NEGRO, (x - 24, y), (x + 24, y), 3)
            pygame.draw.circle(pantalla, BLANCO, centro, 7)
            pygame.draw.circle(pantalla, NEGRO, centro, 7, 3)
        elif clave == "pocion":
            pygame.draw.rect(pantalla, (150, 90, 200), (x - 14, y - 10, 28, 34), border_radius=8)
            pygame.draw.rect(pantalla, (200, 200, 210), (x - 8, y - 24, 16, 16))
            pygame.draw.rect(pantalla, NEGRO, (x - 14, y - 10, 28, 34), 3, border_radius=8)
            pygame.draw.rect(pantalla, NEGRO, (x - 8, y - 24, 16, 16), 2)
        elif clave == "curar":
            pygame.draw.rect(pantalla, (220, 50, 60), (x - 8, y - 22, 16, 44))
            pygame.draw.rect(pantalla, (220, 50, 60), (x - 22, y - 8, 44, 16))
        else:
            pygame.draw.polygon(pantalla, GRIS_OSCURO, [(x + 14, y - 16), (x - 14, y), (x + 14, y + 16)])

    def _dibujar_mochila(self, pantalla):
        j = self.jugador
        velo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL), pygame.SRCALPHA)
        velo.fill((0, 0, 0, 150))
        pantalla.blit(velo, (0, 0))

        panel = pygame.Rect(200, 140, 1520, 820)
        dibujar_panel(pantalla, panel, (255, 244, 225), (170, 100, 30))
        pygame.draw.rect(pantalla, (225, 150, 40), (panel.x, panel.y, panel.w, 90),
                         border_top_left_radius=12, border_top_right_radius=12)
        pantalla.blit(FUENTE_GRANDE.render("MOCHILA", True, BLANCO), (panel.x + 40, panel.y + 22))

        # Objetos
        objetos = [("pocion", f"Pociones: {j.mochila['pocion']}"),
                   ("pokeball", f"Poké Balls: {j.mochila['pokeball']}")]
        for k, (clave, texto) in enumerate(objetos):
            y = 330 + k * 120
            self._icono_articulo(pantalla, clave, (300, y))
            pantalla.blit(FUENTE.render(texto, True, NEGRO), (350, y - 18))
        pantalla.blit(FUENTE_CHICA.render("Las Poké Balls se usarán para", True, GRIS_OSCURO), (260, 560))
        pantalla.blit(FUENTE_CHICA.render("capturar (próxima versión).", True, GRIS_OSCURO), (260, 592))
        pantalla.blit(FUENTE_CHICA.render(f"Dinero: ${j.dinero}", True, NEGRO), (260, 660))

        # Equipo
        for i, (p, r) in enumerate(zip(j.equipo, self.rects_mochila)):
            sel = i == self.sel_mochila
            pygame.draw.rect(pantalla, (255, 250, 220) if sel else BLANCO, r, border_radius=12)
            pygame.draw.rect(pantalla, AMARILLO_SEL if sel else (210, 170, 120), r, 4 if sel else 2, border_radius=12)
            icono = obtener_sprite(p, "frente", (110, 110))
            if icono:
                pantalla.blit(icono, (r.x + 14, r.y + 10))
            hp_max = CATALOGO_POKEMONS[p]["hp"]
            pantalla.blit(FUENTE.render(p.capitalize(), True, NEGRO), (r.x + 150, r.y + 24))
            dibujar_barra_hp(pantalla, r.x + 150, r.y + 76, 380, j.hp[p], hp_max)
            pantalla.blit(FUENTE_CHICA.render(f"{j.hp[p]} / {hp_max}", True, NEGRO), (r.x + 560, r.y + 68))

        pantalla.blit(FUENTE.render(self.msg_mochila, True, (150, 80, 10)), (panel.x + 60, panel.bottom - 110))
        ayuda = FUENTE_CHICA.render("Flechas: elegir Pokémon  |  ENTER: usar Poción  |  M o ESC: cerrar", True, GRIS_OSCURO)
        pantalla.blit(ayuda, (panel.x + 60, panel.bottom - 50))
