# ----------------- ESCENA DE COMBATE: dibujo, animaciones y botones -----------------
# ===== TEMA: Modularidad (Clase 10) =====
# Se importan módulos de Python, propios (sonido, efectos, config, pokemons) y del paquete (.utilidades, .recursos)
import pygame

import sonido
import efectos
from config import (
    BLANCO, NEGRO, GRIS_CLARO, GRIS_OSCURO, AZUL_BOTON, ROJO_BOTON, VERDE_BOTON, FUENTE, FUENTE_CHICA, FUENTE_GRANDE, FUENTE_HABILIDAD, RUTA_FUENTE
)
from pokemons import CATALOGO_POKEMONS
# ===== TEMA: Modularidad (Clase 10) =====
# Se reutiliza calcular_pp del módulo motor_combate para mostrar los PP máximos de cada habilidad
from motor_combate import calcular_pp, es_fuerte, COSTO_FUERTE, ENERGIA_MAX
from config import COLORES_TIPO
from .utilidades import pos_virtual, dibujar_resalte, separar_texto_en_lineas
from .recursos import (
    obtener_pokemon, obtener_caja, obtener_fondo_escenario, dibujar_bases, obtener_barra_mensaje,
    obtener_caja_ataque, obtener_caja_equipo, ESCALA_CAJA, ESCALA_ATAQUE, ESCALA_EQUIPO,
    TAM_ATAQUE, TAM_EQUIPO, BARRA_MSJ_RECT,
)

# ===== TEMA: Diccionarios anidados (Clase 11) =====
# tipo -> diccionario de colores (tuplas RGB)
# Paleta de colores por tipo de Pokémon (se usa como respaldo si falta alguna imagen del combate)
TEMAS_TIPO_COMBATE = {
    "Fuego": {"fondo_top": (70, 25, 15), "fondo_bot": (35, 12, 8), "suelo_rival": (110, 45, 25), "suelo_jug": (130, 55, 30), "principal": (235, 100, 40)},
    "Agua": {"fondo_top": (15, 40, 75), "fondo_bot": (8, 20, 40), "suelo_rival": (30, 80, 130), "suelo_jug": (40, 100, 160), "principal": (40, 130, 235)},
    "Planta": {"fondo_top": (25, 60, 30), "fondo_bot": (12, 30, 15), "suelo_rival": (50, 110, 60), "suelo_jug": (65, 135, 75), "principal": (50, 180, 70)},
    "Eléctrico": {"fondo_top": (75, 70, 20), "fondo_bot": (35, 32, 8), "suelo_rival": (120, 110, 30), "suelo_jug": (145, 135, 35), "principal": (240, 205, 30)},
    "Tierra": {"fondo_top": (65, 45, 25), "fondo_bot": (30, 20, 10), "suelo_rival": (100, 75, 45), "suelo_jug": (125, 95, 55), "principal": (170, 120, 60)},
}

# ===== TEMA: Tuplas (Clase 11) =====
# Posiciones guardadas como tuplas (x, y)
# Posiciones del combate (coordenadas virtuales 1920x1080)
POS_POKEMON_IA = (1030, 160)        # Posicion Pokemon IA
POS_POKEMON_JUG = (300, 350)        # Posicion Pokemon Jugador

# ===== TEMA: Diccionarios (Clase 11) + Tuplas (Clase 11) =====
# Diccionarios con clave 'rival'/'jugador' y tuplas como valores
# Cajas de vida (Jugador y Rival)
BARRA_CAJA = {"rival": (93, 40, 211, 49), "jugador": (116, 40, 233, 49)}        # Barra de vida
# ===== TEMA: Tuplas (Clase 11) =====
# Color RGB (inmutable) de la barra de energía mientras todavía no está cargada
COLOR_ENERGIA_VACIA = (140, 140, 150)
POS_CAJA = {"rival": (600, 100), "jugador": (1200, 650)}                        # Posicion caja de vida

# ===== TEMA: POO (Clase 16) =====
# Cada botón es un objeto pygame.Rect
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


# ===== TEMA: Funciones (Clase 7) + Expresiones y operadores (Clase 3) =====
# Calcula la posición con * y +; retorna un Rect
def rect_habilidad(idx):
    # Las 4 habilidades en una sola fila
    return pygame.Rect(ORIGEN_ATAQUES[0] + idx * (TAM_ATAQUE[0] + SEP_ATAQUES[0]),
                       ORIGEN_ATAQUES[1],
                       TAM_ATAQUE[0], TAM_ATAQUE[1])


# ===== TEMA: Funciones (Clase 7) =====
# Misma idea que rect_habilidad, para las cajas del equipo
# Rectángulo en pantalla de la caja del Pokémon número idx del equipo (las cajas van en fila)
def rect_pokemon(idx):
    return pygame.Rect(ORIGEN_EQUIPO[0] + idx * (TAM_EQUIPO[0] + SEP_EQUIPO), ORIGEN_EQUIPO[1], TAM_EQUIPO[0], TAM_EQUIPO[1])


# ===== TEMA: POO (Clase 16) =====
# Clase EscenaCombate: dibuja el combate y guarda el estado de las animaciones
# Dibuja el combate y maneja las animaciones
class EscenaCombate:
    
    # ===== TEMA: POO (Clase 16) + Diccionarios (Clase 11) =====
    # Constructor con parámetro por defecto; flash y texto_flotante son diccionarios por bando
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

    # ===== TEMA: POO (Clase 16) =====
    # Método que retorna un booleano delegando en otro objeto (gestor)
    # True mientras se reproduce la animación de una habilidad.
    def ocupado(self):
        return self.gestor.ocupado()

    # ===== TEMA: Funciones (Clase 7) + Tuplas (Clase 11) =====
    # Desempaqueta la tupla habilidad; al_impactar es una función recibida como parámetro
    # Anima la habilidad; 'al_impactar' (aplicar el daño en el motor) se llama en el golpe.
    def lanzar_habilidad(self, quien, habilidad, al_impactar, mensaje=None):
        nombre, _potencia, tipo = habilidad
        if mensaje:
            self.combate.mensaje = mensaje
        self.combate.sub_menu = "principal"
        self.gestor.lanzar(quien, nombre, tipo, al_impactar)

    # ===== TEMA: Bucles (Clase 4) + Listas (Clase 11) + Condicionales (Clase 4) =====
    # for desempaquetando tuplas de la lista eventos; if/elif según el multiplicador; clear() vacía la lista
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
            # ===== TEMA: Condicionales (Clase 4) =====
            # Eventos nuevos del motor: ataque que falla o es esquivado, escudo que bloquea y cura del escudo
            elif tipo == "fallo":
                self.texto_flotante[objetivo] = ("¡Falló!", 45)
            elif tipo == "escudo":
                self.texto_flotante[objetivo] = ("¡Bloqueado!", 45)
            elif tipo == "curar":
                self.texto_flotante[objetivo] = (f"+{cantidad} HP", 45)
        self.combate.eventos.clear()

    # ===== TEMA: Condicionales (Clase 4) + Expresiones y operadores (Clase 3) =====
    # // y % alternan la imagen normal y la blanca cada 4 frames
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

    # ===== TEMA: Condicionales (Clase 4) + Tuplas (Clase 11) =====
    # Desempaqueta (texto, timer) y guarda la tupla actualizada en el diccionario
    # Dibuja el texto de daño subiendo poco a poco mientras dura su contador
    def _dibujar_texto_flotante(self, pantalla, quien, x, y_base):
        texto, timer = self.texto_flotante[quien]
        if timer > 0:
            timer -= 1
            self.texto_flotante[quien] = (texto, timer)
            txt = FUENTE_GRANDE.render(texto, True, (255, 80, 80))
            pantalla.blit(txt, (x, y_base - (45 - timer)))

    # ===== TEMA: Condicionales (Clase 4) + Tuplas (Clase 11) =====
    # Compara tuplas (turno, sub_menu) para detectar el cambio
    # Si cambió de menú, la selección vuelve al primer botón.
    def _sincronizar(self):
        contexto = (self.combate.turno, self.combate.sub_menu)
        if contexto != self._contexto:
            self._contexto = contexto
            self.seleccion = 0

    # ===== TEMA: Condicionales (Clase 4) + Expresiones y operadores (Clase 3) =====
    # if/elif/else con max() y min()
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

    # ===== TEMA: Funciones (Clase 7) + Diccionarios (Clase 11) =====
    # POS_CAJA[lado] indexa diccionarios; desempaqueta tuplas
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
        # ===== TEMA: Condicionales (Clase 4) =====
        # if/elif/else encadenados con comparaciones
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

    # ===== TEMA: Funciones (Clase 7) + Diccionarios (Clase 11) + Condicionales (Clase 4) =====
    # COLORES_TIPO[tipo.upper()] indexa un diccionario; if/else cambia el color según la energía
    # Barra de energía del Pokémon del jugador, encima de su caja de vida: gris mientras se carga y del color de su tipo al llegar a 100
    def _dibujar_barra_energia(self, pantalla):
        combate = self.combate
        caja = obtener_caja("jugador")
        if caja is None:
            return
        caja_x, caja_y = POS_CAJA["jugador"]
        # La energía actual del Pokémon activo; min() evita que la barra se salga si pasara de 100
        energia = min(ENERGIA_MAX, combate.energia["jugador"][combate.nombre_jugador])
        proporcion = energia / ENERGIA_MAX
        # Cargada = ya alcanza el costo de la habilidad fuerte
        cargada = energia >= COSTO_FUERTE
        if cargada:
            color = COLORES_TIPO.get(combate.datos_jugador["tipo"].upper(), COLOR_ENERGIA_VACIA)
        else:
            color = COLOR_ENERGIA_VACIA

        # Posición: justo encima de la caja de vida, con un margen a cada lado
        margen = 24
        barra_ancho = caja.get_width() - 2 * margen
        barra_alto = 16
        barra_x = caja_x + margen
        barra_y = caja_y - barra_alto - 8
        # Texto sobre la barra: "ENERGÍA" a la izquierda y el valor a la derecha (o ¡LISTA! al cargarse)
        txt_titulo = FUENTE_CHICA.render("ENERGÍA", True, NEGRO)
        valor = "¡LISTA!" if cargada else f"{energia}/{ENERGIA_MAX}"
        txt_valor = FUENTE_CHICA.render(valor, True, color if cargada else GRIS_OSCURO)
        y_texto = barra_y - txt_titulo.get_height() - 2
        pantalla.blit(txt_titulo, (barra_x, y_texto))
        pantalla.blit(txt_valor, (barra_x + barra_ancho - txt_valor.get_width(), y_texto))

        # Fondo oscuro de la barra, relleno proporcional y borde
        pygame.draw.rect(pantalla, GRIS_OSCURO, (barra_x, barra_y, barra_ancho, barra_alto), border_radius=6)
        ancho_relleno = int(barra_ancho * proporcion)
        if ancho_relleno > 0:
            pygame.draw.rect(pantalla, color, (barra_x, barra_y, ancho_relleno, barra_alto), border_radius=6)
        pygame.draw.rect(pantalla, NEGRO, (barra_x, barra_y, barra_ancho, barra_alto), 2, border_radius=6)

    # ===== TEMA: Listas (Clase 11) =====
    # Lista por comprensión con filtro: crea una lista nueva sin la zona 'volver'
    # Botones que se recorren con las flechas (VOLVER solo se pulsa con mouse; con teclado es ESC).
    def zonas_navegables(self):
        return [z for z in self.zonas_clic() if z[0] != "volver"]

    # ===== TEMA: Expresiones y operadores (Clase 3) =====
    # % (módulo) hace que la selección dé la vuelta de un extremo al otro
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

    # ===== TEMA: Funciones (Clase 7) =====
    # Retorna la acción del botón resaltado o None; indexa una lista de tuplas
    def accion_seleccionada(self):
        # Devuelve la acción del botón resaltado (la que ejecuta ENTER)
        self._sincronizar()
        zonas = self.zonas_navegables()
        if 0 <= self.seleccion < len(zonas):
            return zonas[self.seleccion][0]
        return None

    # ===== TEMA: Bucles (Clase 4) + Tuplas (Clase 11) =====
    # for + enumerate con desempaquetado (_, rect)
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

    # ===== TEMA: Condicionales (Clase 4) + Listas (Clase 11) =====
    # Varios return según el estado; retorna listas de tuplas (acción, rectángulo)
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
        # ===== TEMA: Listas (Clase 11) =====
        # Listas por comprensión; concatenación con +
        # Submenús: una zona por habilidad o por Pokémon del equipo, más VOLVER (cada zona es (acción, rectángulo))
        if combate.sub_menu == "luchar":
            zonas = [(("habilidad", i), rect_habilidad(i)) for i in range(len(combate.datos_jugador["habilidades"]))]
        elif combate.sub_menu == "cambiar":
            zonas = [(("pokemon", i), rect_pokemon(i)) for i in range(len(combate.equipo_jugador))]
        else:
            return []
        return zonas + [("volver", RECT_VOLVER)]

    # ===== TEMA: Bucles (Clase 4) =====
    # for con return anticipado
    # Acción del botón que está bajo la posición del mouse, o None.
    def accion_en(self, pos_real):
        pos = pos_virtual(pos_real)
        for accion, rect in self.zonas_clic():
            if rect.collidepoint(pos):
                return accion
        return None

    # ===== TEMA: Funciones (Clase 7) + Modularidad (Clase 10) =====
    # Método largo que combina funciones de recursos.py, utilidades.py y efectos.py
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
        # Barra de energía del jugador (solo mientras el combate sigue)
        if combate.turno != "fin":
            self._dibujar_barra_energia(pantalla)

        eligiendo_ataque = combate.turno == "jugador" and combate.sub_menu == "luchar"
        # La barra de mensajes se ve siempre, tambien al elegir habilidad
        barra = obtener_barra_mensaje(BARRA_MSJ_RECT.w, BARRA_MSJ_RECT.h)

        # Vida baja = menos del 20% de la vida máxima del Pokémon del jugador (no cuenta al terminar el combate)
        # ===== TEMA: Expresiones booleanas (Clase 3) =====
        # and y comparación encadenada para detectar vida baja
        en_peligro = (combate.turno != "fin"
              and 0 < combate.hp_actual_jugador <= combate.hp_max_jugador * 0.2)
        
        # ===== TEMA: Condicionales (Clase 4) =====
        # if/else: sonido en bucle mientras la vida está baja
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

        # ===== TEMA: Condicionales (Clase 4) =====
        # if/elif/elif: qué se dibuja según el submenú (principal, luchar, cambiar, fin)
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

        # ===== TEMA: Bucles (Clase 4) + Tuplas (Clase 11) =====
        # for + enumerate; desempaqueta la tupla (nombre, potencia, tipo)
        # Submenú de habilidades: una caja por habilidad, con su nombre y sus PP restantes
        elif combate.turno == "jugador" and combate.sub_menu == "luchar":
            habilidades = combate.datos_jugador["habilidades"]
            for idx, habilidad in enumerate(habilidades):
                nombre_habilidad, potencia, tipo_habilidad = habilidad
                rect_boton = rect_habilidad(idx)
                # ===== TEMA: Listas (Clase 11) + Condicionales (Clase 4) =====
                # Se lee de la lista de PP del Pokémon activo cuántos usos le quedan a esta habilidad (misma posición idx); si es 0 la caja se oscurece
                pp_actual = combate.pp_jugador[combate.nombre_jugador][idx]
                pp_maximo = calcular_pp(habilidad)
                # ===== TEMA: Condicionales (Clase 4) + Listas (Clase 11) =====
                # La habilidad fuerte muestra su energía cargada (EN) en vez de PP; sin_usos es True si el motor no deja usarla ahora
                # (sin PP, sin energía suficiente o con el escudo ya activo). 'in' sobre la lista de índices que da el motor
                etiqueta_recurso = "PP"
                if es_fuerte(habilidad):
                    etiqueta_recurso = "EN"
                    pp_actual = combate.energia["jugador"][combate.nombre_jugador]
                    pp_maximo = COSTO_FUERTE
                sin_usos = idx not in combate.indices_usables("jugador")
                caja = obtener_caja_ataque(tipo_habilidad)
                # Se oscurece una copia para no modificar la imagen guardada en caché
                if caja and sin_usos:
                    caja = caja.copy()
                    caja.fill((120, 120, 120, 255), special_flags=pygame.BLEND_RGBA_MULT)
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
                # ===== TEMA: Expresiones y operadores (Clase 3) =====
                # PP como "actual/máximo" con un f-string; el color pasa a rojo cuando ya no quedan
                txt_pp = FUENTE_HABILIDAD .render(f"{etiqueta_recurso} {pp_actual}/{pp_maximo}", True, (170, 40, 40) if sin_usos else (60, 75, 60))
                pantalla.blit(txt_pp, txt_pp.get_rect(midleft=(rect_boton.x + int(53 * ESCALA_ATAQUE), rect_boton.y + int(36 * ESCALA_ATAQUE))))
            self._dibujar_boton_volver(pantalla)

        # ===== TEMA: Bucles (Clase 4) + Diccionarios (Clase 11) =====
        # for + enumerate; consulta los diccionarios hp_jugador y CATALOGO_POKEMONS
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

        # ===== TEMA: Condicionales (Clase 4) =====
        # if anidados; isinstance comprueba si la acción es una tupla
        # Borde en el botón seleccionado (con flechas o con el mouse)
        zonas = self.zonas_navegables()
        if 0 <= self.seleccion < len(zonas) and not self.gestor.ocupado():
            # En el cambio de Pokémon la propia caja seleccionada ya marca la selección
            es_equipo = combate.turno == "jugador" and combate.sub_menu == "cambiar" and isinstance(zonas[self.seleccion][0], tuple)
            if not es_equipo:
                dibujar_resalte(pantalla, zonas[self.seleccion][1])
        # ===== TEMA: Bucles (Clase 4) =====
        # for sobre la lista de tuplas (acción, rectángulo)
        # VOLVER no se navega con flechas: solo se resalta cuando el mouse está encima
        pos_mouse = pos_virtual(pygame.mouse.get_pos())
        for accion, rect in self.zonas_clic():
            if accion == "volver" and rect.collidepoint(pos_mouse):
                dibujar_resalte(pantalla, rect)
                