import math
import os
import random
import sys
import pygame

# Inicializar Pygame
pygame.init()
pygame.font.init()

# Resolución Virtual Interna de Referencia (Full HD)
ANCHO_VIRTUAL, ALTO_VIRTUAL = 1920, 1080

# Obtener la resolución real del monitor actual de forma responsiva
info_pantalla = pygame.display.Info()
ANCHO_REAL, ALTO_REAL = info_pantalla.current_w, info_pantalla.current_h

# Pantalla en modo pantalla completa real (el sistema estirará la superficie virtual)
pantalla_real = pygame.display.set_mode((ANCHO_REAL, ALTO_REAL), pygame.FULLSCREEN | pygame.SCALED)
pantalla = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))

pygame.display.set_caption("Combate Proyecto - Pokémon Añil Ultimate Edition (Responsivo)")

# Colores Base y de Interfaz DS
BLANCO = (255, 255, 255)
NEGRO = (30, 30, 30)
GRIS_CLARO = (245, 245, 250)
GRIS_OSCURO = (70, 70, 80)
AZUL_DS = (30, 144, 255)
AZUL_OSCURO = (15, 45, 90)
ROJO_BOTON = (215, 60, 60)
VERDE_BOTON = (40, 180, 90)
AZUL_BOTON = (30, 140, 210)
BORDE_CAJA = (40, 40, 50)
AMARILLO_ALERTA = (230, 190, 40)
ROJO_ALERTA = (220, 50, 50)

# Colores de Tipos
COLORES_TIPO = {
    "FUEGO": (230, 80, 40),
    "AGUA": (40, 130, 235),
    "PLANTA": (50, 180, 70),
    "ELÉCTRICO": (220, 190, 20),
    "TIERRA": (160, 110, 50),
}

# Fuentes Escaladas
FUENTE = pygame.font.SysFont("Verdana", 26, bold=True)
FUENTE_CHICA = pygame.font.SysFont("Verdana", 20, bold=True)
FUENTE_GRANDE = pygame.font.SysFont("Verdana", 38, bold=True)

# ----------------- BASE DE DATOS DE LOS 25 POKÉMON -----------------
SECCIONES_POKEMON = {
    "FUEGO": ["charmander", "vulpix", "growlithe", "ponyta", "magmar"],
    "AGUA": ["squirtle", "psyduck", "poliwag", "horsea", "staryu"],
    "PLANTA": ["bulbasaur", "oddish", "bellsprout", "tangela", "exeggcute"],
    "ELÉCTRICO": ["pikachu", "magnemite", "voltorb", "electabuzz", "mareep"],
    "TIERRA": ["sandshrew", "geodude", "cubone", "phanpy", "diglett"],
}

CATALOGO_POKEMONS = {
    "charmander": {
        "tipo": "Fuego", "hp": 120, "ataque": 52, "defensa": 43, "atk_esp": 60, "def_esp": 50, "velocidad": 65,
        "desc": "Criatura de naturaleza cálida que habita en zonas montañosas y rocosas. La llama en la punta de su cola refleja su estado vital y anímico.",
        "habilidades": [("Arañazo", 45, "Normal"), ("Lanzallamas", 65, "Fuego"), ("Envite Ígneo", 110, "Fuego"), ("Foco Energía", 0, "Estado")]
    },
    "vulpix": {
        "tipo": "Fuego", "hp": 110, "ataque": 41, "defensa": 40, "atk_esp": 50, "def_esp": 65, "velocidad": 65,
        "desc": "Ágil zorro de pelaje rojizo que manipula llamas internas a voluntad. Al nacer posee una sola cola que se ramifica con los años.",
        "habilidades": [("Ataque Rápido", 40, "Normal"), ("Ascuas", 60, "Fuego"), ("Giro Fuego", 105, "Fuego"), ("Pantalla Humo", 0, "Estado")]
    },
    "growlithe": {
        "tipo": "Fuego", "hp": 130, "ataque": 70, "defensa": 45, "atk_esp": 70, "def_esp": 50, "velocidad": 60,
        "desc": "Fiel canino dotado de un valor inquebrantable. Protege su territorio con fiereza y guarda un fuerte lazo de lealtad con su cuidador.",
        "habilidades": [("Mordisco", 50, "Normal"), ("Colmillo Ígneo", 70, "Fuego"), ("Envite Ígneo", 120, "Fuego"), ("Rugido", 0, "Estado")]
    },
    "ponyta": {
        "tipo": "Fuego", "hp": 115, "ataque": 85, "defensa": 55, "atk_esp": 65, "def_esp": 65, "velocidad": 90,
        "desc": "Equino veloz cuyas patas y crines arden en llamas. Sus aptitudes para el galope se potencian al saltar obstáculos naturales.",
        "habilidades": [("Patada", 45, "Normal"), ("Rueda Fuego", 65, "Fuego"), ("Nitrocarga", 110, "Fuego"), ("Agilidad", 0, "Estado")]
    },
    "magmar": {
        "tipo": "Fuego", "hp": 140, "ataque": 95, "defensa": 57, "atk_esp": 100, "def_esp": 85, "velocidad": 93,
        "desc": "Habita inmerso en las profundidades de los cráteres volcánicos. Su temperatura corporal alcanza niveles extremos capaces de fundir la roca.",
        "habilidades": [("Puño Certero", 50, "Normal"), ("Puño Fuego", 70, "Fuego"), ("Magmatormenta", 120, "Fuego"), ("Malicioso", 0, "Estado")]
    },
    "squirtle": {
        "tipo": "Agua", "hp": 125, "ataque": 48, "defensa": 65, "atk_esp": 50, "def_esp": 64, "velocidad": 43,
        "desc": "Tortuga acuática cuyo caparazón hidroaerodinámico reduce la resistencia al nadar y sirve como poderosa defensa ante impactos.",
        "habilidades": [("Placaje", 45, "Normal"), ("Pistola Agua", 60, "Agua"), ("Hidrobomba", 115, "Agua"), ("Refugio", 0, "Estado")]
    },
    "psyduck": {
        "tipo": "Agua", "hp": 120, "ataque": 52, "defensa": 48, "atk_esp": 65, "def_esp": 50, "velocidad": 55,
        "desc": "Criatura despistada que sufre jaquecas crónicas. Cuando el dolor de cabeza llega al límite, libera ondas de poder psíquico oculto.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Surf", 65, "Agua"), ("Hidropulso", 110, "Agua"), ("Amnesia", 0, "Estado")]
    },
    "poliwag": {
        "tipo": "Agua", "hp": 110, "ataque": 50, "defensa": 40, "atk_esp": 40, "def_esp": 40, "velocidad": 90,
        "desc": "Anfibio de piel traslúcida que permite observar su órgano vital en espiral. Se desenvuelve con soltura en corrientes fluviales.",
        "habilidades": [("Bofetón", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Hidrobomba", 120, "Agua"), ("Hipnosis", 0, "Estado")]
    },
    "horsea": {
        "tipo": "Agua", "hp": 105, "ataque": 40, "defensa": 70, "atk_esp": 70, "def_esp": 25, "velocidad": 60,
        "desc": "Pequeño habitante marino que nada oscilando su aleta dorsal. Ante amenazas inminentes, expulsa chorros de tinta para camuflarse.",
        "habilidades": [("Pistola Agua", 45, "Agua"), ("Rayos Burbuja", 65, "Agua"), ("Hidrobomba", 115, "Agua"), ("Smog", 0, "Estado")]
    },
    "staryu": {
        "tipo": "Agua", "hp": 115, "ataque": 45, "defensa": 55, "atk_esp": 70, "def_esp": 55, "velocidad": 85,
        "desc": "Misterioso organismo marino con simetría estelar. Su núcleo central emite pulsos lumínicos durante las horas nocturnas.",
        "habilidades": [("Rapidez", 45, "Normal"), ("Pistola Agua", 60, "Agua"), ("Rayo Hielo", 110, "Agua"), ("Recuperación", 0, "Estado")]
    },
    "bulbasaur": {
        "tipo": "Planta", "hp": 125, "ataque": 49, "defensa": 49, "atk_esp": 65, "def_esp": 65, "velocidad": 45,
        "desc": "Reptil pacífico que transporta un bulbo vegetal en el dorso. Este bulbo crece absorbiendo la luz solar durante el día.",
        "habilidades": [("Placaje", 45, "Normal"), ("Látigo Cepa", 60, "Planta"), ("Rayo Solar", 115, "Planta"), ("Drenadoras", 0, "Estado")]
    },
    "oddish": {
        "tipo": "Planta", "hp": 110, "ataque": 50, "defensa": 55, "atk_esp": 75, "def_esp": 65, "velocidad": 30,
        "desc": "Organismo de hábitos nocturnos. Durante el día permanece enterrado absorbiendo nutrientes minerales del suelo forestal.",
        "habilidades": [("Absorber", 40, "Planta"), ("Hoja Afilada", 65, "Planta"), ("Gigadrenado", 110, "Planta"), ("Polvo Sueño", 0, "Estado")]
    },
    "bellsprout": {
        "tipo": "Planta", "hp": 105, "ataque": 75, "defensa": 35, "atk_esp": 70, "def_esp": 30, "velocidad": 40,
        "desc": "Planta carnívora de tallo flexible capaz de esquivar embestidas ágilmente antes de atrapar a sus presas con lianas.",
        "habilidades": [("Látigo", 40, "Normal"), ("Látigo Cepa", 60, "Planta"), ("Bomba Lodo", 105, "Planta"), ("Crecimiento", 0, "Estado")]
    },
    "tangela": {
        "tipo": "Planta", "hp": 135, "ataque": 55, "defensa": 115, "atk_esp": 100, "def_esp": 40, "velocidad": 60,
        "desc": "Enigmática criatura envuelta en densas lianas azules. Si una de sus extremidades vegetales se desprende, no experimenta dolor.",
        "habilidades": [("Constricción", 45, "Normal"), ("Megaagotar", 65, "Planta"), ("Látigo Cerval", 115, "Planta"), ("Infortunio", 0, "Estado")]
    },
    "exeggcute": {
        "tipo": "Planta", "hp": 120, "ataque": 40, "defensa": 80, "atk_esp": 60, "def_esp": 45, "velocidad": 40,
        "desc": "Conjunto de seis semillas con aspecto de frutos que se mantienen unidas y sincronizadas mediante telepatía constante.",
        "habilidades": [("Confusión", 45, "Psíquico"), ("Megaagotar", 65, "Planta"), ("Psíquico", 110, "Psíquico"), ("Hipnosis", 0, "Estado")]
    },
    "pikachu": {
        "tipo": "Eléctrico", "hp": 110, "ataque": 55, "defensa": 40, "atk_esp": 50, "def_esp": 50, "velocidad": 90,
        "desc": "Roedor ágil que almacena energía eléctrica en sus mejillas. Al sentirse amenazado, emite potentes descargas defensivas.",
        "habilidades": [("Ataque Rápido", 45, "Normal"), ("Impactrueno", 60, "Eléctrico"), ("Trueno", 120, "Eléctrico"), ("Onda Trueno", 0, "Estado")]
    },
    "magnemite": {
        "tipo": "Eléctrico", "hp": 115, "ataque": 35, "defensa": 70, "atk_esp": 95, "def_esp": 55, "velocidad": 45,
        "desc": "Unidad mecánica flotante que desafía la gravedad mediante campos electromagnéticos emitidos por sus terminales laterales.",
        "habilidades": [("Tacleada", 40, "Normal"), ("Chispa", 65, "Eléctrico"), ("Electrocañón", 115, "Eléctrico"), ("Supersónico", 0, "Estado")]
    },
    "voltorb": {
        "tipo": "Eléctrico", "hp": 100, "ataque": 30, "defensa": 50, "atk_esp": 55, "def_esp": 55, "velocidad": 100,
        "desc": "Esfera energética inestable que guarda gran parecido con una Poké Ball. Detona ante sacudidas o estímulos bruscos.",
        "habilidades": [("Placaje", 45, "Normal"), ("Impactrueno", 60, "Eléctrico"), ("Autodestrucción", 120, "Eléctrico"), ("Pantalla Luz", 0, "Estado")]
    },
    "electabuzz": {
        "tipo": "Eléctrico", "hp": 135, "ataque": 83, "defensa": 57, "atk_esp": 95, "def_esp": 85, "velocidad": 105,
        "desc": "Humanoide corpulento atraído por las subestaciones eléctricas. Se alimenta directamente de generadores de energía.",
        "habilidades": [("Puño Certero", 50, "Normal"), ("Puño Trueno", 70, "Eléctrico"), ("Trueno", 120, "Eléctrico"), ("Pantalla de Luz", 0, "Estado")]
    },
    "mareep": {
        "tipo": "Eléctrico", "hp": 120, "ataque": 40, "defensa": 40, "atk_esp": 65, "def_esp": 45, "velocidad": 35,
        "desc": "Ovejita pacífica cuya suave lana acumula electricidad estática por fricción atmosférica, brillando en la oscuridad.",
        "habilidades": [("Placaje", 40, "Normal"), ("Onda Shock", 60, "Eléctrico"), ("Trueno", 110, "Eléctrico"), ("Growl", 0, "Estado")]
    },
    "sandshrew": {
        "tipo": "Tierra", "hp": 125, "ataque": 75, "defensa": 85, "atk_esp": 20, "def_esp": 30, "velocidad": 40,
        "desc": "Mamífero cavador adaptado a entornos áridos. Al rodar sobre sí mismo absorbe impactos y amortigua caídas con su piel acorazada.",
        "habilidades": [("Arañazo", 45, "Normal"), ("Disparo Lodo", 60, "Tierra"), ("Terremoto", 120, "Tierra"), ("Defensa Férrea", 0, "Estado")]
    },
    "geodude": {
        "tipo": "Tierra", "hp": 130, "ataque": 80, "defensa": 100, "atk_esp": 30, "def_esp": 30, "velocidad": 20,
        "desc": "Formación rocosa con consciencia propia que habita en senderos montañosos, confundiéndose fácilmente con rocas ordinarias.",
        "habilidades": [("Placaje", 45, "Normal"), ("Terratemblor", 65, "Tierra"), ("Terremoto", 120, "Tierra"), ("Fortaleza", 0, "Estado")]
    },
    "cubone": {
        "tipo": "Tierra", "hp": 120, "ataque": 50, "defensa": 95, "atk_esp": 40, "def_esp": 50, "velocidad": 35,
        "desc": "Solitaria criatura que resguarda su rostro con el cráneo de su progenitora, emitiendo melancólicos lamentos al atardecer.",
        "habilidades": [("Hueso Palo", 50, "Normal"), ("Bofetón Lodo", 60, "Tierra"), ("Huesomerang", 110, "Tierra"), ("Foco Energía", 0, "Estado")]
    },
    "phanpy": {
        "tipo": "Tierra", "hp": 140, "ataque": 60, "defensa": 60, "atk_esp": 40, "def_esp": 40, "velocidad": 40,
        "desc": "Pequeño paquidermo juguetón que utiliza su larga trompa para interactuar con su entorno y saludar a otros ejemplares.",
        "habilidades": [("Placaje", 45, "Normal"), ("Disparo Lodo", 65, "Tierra"), ("Terremoto", 115, "Tierra"), ("Encanto", 0, "Estado")]
    },
    "diglett": {
        "tipo": "Tierra", "hp": 95, "ataque": 55, "defensa": 25, "atk_esp": 35, "def_esp": 45, "velocidad": 95,
        "desc": "Especie subterránea que perfora la tierra a poca profundidad para alimentarse de raíces sin exponerse al exterior.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Bofetón Lodo", 60, "Tierra"), ("Terremoto", 110, "Tierra"), ("Acuchillar", 0, "Estado")]
    },
}

LISTA_PLANA_POKES = []
for tipo_sec, pokes in SECCIONES_POKEMON.items():
    for p in pokes:
        LISTA_PLANA_POKES.append(p)


def calcular_multiplicador(tipo_ataque, tipo_defensor):
    if tipo_ataque == "Eléctrico" and tipo_defensor == "Tierra":
        return 0.0
    tablas_ventajas = {
        "Fuego": ["Planta"],
        "Agua": ["Fuego", "Tierra"],
        "Planta": ["Agua", "Tierra"],
        "Eléctrico": ["Agua"],
        "Tierra": ["Fuego", "Eléctrico"],
    }
    if tipo_ataque in tablas_ventajas and tipo_defensor in tablas_ventajas[tipo_ataque]:
        return 2.0
    for atacante, defensores in tablas_ventajas.items():
        if tipo_defensor == atacante and tipo_ataque in defensores:
            return 0.5
    return 1.0


# ----------------- CLASE DE COMBATE -----------------
class Combate:
    def __init__(self, equipo_jugador, modo):
        self.modo = modo
        self.eq_jugador = list(equipo_jugador)
        self.idx_activo_j = 0

        pool_disponible = [p for p in LISTA_PLANA_POKES if p not in self.eq_jugador]
        self.eq_ia = random.sample(pool_disponible, len(self.eq_jugador))
        self.idx_activo_i = 0

        self.hp_jugador = {p: CATALOGO_POKEMONS[p]["hp"] for p in self.eq_jugador}
        self.hp_ia = {p: CATALOGO_POKEMONS[p]["hp"] for p in self.eq_ia}

        self.flash_ia_timer = 0
        self.flash_jug_timer = 0
        self.texto_flotante_ia = ""
        self.texto_flotante_ia_timer = 0
        self.texto_flotante_jug = ""
        self.texto_flotante_jug_timer = 0

        self.cargar_pokemons_activos()
        self.turno = "jugador"
        self.sub_menu = "principal"
        self.mensaje = f"¡El rival envió a {self.i_nombre.capitalize()}!"

    def actualizar_hp_actual(self):
        self.hp_jugador[self.p_nombre] = self.p_hp
        self.hp_ia[self.i_nombre] = self.i_hp

    def cargar_pokemons_activos(self):
        self.p_nombre = self.eq_jugador[self.idx_activo_j]
        self.p_data = CATALOGO_POKEMONS[self.p_nombre]
        self.p_hp_max = self.p_data["hp"]
        self.p_hp = self.hp_jugador[self.p_nombre]

        self.i_nombre = self.eq_ia[self.idx_activo_i]
        self.i_data = CATALOGO_POKEMONS[self.i_nombre]
        self.i_hp_max = self.i_data["hp"]
        self.i_hp = self.hp_ia[self.i_nombre]

        self.sprite_jugador = self.cargar_sprite(self.p_nombre, "espalda")
        self.sprite_ia = self.cargar_sprite(self.i_nombre, "frente")
        self.tema = TEMAS_TIPO_COMBATE.get(self.p_data["tipo"], TEMAS_TIPO_COMBATE["Fuego"])

    def cargar_sprite(self, nombre, vista):
        ruta = f"assets/pokemons/{vista}/{nombre}.png"
        if os.path.exists(ruta):
            img = pygame.image.load(ruta).convert_alpha()
            return pygame.transform.scale(img, (280, 280))
        else:
            surf = pygame.Surface((280, 280))
            surf.fill((200, 50, 50) if vista == "frente" else (50, 100, 200))
            return surf

    def ejecutar_turno(self, index_habilidad):
        if self.turno != "jugador":
            return

        hab = self.p_data["habilidades"][index_habilidad]
        nombre_hab, potencia, tipo_hab = hab

        if tipo_hab == "Estado":
            self.mensaje = f"¡{self.p_nombre.capitalize()} usó {nombre_hab}!"
        else:
            mult = calcular_multiplicador(tipo_hab, self.i_data["tipo"])
            daño = int(potencia * mult)
            self.i_hp = max(0, self.i_hp - daño)

            self.flash_ia_timer = 20
            self.texto_flotante_ia = f"-{daño} HP"
            self.texto_flotante_ia_timer = 45

            info_mult = ""
            if mult == 2.0:
                info_mult = " ¡Es muy eficaz!"
            elif mult == 0.5:
                info_mult = " No es muy eficaz..."
            elif mult == 0.0:
                info_mult = " ¡No afecta!"

            self.mensaje = f"¡{self.p_nombre.capitalize()} usó {nombre_hab}! Hizo {daño} daño (-{daño} HP).{info_mult}"

        self.actualizar_hp_actual()

        if self.i_hp <= 0:
            if self.idx_activo_i < len(self.eq_ia) - 1:
                self.idx_activo_i += 1
                self.cargar_pokemons_activos()
                self.mensaje = f"¡El rival envió a {self.i_nombre.capitalize()}!"
                self.turno = "jugador"
                self.sub_menu = "principal"
                return
            else:
                self.mensaje = "¡Has derrotado a todos los rivales! ¡Victoria!"
                self.turno = "fin"
                return

        self.turno = "ia"
        self.sub_menu = "principal"

    def cambiar_pokemon_jugador(self, nuevo_idx):
        if nuevo_idx == self.idx_activo_j:
            self.mensaje = "¡Ese Pokémon ya está combatiendo!"
            self.sub_menu = "principal"
            return
        
        nuevo_nombre = self.eq_jugador[nuevo_idx]
        if self.hp_jugador[nuevo_nombre] <= 0:
            self.mensaje = f"¡{nuevo_nombre.capitalize()} está debilitado y no puede combatir!"
            self.sub_menu = "principal"
            return

        self.actualizar_hp_actual()
        self.idx_activo_j = nuevo_idx
        self.cargar_pokemons_activos()
        self.mensaje = f"¡Adelante, {self.p_nombre.capitalize()}!"
        self.turno = "ia"
        self.sub_menu = "principal"

    def turno_ia(self):
        if self.turno != "ia":
            return

        hab = random.choice(self.i_data["habilidades"])
        nombre_hab, potencia, tipo_hab = hab

        if tipo_hab == "Estado":
            self.mensaje = f"¡El rival usó {nombre_hab}!"
        else:
            mult = calcular_multiplicador(tipo_hab, self.p_data["tipo"])
            daño = int(potencia * mult)
            self.p_hp = max(0, self.p_hp - daño)

            self.flash_jug_timer = 20
            self.texto_flotante_jug = f"-{daño} HP"
            self.texto_flotante_jug_timer = 45

            self.mensaje = f"¡{self.i_nombre.capitalize()} rival usó {nombre_hab}! Hizo {daño} daño (-{daño} HP)."

        self.actualizar_hp_actual()

        if self.p_hp <= 0:
            siguiente_idx = -1
            for idx in range(len(self.eq_jugador)):
                if self.hp_jugador[self.eq_jugador[idx]] > 0 and idx != self.idx_activo_j:
                    siguiente_idx = idx
                    break

            if siguiente_idx != -1:
                self.idx_activo_j = siguiente_idx
                self.cargar_pokemons_activos()
                self.mensaje = f"¡{self.p_nombre.capitalize()} entra al combate!"
                self.turno = "jugador"
            else:
                self.mensaje = "¡Tu equipo ha caído debilitado! Derrota..."
                self.turno = "fin"
        else:
            self.turno = "jugador"


TEMAS_TIPO_COMBATE = {
    "Fuego": {"fondo_top": (70, 25, 15), "fondo_bot": (35, 12, 8), "suelo_rival": (110, 45, 25), "suelo_jug": (130, 55, 30), "principal": (235, 100, 40)},
    "Agua": {"fondo_top": (15, 40, 75), "fondo_bot": (8, 20, 40), "suelo_rival": (30, 80, 130), "suelo_jug": (40, 100, 160), "principal": (40, 130, 235)},
    "Planta": {"fondo_top": (25, 60, 30), "fondo_bot": (12, 30, 15), "suelo_rival": (50, 110, 60), "suelo_jug": (65, 135, 75), "principal": (50, 180, 70)},
    "Eléctrico": {"fondo_top": (75, 70, 20), "fondo_bot": (35, 32, 8), "suelo_rival": (120, 110, 30), "suelo_jug": (145, 135, 35), "principal": (240, 205, 30)},
    "Tierra": {"fondo_top": (65, 45, 25), "fondo_bot": (30, 20, 10), "suelo_rival": (100, 75, 45), "suelo_jug": (125, 95, 55), "principal": (170, 120, 60)},
}


# ----------------- DIBUJAR PANTALLA DE COMBATE RESPONSIVA -----------------
def dibujar_interfaz_combate(pantalla, combate):
    for y in range(720):
        factor = y / 720.0
        r = int(combate.tema["fondo_top"][0] * (1 - factor) + combate.tema["fondo_bot"][0] * factor)
        g = int(combate.tema["fondo_top"][1] * (1 - factor) + combate.tema["fondo_bot"][1] * factor)
        b = int(combate.tema["fondo_top"][2] * (1 - factor) + combate.tema["fondo_bot"][2] * factor)
        pygame.draw.line(pantalla, (r, g, b), (0, y), (ANCHO_VIRTUAL, y))

    pygame.draw.ellipse(pantalla, (20, 20, 25), (1150, 283, 460, 125))
    pygame.draw.ellipse(pantalla, combate.tema["suelo_rival"], (1140, 275, 480, 115))
    pygame.draw.ellipse(pantalla, (20, 20, 25), (275, 743, 520, 155))
    pygame.draw.ellipse(pantalla, combate.tema["suelo_jug"], (265, 735, 540, 145))

    if combate.flash_ia_timer > 0:
        combate.flash_ia_timer -= 1
        if (combate.flash_ia_timer // 4) % 2 == 0:
            surf_flash = combate.sprite_ia.copy()
            surf_flash.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            pantalla.blit(surf_flash, (1240, 100))
        else:
            pantalla.blit(combate.sprite_ia, (1240, 100))
    else:
        pantalla.blit(combate.sprite_ia, (1240, 100))

    if combate.flash_jug_timer > 0:
        combate.flash_jug_timer -= 1
        if (combate.flash_jug_timer // 4) % 2 == 0:
            surf_flash_j = combate.sprite_jugador.copy()
            surf_flash_j.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            pantalla.blit(surf_flash_j, (380, 480))
        else:
            pantalla.blit(combate.sprite_jugador, (380, 480))
    else:
        pantalla.blit(combate.sprite_jugador, (380, 480))

    if combate.texto_flotante_ia_timer > 0:
        combate.texto_flotante_ia_timer -= 1
        txt_d = FUENTE_GRANDE.render(combate.texto_flotante_ia, True, (255, 80, 80))
        pantalla.blit(txt_d, (1360, 70 - (45 - combate.texto_flotante_ia_timer)))

    if combate.texto_flotante_jug_timer > 0:
        combate.texto_flotante_jug_timer -= 1
        txt_dj = FUENTE_GRANDE.render(combate.texto_flotante_jug, True, (255, 80, 80))
        pantalla.blit(txt_dj, (500, 450 - (45 - combate.texto_flotante_jug_timer)))

    pygame.draw.rect(pantalla, (20, 20, 30), (100, 80, 520, 110), border_radius=15)
    pygame.draw.rect(pantalla, GRIS_CLARO, (104, 84, 512, 102), border_radius=12)
    pygame.draw.rect(pantalla, BORDE_CAJA, (104, 84, 512, 102), 3, border_radius=12)
    txt_ia = FUENTE.render(f"{combate.i_nombre.capitalize()}", True, NEGRO)
    txt_ia_lvl = FUENTE.render(f"Lv.70", True, NEGRO)
    pantalla.blit(txt_ia, (130, 100))
    pantalla.blit(txt_ia_lvl, (510, 100))

    pygame.draw.rect(pantalla, GRIS_OSCURO, (230, 145, 340, 18), border_radius=6)
    ancho_hp_i = int(340 * (combate.i_hp / combate.i_hp_max))
    color_hp_i = VERDE_BOTON
    if combate.i_hp / combate.i_hp_max <= 0.5:
        color_hp_i = AMARILLO_ALERTA
    if combate.i_hp / combate.i_hp_max <= 0.2:
        color_hp_i = ROJO_ALERTA
    pygame.draw.rect(pantalla, color_hp_i, (230, 145, max(0, ancho_hp_i), 18), border_radius=6)

    pygame.draw.rect(pantalla, (20, 20, 30), (1296, 526, 524, 124), border_radius=15)
    pygame.draw.rect(pantalla, GRIS_CLARO, (1300, 530, 516, 116), border_radius=12)
    pygame.draw.rect(pantalla, BORDE_CAJA, (1300, 530, 516, 116), 3, border_radius=12)
    txt_jug = FUENTE.render(f"{combate.p_nombre.capitalize()}", True, NEGRO)
    txt_jug_lvl = FUENTE.render(f"Lv.70", True, NEGRO)
    pantalla.blit(txt_jug, (1330, 550))
    pantalla.blit(txt_jug_lvl, (1710, 550))

    pygame.draw.rect(pantalla, GRIS_OSCURO, (1450, 600, 320, 18), border_radius=6)
    ancho_hp_p = int(320 * (combate.p_hp / combate.p_hp_max))
    color_hp_p = VERDE_BOTON
    if combate.p_hp / combate.p_hp_max <= 0.5:
        color_hp_p = AMARILLO_ALERTA
    if combate.p_hp / combate.p_hp_max <= 0.2:
        color_hp_p = ROJO_ALERTA
    pygame.draw.rect(pantalla, color_hp_p, (1450, 600, max(0, ancho_hp_p), 18), border_radius=6)

    txt_hp_num = FUENTE_CHICA.render(f"{combate.p_hp} / {combate.p_hp_max}", True, NEGRO)
    pantalla.blit(txt_hp_num, (1610, 630))

    pygame.draw.rect(pantalla, (20, 20, 30), (96, 796, 1728, 228), border_radius=16)
    pygame.draw.rect(pantalla, NEGRO, (100, 800, 1720, 220), border_radius=14)
    pygame.draw.rect(pantalla, GRIS_CLARO, (110, 810, 1700, 200), border_radius=10)
    txt_msj = FUENTE.render(combate.mensaje, True, NEGRO)
    pantalla.blit(txt_msj, (140, 880))

    if combate.turno == "jugador" and combate.sub_menu == "principal":
        pygame.draw.rect(pantalla, ROJO_BOTON, (1200, 830, 280, 75), border_radius=12)
        pygame.draw.rect(pantalla, NEGRO, (1200, 830, 280, 75), 3, border_radius=12)
        pantalla.blit(FUENTE_GRANDE.render("LUCHAR", True, BLANCO), (1265, 845))

        pygame.draw.rect(pantalla, VERDE_BOTON, (1510, 830, 280, 75), border_radius=12)
        pygame.draw.rect(pantalla, NEGRO, (1510, 830, 280, 75), 3, border_radius=12)
        txt_cambio = "CAMBIAR" if combate.modo == "3v3" else "POKÉMON"
        pantalla.blit(FUENTE_GRANDE.render(txt_cambio, True, BLANCO), (1570, 845))

    elif combate.turno == "jugador" and combate.sub_menu == "luchar":
        habilidades = combate.p_data["habilidades"]
        for idx, hab in enumerate(habilidades):
            nombre_h, pot, tipo_h = hab
            bx = 1200 if idx % 2 == 0 else 1510
            by = 830 if idx < 2 else 920
            pygame.draw.rect(pantalla, combate.tema["principal"], (bx, by, 280, 75), border_radius=12)
            pygame.draw.rect(pantalla, NEGRO, (bx, by, 280, 75), 3, border_radius=12)
            txt_h = FUENTE.render(nombre_h, True, BLANCO)
            pantalla.blit(txt_h, (bx + 25, by + 22))

    elif combate.turno == "jugador" and combate.sub_menu == "cambiar":
        for idx, p_eq in enumerate(combate.eq_jugador):
            bx = 1200 + (idx * 200)
            by = 860
            hp_actual_poke = combate.hp_jugador[p_eq]
            col_sel = AZUL_BOTON if hp_actual_poke > 0 else (120, 120, 120)
            if idx == combate.idx_activo_j:
                col_sel = GRIS_OSCURO

            pygame.draw.rect(pantalla, col_sel, (bx, by, 180, 80), border_radius=12)
            pygame.draw.rect(pantalla, NEGRO, (bx, by, 180, 80), 3, border_radius=12)
            txt_eq = FUENTE.render(p_eq[:10].capitalize(), True, BLANCO)
            pantalla.blit(txt_eq, (bx + 20, by + 25))

    elif combate.turno == "fin":
        txt_r = FUENTE_GRANDE.render("Presiona [R] para volver al Menú Principal", True, ROJO_BOTON)
        pantalla.blit(txt_r, (140, 920))


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


# ----------------- BUCLE PRINCIPAL -----------------
def main():
    estado_app = "menu_principal"
    modo_juego = "1v1"

    seleccion_idx = 0
    scroll_offset_sel = 0
    equipo_seleccionado = []

    lib_sec_idx = 0
    lib_poke_idx = 0
    lib_detalle = False
    scroll_offset_lib = 0

    reloj = pygame.time.Clock()
    ejecutando = True
    combate = None
    retraso_ia = 0

    tipo_claves = list(SECCIONES_POKEMON.keys())

    while ejecutando:
        pantalla.fill(AZUL_OSCURO)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                if estado_app == "menu_principal":
                    if evento.key == pygame.K_DOWN:
                        seleccion_idx = (seleccion_idx + 1) % 3
                    elif evento.key == pygame.K_UP:
                        seleccion_idx = (seleccion_idx - 1) % 3
                    elif evento.key == pygame.K_RETURN:
                        if seleccion_idx == 0:
                            modo_juego = "1v1"
                            estado_app = "seleccion"
                            seleccion_idx = 0
                            scroll_offset_sel = 0
                            equipo_seleccionado = []
                        elif seleccion_idx == 1:
                            modo_juego = "3v3"
                            estado_app = "seleccion"
                            seleccion_idx = 0
                            scroll_offset_sel = 0
                            equipo_seleccionado = []
                        elif seleccion_idx == 2:
                            estado_app = "biblioteca"
                            lib_sec_idx = 0
                            lib_poke_idx = 0
                            lib_detalle = False
                            scroll_offset_lib = 0

                elif estado_app == "seleccion":
                    limite = len(LISTA_PLANA_POKES)
                    if evento.key == pygame.K_DOWN:
                        seleccion_idx = (seleccion_idx + 1) % limite
                    elif evento.key == pygame.K_UP:
                        seleccion_idx = (seleccion_idx - 1) % limite
                    elif evento.key == pygame.K_RETURN:
                        poke_elegido = LISTA_PLANA_POKES[seleccion_idx]
                        if poke_elegido not in equipo_seleccionado:
                            equipo_seleccionado.append(poke_elegido)

                        meta_equipo = 1 if modo_juego == "1v1" else 3
                        if len(equipo_seleccionado) == meta_equipo:
                            estado_app = "estadisticas"

                    y_item_sel = 0
                    idx_actual = 0
                    for tipo_sec, pokes in SECCIONES_POKEMON.items():
                        y_item_sel += 45
                        for p_name in pokes:
                            if idx_actual == seleccion_idx:
                                break
                            y_item_sel += 50
                            idx_actual += 1
                        if idx_actual == seleccion_idx:
                            break
                        y_item_sel += 20

                    if y_item_sel - scroll_offset_sel > 800:
                        scroll_offset_sel = y_item_sel - 800
                    elif y_item_sel - scroll_offset_sel < 60:
                        scroll_offset_sel = max(0, y_item_sel - 60)

                elif estado_app == "estadisticas":
                    if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                        combate = Combate(equipo_seleccionado, modo_juego)
                        estado_app = "combate"

                elif estado_app == "combate":
                    if combate.turno == "jugador":
                        if combate.sub_menu == "principal":
                            if evento.key == pygame.K_1 or evento.key == pygame.K_l:
                                combate.sub_menu = "luchar"
                            elif evento.key == pygame.K_2:
                                if modo_juego == "3v3":
                                    combate.sub_menu = "cambiar"
                                else:
                                    combate.mensaje = "¡Solo tienes 1 Pokémon en 1v1!"
                        elif combate.sub_menu == "luchar":
                            if evento.key == pygame.K_1:
                                combate.ejecutar_turno(0)
                            elif evento.key == pygame.K_2:
                                combate.ejecutar_turno(1)
                            elif evento.key == pygame.K_3:
                                combate.ejecutar_turno(2)
                            elif evento.key == pygame.K_4:
                                combate.ejecutar_turno(3)
                            elif evento.key == pygame.K_ESCAPE:
                                combate.sub_menu = "principal"
                        elif combate.sub_menu == "cambiar":
                            if evento.key == pygame.K_1:
                                combate.cambiar_pokemon_jugador(0)
                            elif evento.key == pygame.K_2 and len(combate.eq_jugador) > 1:
                                combate.cambiar_pokemon_jugador(1)
                            elif evento.key == pygame.K_3 and len(combate.eq_jugador) > 2:
                                combate.cambiar_pokemon_jugador(2)
                            elif evento.key == pygame.K_ESCAPE:
                                combate.sub_menu = "principal"
                    elif combate.turno == "fin":
                        if evento.key == pygame.K_r:
                            estado_app = "menu_principal"
                            seleccion_idx = 0

                elif estado_app == "biblioteca":
                    tipo_actual = tipo_claves[lib_sec_idx]
                    pokes_actuales = SECCIONES_POKEMON[tipo_actual]

                    if lib_detalle:
                        if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                            lib_detalle = False
                    else:
                        if evento.key == pygame.K_DOWN:
                            row = lib_poke_idx // 2
                            if row < 1:
                                nuevo_idx = lib_poke_idx + 2
                                if nuevo_idx < len(pokes_actuales):
                                    lib_poke_idx = nuevo_idx
                                else:
                                    lib_poke_idx = len(pokes_actuales) - 1
                            elif row == 1:
                                if len(pokes_actuales) > 4:
                                    lib_poke_idx = 4
                                else:
                                    lib_sec_idx = (lib_sec_idx + 1) % len(tipo_claves)
                                    lib_poke_idx = 0
                            else:
                                lib_sec_idx = (lib_sec_idx + 1) % len(tipo_claves)
                                lib_poke_idx = 0

                        elif evento.key == pygame.K_UP:
                            row = lib_poke_idx // 2
                            if row > 0:
                                lib_poke_idx -= 2
                            else:
                                lib_sec_idx = (lib_sec_idx - 1) % len(tipo_claves)
                                prev_pokes = SECCIONES_POKEMON[tipo_claves[lib_sec_idx]]
                                lib_poke_idx = len(prev_pokes) - 1

                        elif evento.key == pygame.K_RIGHT:
                            col = lib_poke_idx % 2
                            if col == 0 and lib_poke_idx + 1 < len(pokes_actuales):
                                lib_poke_idx += 1

                        elif evento.key == pygame.K_LEFT:
                            col = lib_poke_idx % 2
                            if col == 1:
                                lib_poke_idx -= 1

                        elif evento.key == pygame.K_RETURN:
                            lib_detalle = True
                        elif evento.key == pygame.K_ESCAPE:
                            estado_app = "menu_principal"

                        y_tarjeta = lib_sec_idx * 700 + 50 + (lib_poke_idx // 2) * 190
                        if y_tarjeta - scroll_offset_lib > 700:
                            scroll_offset_lib = y_tarjeta - 700
                        elif y_tarjeta - scroll_offset_lib < 80:
                            scroll_offset_lib = max(0, y_tarjeta - 80)

        # ================= RENDERIZADO VISUAL RESPONSIVO =================
        if estado_app == "menu_principal":
            pantalla.fill((20, 35, 60))
            pygame.draw.rect(pantalla, AZUL_DS, (610, 240, 700, 600), border_radius=20)
            pygame.draw.rect(pantalla, BLANCO, (610, 240, 700, 600), 6, border_radius=20)

            titulo = FUENTE_GRANDE.render("POKÉMON AÑIL - DUELO", True, BLANCO)
            pantalla.blit(titulo, (720, 300))

            opciones = ["Modo 1v1", "Modo 3v3", "Biblioteca de Pokémon"]
            for idx, op in enumerate(opciones):
                color_op = (255, 230, 50) if seleccion_idx == idx else BLANCO
                pref = "▶ " if seleccion_idx == idx else "   "
                txt = FUENTE.render(f"{pref}{op}", True, color_op)
                pantalla.blit(txt, (750, 440 + (idx * 80)))

            sub_inf = FUENTE_CHICA.render("Usa Flechas ARRIBA/ABAJO y ENTER para seleccionar", True, (200, 220, 240))
            pantalla.blit(sub_inf, (710, 750))

        elif estado_app == "seleccion":
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

            ruta_img = f"assets/pokemons/frente/{poke_actual}.png"
            if os.path.exists(ruta_img):
                img_f = pygame.image.load(ruta_img).convert_alpha()
                img_f = pygame.transform.scale(img_f, (600, 600))
                pantalla.blit(img_f, (1040, 200))

            t_name_prev = FUENTE_GRANDE.render(poke_actual.upper(), True, BLANCO)
            pantalla.blit(t_name_prev, (880, 130))

        elif estado_app == "estadisticas":
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

                ruta_img = f"assets/pokemons/frente/{p_elec}.png"
                if os.path.exists(ruta_img):
                    img_f = pygame.image.load(ruta_img).convert_alpha()
                    img_f = pygame.transform.scale(img_f, (250, 250))
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

        elif estado_app == "combate":
            if combate.turno == "ia":
                retraso_ia += 1
                if retraso_ia > 60:
                    combate.turno_ia()
                    retraso_ia = 0
            dibujar_interfaz_combate(pantalla, combate)

        elif estado_app == "biblioteca":
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

                        ruta_c = f"assets/pokemons/frente/{poke_name}.png"
                        if os.path.exists(ruta_c):
                            img_c = pygame.image.load(ruta_c).convert_alpha()
                            img_c = pygame.transform.scale(img_c, (140, 140))
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

                ruta_lib = f"assets/pokemons/frente/{poke_sel}.png"
                if os.path.exists(ruta_lib):
                    img_lib = pygame.image.load(ruta_lib).convert_alpha()
                    img_lib = pygame.transform.scale(img_lib, (320, 320))
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

        # Volcar la superficie virtual escalada en la pantalla real del monitor
        pantalla_real.blit(pygame.transform.smoothscale(pantalla, (ANCHO_REAL, ALTO_REAL)), (0, 0))
        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()