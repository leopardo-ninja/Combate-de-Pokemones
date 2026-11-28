# ----------------- ESCENA DE COMBATE: dibujo, animaciones y botones -----------------
import pygame

import sonido
import efectos
import entrada_pokemon
from config import (
    BLANCO, NEGRO, GRIS_CLARO, GRIS_OSCURO, AZUL_BOTON, ROJO_BOTON, VERDE_BOTON, FUENTE, FUENTE_CHICA, FUENTE_GRANDE, FUENTE_HABILIDAD, RUTA_FUENTE
)
from pokemons import CATALOGO_POKEMONS
from motor_combate import ENERGIA_MAX, COSTO_FUERTE
from .utilidades import pos_virtual, dibujar_resalte, separar_texto_en_lineas
from .recursos import (
    obtener_pokemon, obtener_caja, obtener_fondo_escenario, dibujar_bases, obtener_barra_mensaje,
    obtener_caja_ataque, obtener_caja_equipo, obtener_bolas_equipo, ESCALA_CAJA, ESCALA_ATAQUE, ESCALA_EQUIPO,
    TAM_ATAQUE, TAM_EQUIPO, BARRA_MSJ_RECT,
)

# Paleta de colores por tipo de Pokémon (se usa como respaldo si falta alguna imagen del combate)
TEMAS_TIPO_COMBATE = {
    "Fuego": {"fondo_top": (70, 25, 15), "fondo_bot": (35, 12, 8), "suelo_rival": (110, 45, 25), "suelo_jug": (130, 55, 30), "principal": (235, 100, 40)},
    "Agua": {"fondo_top": (15, 40, 75), "fondo_bot": (8, 20, 40), "suelo_rival": (30, 80, 130), "suelo_jug": (40, 100, 160), "principal": (40, 130, 235)},
    "Planta": {"fondo_top": (25, 60, 30), "fondo_bot": (12, 30, 15), "suelo_rival": (50, 110, 60), "suelo_jug": (65, 135, 75), "principal": (50, 180, 70)},
    "Eléctrico": {"fondo_top": (75, 70, 20), "fondo_bot": (35, 32, 8), "suelo_rival": (120, 110, 30), "suelo_jug": (145, 135, 35), "principal": (240, 205, 30)},
    "Tierra": {"fondo_top": (65, 45, 25), "fondo_bot": (30, 20, 10), "suelo_rival": (100, 75, 45), "suelo_jug": (125, 95, 55), "principal": (170, 120, 60)},
}

# Posiciones del combate (coordenadas virtuales 1920x1080)
POS_POKEMON_IA = (1030, 160)        # Posicion Pokemon IA
POS_POKEMON_JUG = (300, 350)        # Posicion Pokemon Jugador

# ===== TEMA: Diccionarios (Clase 11) + Tuplas (Clase 11) =====
# Diccionarios bando -> tupla. Se consultan así: PIES_POKEMON["ia"]
# ===== AJUSTE DEL TAMAÑO DE LOS POKÉMON (lo único que normalmente tendrás que tocar) =====
# Tamaño de cada bando en porcentaje: 100 = normal, 90 = 10 % más pequeño, 110 = 10 % más grande
TAMANO_POKEMON_PORCENTAJE = {"ia": 81, "jugador": 100}
# Ajuste extra para Pokémon concretos (se multiplica por el de su bando). Se escribe el nombre en minúsculas y su porcentaje
# Ejemplo: AJUSTE_POKEMON = {"moltres": 90, "caterpie": 120}
AJUSTE_POKEMON = {}

# Ajuste automático del tamaño y la posición de los sprites (así los Pokémon grandes, como los legendarios, no se salen del círculo)
TAM_LIENZO_POKEMON = {"ia": (500, 500), "jugador": (680, 680)}        # Tamaño de la caja donde se dibuja cada Pokémon (no cambia cuánto se ve)
TAM_MAX_POKEMON = {"ia": (336, 272), "jugador": (416, 376)}     # Tope de seguridad (ancho, alto): solo reduce los que se pasan, casi nunca hay que tocarlo
PIES_POKEMON = {"ia": (1310, 510), "jugador": (640, 840)}           # Punto del círculo (x, y) donde apoya los pies cada Pokémon
pokemons_ajustados = {}                                              # Memoria de sprites ya ajustados: (nombre, bando) -> imagen


# ===== TEMA: Funciones (Clase 7) + Diccionarios (Clase 11) + Condicionales (Clase 4) =====
# Entrada: nombre del Pokémon, bando ("ia" o "jugador") y su imagen. Salida (post-condición): una imagen del mismo tamaño de caja con el Pokémon reducido si era muy grande y con los pies sobre el círculo
# Recorta el espacio transparente, reduce el sprite si pasa del máximo (nunca lo agranda) y lo apoya en PIES_POKEMON. El resultado se guarda para no repetir el cálculo en cada frame
def ajustar_tamano_pokemon(nombre, bando, imagen):
    clave = (nombre, bando)
    if clave in pokemons_ajustados:
        return pokemons_ajustados[clave]

    # get_bounding_rect() devuelve el rectángulo que ocupa la parte no transparente del sprite
    zona_visible = imagen.get_bounding_rect()
    if zona_visible.width == 0 or zona_visible.height == 0:
        pokemons_ajustados[clave] = imagen
        return imagen
    recorte = imagen.subsurface(zona_visible).copy()

    # min() elige la reducción más fuerte necesaria del tope de seguridad; 1.0 significa que ese tope no agranda
    max_ancho, max_alto = TAM_MAX_POKEMON[bando]
    escala = min(1.0, max_ancho / zona_visible.width, max_alto / zona_visible.height)
    # Después se aplica el porcentaje del bando y el de ese Pokémon en concreto (100 = sin cambio)
    porcentaje = TAMANO_POKEMON_PORCENTAJE[bando] * AJUSTE_POKEMON.get(nombre, 100) / 100
    escala = escala * porcentaje / 100
    if escala != 1.0:
        nuevo_tam = (max(1, int(zona_visible.width * escala)), max(1, int(zona_visible.height * escala)))
        recorte = pygame.transform.scale(recorte, nuevo_tam)    # scale (sin suavizar) conserva el estilo pixelado

    # Se pone el recorte sobre un lienzo transparente del tamaño de la caja, con la base centrada en el punto de los pies
    lienzo = pygame.Surface(TAM_LIENZO_POKEMON[bando], pygame.SRCALPHA)
    pos_caja = POS_POKEMON_IA if bando == "ia" else POS_POKEMON_JUG
    pies_x = PIES_POKEMON[bando][0] - pos_caja[0]
    pies_y = PIES_POKEMON[bando][1] - pos_caja[1]
    lienzo.blit(recorte, recorte.get_rect(midbottom=(pies_x, pies_y)))
    pokemons_ajustados[clave] = lienzo
    return lienzo


# Opacidad del Pokémon en la fase transparente del parpadeo al recibir daño (0 = invisible, 255 = normal)
ALFA_PARPADEO = 0

# Las 3 bolas del equipo (vivo / caído / vacío), sin fondo. Las del jugador van bajo su caja de vida, pegadas a la derecha;
# las del rival, bajo la suya, pegadas a la izquierda. Se da una esquina de la fila de bolas (x, y)
POS_BANDEJA = {"jugador": (1555, 790), "ia": (629, 210)}
ANCLA_BANDEJA = {"jugador": "topright", "ia": "topleft"}
SEP_BOLAS = 6                                   # espacio entre bolas

# Cajas de vida (Jugador y Rival)
BARRA_CAJA = {"rival": (93, 40, 211, 48), "jugador": (117, 39, 233, 48)}        # Barra de vida
POS_CAJA = {"rival": (600, 100), "jugador": (1200, 650)}                        # Posicion caja de vida

# Barra de energía (solo la caja del jugador), justo debajo de la de vida. Píxeles originales de la imagen: x0, y0, x1, y1
BARRA_ENERGIA = (115, 53, 237, 58)
COLOR_ENERGIA = ((60, 150, 235), (150, 205, 255))            # Cargando: (color, brillo)
COLOR_ENERGIA_LISTA = ((250, 190, 30), (255, 240, 150))      # Llena (la habilidad fuerte ya se puede usar)

# Botones pantalla combate (x, y, ancho, alto)
RECT_LUCHAR = pygame.Rect(900, 880, 260, 60)                # LUCHAR
RECT_CAMBIAR = pygame.Rect(1200, 880, 260, 60)              # POKEMON
RECT_VOLVER = pygame.Rect(150, 925, 220, 55)                # VOLVER
RECT_MENU_FIN = pygame.Rect(1200, 925, 260, 60)             # MENU
OFFSET_NOMBRE = {"rival": (12, 11), "jugador": (36, 11)}    # Diferencia de posicion entre los nombres de los pokemons

# Cajas de los ataques
ORIGEN_ATAQUES = (545, 905)          # Esquina superior izquierda de la fila de 4 cajas
SEP_ATAQUES = (20, 10)               # Separación horizontal entre cajas (el vertical ya no se usa)

# Cajas del equipo (cambiar de pokemon)
ORIGEN_EQUIPO = (900, 895)             # Esquina superior izquierda de la primera caja (x, y)
SEP_EQUIPO = 15                        # Espacio entre cajas
BARRA_EQUIPO = (24, 33, 48, 3)         # Barra de vida dentro de la caja: x, y, ancho, alto (píxeles originales)
FUENTE_EQUIPO = pygame.font.Font(RUTA_FUENTE, 17)   # Vida en número


def rect_habilidad(idx):
    # Las 4 habilidades en una sola fila
    return pygame.Rect(ORIGEN_ATAQUES[0] + idx * (TAM_ATAQUE[0] + SEP_ATAQUES[0]),
                       ORIGEN_ATAQUES[1],
                       TAM_ATAQUE[0], TAM_ATAQUE[1])


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
        self.energia_visible = {}   # quien -> (nombre, energía mostrada) para animar el llenado de la barra
        # Entrada de los Pokémon con la Poké Ball: qué Pokémon había en el frame anterior y la animación en curso de cada lado
        self.nombres_vistos = {"ia": None, "jugador": None}
        self.entradas = {"ia": None, "jugador": None}
        # Frames que le quedan al parpadeo blanco de cada lado cuando recibe daño
        self.flash = {"ia": 0, "jugador": 0}
        self.gestor = efectos.GestorEfectos()   # animaciones de las habilidades
        # Texto de daño que sube sobre cada Pokémon: (texto, frames restantes)
        self.texto_flotante = {"ia": ("", 0), "jugador": ("", 0)}
        self.seleccion = 0          # botón resaltado (índice en zonas_navegables)
        self._contexto = None       # (turno, sub_menu) para reiniciar la selección al cambiar de menú

    # True mientras se reproduce la animación de una habilidad.
    def ocupado(self):
        return self.gestor.ocupado() or any(entrada is not None for entrada in self.entradas.values())

    # Anima la habilidad; 'al_impactar' (aplicar el daño en el motor) se llama en el golpe.
    def lanzar_habilidad(self, quien, habilidad, al_impactar, mensaje=None):
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

    # Dibuja un Pokémon; si acaba de recibir daño parpadea, alternando cada 4 frames entre verse normal y volverse transparente
    def _dibujar_pokemon(self, pantalla, imagen_pokemon, pos, quien):
        if self.flash[quien] > 0:
            self.flash[quien] -= 1
            if (self.flash[quien] // 4) % 2 == 0:
                # Fase transparente del parpadeo: ALFA_PARPADEO = 0 lo oculta del todo; con un valor mayor (ej. 80) queda semitransparente
                if ALFA_PARPADEO > 0:
                    transparente = imagen_pokemon.copy()
                    transparente.set_alpha(ALFA_PARPADEO)
                    pantalla.blit(transparente, pos)
                return
        pantalla.blit(imagen_pokemon, pos)

    # Estado de la bola número i del equipo de un bando: "vivo", "caido" (sin vida) o "vacio" (el equipo tiene menos de 3)
    def _estado_bola(self, bando, i):
        c = self.combate
        equipo = c.equipo_jugador if bando == "jugador" else c.equipo_ia
        if i >= len(equipo):
            return "vacio"
        nombre = equipo[i]
        # La vida del Pokémon que combate está en hp_actual_*; la de los demás, en el diccionario del equipo
        if bando == "jugador":
            hp = c.hp_actual_jugador if nombre == c.nombre_jugador else c.hp_jugador[nombre]
        else:
            hp = c.hp_actual_ia if nombre == c.nombre_ia else c.hp_ia[nombre]
        return "vivo" if hp > 0 else "caido"

    # Dibuja las 3 bolas de un bando ("jugador" o "ia"), una al lado de otra y sin fondo
    def _dibujar_bandeja_equipo(self, pantalla, bando):
        bolas = obtener_bolas_equipo("jugador" if bando == "jugador" else "rival")
        if bolas is None:
            return
        lado = bolas["vivo"].get_width()
        # Rectángulo que ocupan las 3 bolas, colocado según la esquina elegida
        rect = pygame.Rect(0, 0, 3 * lado + 2 * SEP_BOLAS, lado)
        setattr(rect, ANCLA_BANDEJA[bando], POS_BANDEJA[bando])
        for i in range(3):
            pantalla.blit(bolas[self._estado_bola(bando, i)], (rect.x + i * (lado + SEP_BOLAS), rect.y))

    # Si el Pokémon activo cambió (inicio del combate, relevo o uno debilitado), el nuevo entra lanzado desde una Poké Ball
    def _revisar_entradas(self):
        for quien, nombre in (("ia", self.combate.nombre_ia), ("jugador", self.combate.nombre_jugador)):
            if nombre != self.nombres_vistos[quien]:
                primera_vez = self.nombres_vistos[quien] is None
                self.nombres_vistos[quien] = nombre
                # Al empezar el combate el del jugador sale un poco después que el rival
                retraso = 25 if (primera_vez and quien == "jugador") else 0
                self.entradas[quien] = entrada_pokemon.EntradaPokemon(quien, retraso)

    # Dibuja la animación de entrada si la hay; si no, el Pokémon normal (con su parpadeo de daño)
    def _dibujar_pokemon_o_entrada(self, pantalla, imagen_pokemon, pos, quien):
        entrada = self.entradas[quien]
        if entrada is None:
            self._dibujar_pokemon(pantalla, imagen_pokemon, pos, quien)
            return
        entrada.dibujar(pantalla, imagen_pokemon, pos)
        if entrada.terminada():
            self.entradas[quien] = None

    # La caja de vida aparece cuando el Pokémon ya salió de la bola
    def _caja_visible(self, quien):
        entrada = self.entradas[quien]
        return entrada is None or entrada.salio()

    # Dibuja el texto de daño subiendo poco a poco mientras dura su contador
    def _dibujar_texto_flotante(self, pantalla, quien, x, y_base):
        texto, timer = self.texto_flotante[quien]
        if timer > 0:
            timer -= 1
            self.texto_flotante[quien] = (texto, timer)
            txt = FUENTE_GRANDE.render(texto, True, (255, 80, 80))
            pantalla.blit(txt, (x, y_base - (45 - timer)))

    # Si cambió de menú, la selección vuelve al primer botón.
    def _sincronizar(self):
        contexto = (self.combate.turno, self.combate.sub_menu)
        if contexto != self._contexto:
            self._contexto = contexto
            self.seleccion = 0

    # HP que se muestra en la barra: se acerca poco a poco al real para animar el daño.
    def _hp_visible(self, quien, nombre, hp, hp_max):
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

    # Energía que se muestra en la barra: se acerca poco a poco a la real (igual que la vida)
    def _energia_visible(self, quien, nombre, energia):
        guardado = self.energia_visible.get(quien)
        if guardado is None or guardado[0] != nombre:
            valor = energia
        else:
            valor = guardado[1]
            paso = ENERGIA_MAX / 60
            if valor > energia:
                valor = max(energia, valor - paso)
            elif valor < energia:
                valor = min(energia, valor + paso)
        self.energia_visible[quien] = (nombre, valor)
        return valor

    # Barra de energía bajo la de vida: se llena con cada ataque o golpe recibido y brilla cuando alcanza para la habilidad fuerte
    def _dibujar_barra_energia(self, pantalla, caja_x, caja_y, nombre, energia):
        x0, y0, x1, y1 = BARRA_ENERGIA
        barra_x = caja_x + int(x0 * ESCALA_CAJA)
        barra_y = caja_y + int(y0 * ESCALA_CAJA)
        barra_ancho = int((x1 - x0 + 1) * ESCALA_CAJA)
        barra_alto = int((y1 - y0 + 1) * ESCALA_CAJA)

        # Fondo (pista) de la barra
        pista = pygame.Rect(barra_x, barra_y, barra_ancho, barra_alto)
        pygame.draw.rect(pantalla, (250, 252, 250), pista, border_radius=4)

        # Relleno según la energía mostrada
        mostrada = self._energia_visible("jugador", nombre, energia)
        proporcion = max(0.0, min(1.0, mostrada / ENERGIA_MAX))
        lista = energia >= COSTO_FUERTE
        color, brillo = COLOR_ENERGIA_LISTA if lista else COLOR_ENERGIA
        ancho = int(barra_ancho * proporcion)
        if ancho > 0:
            pygame.draw.rect(pantalla, color, (barra_x, barra_y, ancho, barra_alto), border_radius=4)
            pygame.draw.rect(pantalla, brillo, (barra_x + 2, barra_y + 1, max(0, ancho - 4), max(1, barra_alto // 3)), border_radius=3)
        pygame.draw.rect(pantalla, (105, 117, 93), pista, 2, border_radius=4)

        # Cuando está llena, el borde parpadea suavemente para avisar que la habilidad fuerte está lista
        if lista:
            pulso = (pygame.time.get_ticks() // 300) % 2 == 0
            pygame.draw.rect(pantalla, (255, 255, 255) if pulso else (250, 190, 30), pista.inflate(4, 4), 2, border_radius=5)

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

        # Solo la caja del jugador muestra la energía (debajo de la vida) y la vida en números
        if mostrar_numeros:
            self._dibujar_barra_energia(pantalla, caja_x, caja_y, nombre, self.combate.energia["jugador"][nombre])
            txt_hp = FUENTE_CHICA.render(f"{hp} / {hp_max}", True, NEGRO)
            x_num = caja_x + int((barra_x0 + 120) * ESCALA_CAJA)   # borde derecho del texto
            y_num = caja_y + int((barra_y0 + 20) * ESCALA_CAJA)    # borde superior del texto
            pantalla.blit(txt_hp, (x_num - txt_hp.get_width(), y_num))

    # Botones que se recorren con las flechas (VOLVER solo se pulsa con mouse; con teclado es ESC).
    def zonas_navegables(self):
        return [z for z in self.zonas_clic() if z[0] != "volver"]

    # Mueve el botón resaltado con las flechas.
    def mover_seleccion(self, tecla):
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

    # Resalta el botón que está bajo el mouse (si hay uno).
    def seleccionar_en(self, pos_real):
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
            usables = combate.indices_usables("jugador")
            zonas = []
            for i in range (len(combate.datos_jugador["habilidades"])):
                if not usables or i in usables:
                    zonas.append((("habilidad", i), rect_habilidad(i)))
        elif combate.sub_menu == "cambiar":
            zonas = [(("pokemon", i), rect_pokemon(i)) for i in range(len(combate.equipo_jugador))]
        else:
            return []
        return zonas + [("volver", RECT_VOLVER)]

    # Acción del botón que está bajo la posición del mouse, o None.
    def accion_en(self, pos_real):
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
        self._revisar_entradas()
        tema = TEMAS_TIPO_COMBATE.get(combate.datos_jugador["tipo"], TEMAS_TIPO_COMBATE["Fuego"])
        # Cada sprite se ajusta a su caja: los grandes se reducen y todos apoyan los pies en el círculo (ver ajustar_tamano_pokemon)
        pokemon_ia = ajustar_tamano_pokemon(combate.nombre_ia, "ia", obtener_pokemon(combate.nombre_ia, "frente", TAM_LIENZO_POKEMON["ia"], (200, 50, 50)))                   #Pokemon rival tamano
        pokemon_jugador = ajustar_tamano_pokemon(combate.nombre_jugador, "jugador", obtener_pokemon(combate.nombre_jugador, "espalda", TAM_LIENZO_POKEMON["jugador"], (50, 100, 200)))    #Pokemon aliado tamano

        # Fondo y bases del escenario elegido
        pantalla.blit(obtener_fondo_escenario(self.escenario), (0, 0))
        dibujar_bases(pantalla, self.escenario)

        # Cuánto se mueve cada Pokémon durante la animación (embestida, sacudida...) y su posición final
        desplazamiento_ia = self.gestor.desplazamiento("ia")
        desplazamiento_jugador = self.gestor.desplazamiento("jugador")
        pos_ia = (POS_POKEMON_IA[0] + desplazamiento_ia[0], POS_POKEMON_IA[1] + desplazamiento_ia[1])
        pos_jug = (POS_POKEMON_JUG[0] + desplazamiento_jugador[0], POS_POKEMON_JUG[1] + desplazamiento_jugador[1])
        self._dibujar_pokemon_o_entrada(pantalla, pokemon_ia, pos_ia, "ia") #Pokemon rival posicion
        self._dibujar_pokemon_o_entrada(pantalla, pokemon_jugador, pos_jug, "jugador") #Pokemon aliado posicion
        # Efectos de las habilidades (baldosas de stats sobre la silueta y partículas)
        self.gestor.dibujar_sobre_pokemons(pantalla, {"ia": (pokemon_ia, pos_ia), "jugador": (pokemon_jugador, pos_jug)})
        self.gestor.dibujar(pantalla)
        # Texto de daño sobre cada Pokémon
        self._dibujar_texto_flotante(pantalla, "ia", 1360, 150)
        self._dibujar_texto_flotante(pantalla, "jugador", 500, 470)

        # Cajas de vida: la del rival sin números y la del jugador con ellos
        if self._caja_visible("ia"):
            self._dibujar_bandeja_equipo(pantalla, "ia")
            self._dibujar_caja_vida(pantalla, "rival", combate.nombre_ia, combate.hp_actual_ia, combate.hp_max_ia, False)
        if self._caja_visible("jugador"):
            self._dibujar_bandeja_equipo(pantalla, "jugador")
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
        if combate.turno == "jugador" and combate.sub_menu == "principal" and not self.ocupado():
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
                sin_usos = idx not in combate.indices_usables("jugador")
                if caja and sin_usos:
                    caja = caja.copy()
                    caja.fill((90, 90, 90), special_flags=pygame.BLEND_RGB_MULT)
                    caja.fill((105, 105, 110), special_flags=pygame.BLEND_RGB_ADD)
                if caja:
                    pantalla.blit(caja, rect_boton.topleft)
                else:   # respaldo si falta la imagen
                    pygame.draw.rect(pantalla, tema["principal"], rect_boton, border_radius=12)
                    pygame.draw.rect(pantalla, NEGRO, rect_boton, 3, border_radius=12)
                # Nombre del ataque en la mitad de arriba de la caja
                texto_habilidad = FUENTE_HABILIDAD .render(nombre_habilidad, True,(95, 95, 100) if sin_usos else NEGRO)
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
        if 0 <= self.seleccion < len(zonas) and not self.ocupado():
            # En el cambio de Pokémon la propia caja seleccionada ya marca la selección
            es_equipo = combate.turno == "jugador" and combate.sub_menu == "cambiar" and isinstance(zonas[self.seleccion][0], tuple)
            if not es_equipo:
                dibujar_resalte(pantalla, zonas[self.seleccion][1])
        # VOLVER no se navega con flechas: solo se resalta cuando el mouse está encima
        pos_mouse = pos_virtual(pygame.mouse.get_pos())
        for accion, rect in self.zonas_clic():
            if accion == "volver" and rect.collidepoint(pos_mouse):
                dibujar_resalte(pantalla, rect)