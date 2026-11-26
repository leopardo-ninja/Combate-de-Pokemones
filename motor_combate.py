# ===== TEMA: Modularidad (Clase 10) =====
# Se importa random y datos del módulo pokemons
import random

from pokemons import CATALOGO_POKEMONS, LISTA_PLANA_POKES


# ===== TEMA: Funciones (Clase 7) + Algoritmos: pre y post condiciones (Clase 2) =====
# Entrada: dos tipos. Salida (post-condición): 0.0, 0.5, 1.0 o 2.0
# Devuelve cuánto se multiplica el daño según el tipo del ataque y el del defensor:
# 0.0 = no afecta, 2.0 = muy eficaz, 0.5 = poco eficaz, 1.0 = daño normal
def calcular_multiplicador(tipo_ataque, tipo_defensor):
    # Caso especial: los de tipo Tierra son inmunes a los ataques Eléctricos
    if tipo_ataque == "Eléctrico" and tipo_defensor == "Tierra":
        return 0.0
    # ===== TEMA: Diccionarios (Clase 11) =====
    # Diccionario tipo -> lista de tipos contra los que es eficaz
    # Cada tipo atacante -> lista de tipos contra los que es muy eficaz
    tablas_ventajas = {
        "Fuego": ["Planta"],
        "Agua": ["Fuego", "Tierra"],
        "Planta": ["Agua", "Tierra"],
        "Eléctrico": ["Agua"],
        "Tierra": ["Fuego", "Eléctrico"],
    }
    # ===== TEMA: Condicionales (Clase 4) + Expresiones y operadores (Clase 3) =====
    # Operadores and e in sobre un diccionario y una lista
    # El ataque tiene ventaja sobre el defensor: daño doble
    if tipo_ataque in tablas_ventajas and tipo_defensor in tablas_ventajas[tipo_ataque]:
        return 2.0
    # ===== TEMA: Bucles (Clase 4) + Diccionarios (Clase 11) =====
    # for con .items() recorre el diccionario
    # Desventaja: si el defensor tendría ventaja sobre este tipo de ataque, el golpe es poco eficaz
    for atacante, defensores in tablas_ventajas.items():
        if tipo_defensor == atacante and tipo_ataque in defensores:
            return 0.5
    # Cualquier otra combinación hace daño normal
    return 1.0


# ===== TEMA: Expresiones y operadores (Clase 3) =====
# Constantes numéricas que equilibran el juego
# ----------------- AJUSTES DEL DAÑO (se pueden cambiar para equilibrar el juego) -----------------
FACTOR_DAÑO = 0.30   # Multiplicador general: más alto = combates más cortos
TOPE_DAÑO = 0.40     # Ningún golpe quita más de este % de la vida máxima del rival (evita one-shots)
BONO_STAB = 1.5      # Bono si la habilidad es del mismo tipo que el Pokémon que la usa

# ----------------- PP: USOS DE CADA HABILIDAD (se pueden cambiar para equilibrar el juego) -----------------
# ===== TEMA: Expresiones y operadores (Clase 3) =====
# Constantes numéricas: cuántos usos por combate tiene cada tipo de habilidad y desde qué potencia cuenta como media o fuerte
PP_ESTADO = 3          # Habilidades de Estado (ahora son el Escudo): pocos usos
PP_BASICO = 15         # Ataques sencillos (potencia baja)
PP_MEDIO = 8           # Ataques intermedios
POTENCIA_MEDIA = 55    # Desde esta potencia el ataque cuenta como medio
POTENCIA_FUERTE = 100  # Desde esta potencia el ataque cuenta como fuerte (el fuerte NO usa PP: usa energía)

# ----------------- ENERGÍA: la habilidad fuerte hay que cargarla (como en Pokémon GO) -----------------
# ===== TEMA: Expresiones y operadores (Clase 3) =====
# Cada Pokémon empieza con 0 de energía. Atacar y recibir golpes la carga; la habilidad fuerte gasta COSTO_FUERTE
ENERGIA_MAX = 100          # Energía máxima que se puede guardar
COSTO_FUERTE = 100         # Energía que gasta la habilidad fuerte (se gasta aunque falle)
ENERGIA_POR_ATAQUE = 25    # Energía que gana el Pokémon que usa un ataque que no es el fuerte
ENERGIA_POR_GOLPE = 10     # Energía que gana el Pokémon que recibe daño

# ----------------- PRECISIÓN Y ESQUIVA (porcentajes de acierto) -----------------
# ===== TEMA: Expresiones y operadores (Clase 3) =====
# Porcentaje base de acierto según el tipo de habilidad. Cuanto más fuerte, más fácil de fallar
PRECISION_BASICO = 95
PRECISION_MEDIO = 90
PRECISION_FUERTE = 80
PRECISION_ESTADO = 100
ESQUIVA_POR_VELOCIDAD = 0.15   # Puntos de esquiva por cada punto de velocidad que el defensor le saca al atacante
ESQUIVA_MAX = 15               # Tope de esquiva por velocidad (en puntos porcentuales)

# ----------------- ESCUDO (las habilidades de Estado) -----------------
# ===== TEMA: Expresiones y operadores (Clase 3) =====
# El Escudo bloquea el siguiente ataque que reciba el Pokémon y lo cura un poco, más si está en estado crítico
ESCUDO_CURA = 0.10            # Cura normal: % de la vida máxima
ESCUDO_CURA_CRITICO = 0.25    # Cura si está en estado crítico: % de la vida máxima
UMBRAL_CRITICO = 0.30         # Estado crítico: vida por debajo de este % de la vida máxima
IA_UMBRAL_ESCUDO = 0.50       # El rival solo usa el Escudo cuando le queda este % de vida o menos
IA_PROB_FUERTE = 0.60         # Probabilidad de que el rival use la habilidad fuerte cuando la tiene cargada

# ===== TEMA: Tuplas (Clase 11) =====
# Habilidad de emergencia: igual que las demás es una tupla (nombre, potencia, tipo). No tiene PP y se usa cuando no queda ninguna opción
FORCEJEO = ("Forcejeo", 50, "Normal")


# ===== TEMA: Funciones (Clase 7) + Algoritmos: pre y post condiciones (Clase 2) =====
# Entrada: la tupla de una habilidad. Salida (post-condición): True solo si es un ataque (no de Estado) con potencia desde POTENCIA_FUERTE
# Dice si una habilidad es la "fuerte" (la que gasta energía en vez de PP)
def es_fuerte(habilidad):
    nombre_habilidad, potencia, tipo_habilidad = habilidad
    return tipo_habilidad != "Estado" and potencia >= POTENCIA_FUERTE


# ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) + Algoritmos: pre y post condiciones (Clase 2) =====
# Entrada: la tupla de una habilidad. Salida (post-condición): un entero >= 0 (0 para la fuerte, que usa energía); los if con return van de la más específica a la más general
# Devuelve los PP (usos por combate) de una habilidad según su tipo y su potencia
def calcular_pp(habilidad):
    nombre_habilidad, potencia, tipo_habilidad = habilidad
    # Las de Estado tienen potencia 0, por eso se revisan primero
    if tipo_habilidad == "Estado":
        return PP_ESTADO
    if potencia >= POTENCIA_FUERTE:
        return 0
    if potencia >= POTENCIA_MEDIA:
        return PP_MEDIO
    return PP_BASICO


# ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) + Algoritmos: pre y post condiciones (Clase 2) =====
# Entrada: la tupla de una habilidad. Salida (post-condición): un porcentaje entre 0 y 100
# Devuelve el porcentaje base de acierto de una habilidad según su tipo y su potencia
def calcular_precision(habilidad):
    nombre_habilidad, potencia, tipo_habilidad = habilidad
    if tipo_habilidad == "Estado":
        return PRECISION_ESTADO
    if potencia >= POTENCIA_FUERTE:
        return PRECISION_FUERTE
    if potencia >= POTENCIA_MEDIA:
        return PRECISION_MEDIO
    return PRECISION_BASICO


# ===== TEMA: Funciones (Clase 7) + Tuplas (Clase 11) + Diccionarios (Clase 11) =====
# Retorna dos valores como tupla: (probabilidad de acierto, puntos de esquiva). La esquiva solo aparece si el defensor es más rápido
# Probabilidad final = precisión de la habilidad - esquiva por velocidad (un defensor veloz esquiva más)
def calcular_prob_acierto(atacante, defensor, habilidad):
    precision = calcular_precision(habilidad)
    # Diferencia de velocidad a favor del defensor; max() evita que sea negativa y min() la limita al tope
    ventaja_defensor = (defensor["velocidad"] - atacante["velocidad"]) * ESQUIVA_POR_VELOCIDAD
    esquiva = min(max(ventaja_defensor, 0), ESQUIVA_MAX)
    return precision - esquiva, esquiva


# ===== TEMA: Funciones (Clase 7) + Tuplas (Clase 11) =====
# Desempaqueta la tupla habilidad; retorna dos valores (daño, multiplicador) como tupla
# Calcula el daño de una habilidad. La usan tanto el jugador como la IA, así el cálculo está solo aquí
# atacante y defensor son los diccionarios de datos del catálogo; habilidad es (nombre, potencia, tipo)
# Devuelve (daño, multiplicador de tipos)
def calcular_daño(atacante, defensor, habilidad):
    nombre_habilidad, potencia, tipo_habilidad = habilidad

    # ===== TEMA: Condicionales (Clase 4) =====
    # return anticipado: si es de Estado el daño es 0
    # Las habilidades de Estado no hacen daño
    if tipo_habilidad == "Estado":
        return 0, 1.0

    multiplicador = calcular_multiplicador(tipo_habilidad, defensor["tipo"])

    # ===== TEMA: Condicionales (Clase 4) + Diccionarios (Clase 11) =====
    # if/else; max() compara estadísticas guardadas en diccionarios
    # Las Normales usan ataque/defensa; las elementales usan la mejor estadística ofensiva y defensiva
    if tipo_habilidad == "Normal":
        ataque = atacante["ataque"]
        defensa = defensor["defensa"]
    else:
        ataque = max(atacante["ataque"], atacante["atk_esp"])
        defensa = max(defensor["defensa"], defensor["def_esp"])

    # Bono por usar una habilidad del propio tipo
    bono = 1.0
    if tipo_habilidad == atacante["tipo"]:
        bono = BONO_STAB

    daño = int(potencia * (ataque / defensa) * FACTOR_DAÑO * multiplicador * bono)

    # ===== TEMA: Expresiones y operadores (Clase 3) =====
    # min() limita el daño; int() convierte a entero
    # Tope por golpe: un solo ataque nunca supera el % de vida máxima del rival
    daño = min(daño, int(defensor["hp"] * TOPE_DAÑO))
    return daño, multiplicador


# ===== TEMA: POO (Clase 16) =====
# Clase Combate: guarda el estado del combate (equipos, vida, turno y mensajes)
# ----------------- CLASE DE COMBATE -----------------
# Guarda todo el estado del combate (equipos, vida, turno y mensajes). No dibuja nada: de eso se encarga la interfaz
class Combate:
    # ===== TEMA: POO (Clase 16) =====
    # Constructor: crea los atributos de la clase Combate
    def __init__(self, equipo_jugador, modo):
        # modo es "1v1" o "3v3"
        self.modo = modo
        # Equipo del jugador y posición (índice) del Pokémon que está combatiendo ahora
        self.equipo_jugador = list(equipo_jugador)
        self.idx_activo_jugador = 0

        # ===== TEMA: Listas (Clase 11) =====
        # Lista por comprensión con filtro (not in) y random.sample
        # El rival recibe un equipo aleatorio del mismo tamaño, sin repetir pokémons del jugador
        pool_disponible = [nombre_pokemon for nombre_pokemon in LISTA_PLANA_POKES if nombre_pokemon not in self.equipo_jugador]
        self.equipo_ia = random.sample(pool_disponible, len(self.equipo_jugador))
        self.idx_activo_ia = 0

        # ===== TEMA: Diccionarios (Clase 11) =====
        # Diccionarios nombre -> vida, construidos desde el catálogo
        # Vida actual de cada Pokémon de ambos equipos (nombre -> vida). Empiezan con la vida máxima
        self.hp_jugador = {nombre_pokemon: CATALOGO_POKEMONS[nombre_pokemon]["hp"] for nombre_pokemon in self.equipo_jugador}
        self.hp_ia = {nombre_pokemon: CATALOGO_POKEMONS[nombre_pokemon]["hp"] for nombre_pokemon in self.equipo_ia}

        # ===== TEMA: Diccionarios (Clase 11) + Listas (Clase 11) =====
        # Diccionario nombre -> lista con los PP que le quedan a cada habilidad (misma posición que en su lista 'habilidades'); se crea con comprensiones
        # PP restantes de cada habilidad de cada Pokémon. Empiezan con los PP máximos y se van gastando
        self.pp_jugador = {nombre_pokemon: [calcular_pp(habilidad) for habilidad in CATALOGO_POKEMONS[nombre_pokemon]["habilidades"]] for nombre_pokemon in self.equipo_jugador}
        self.pp_ia = {nombre_pokemon: [calcular_pp(habilidad) for habilidad in CATALOGO_POKEMONS[nombre_pokemon]["habilidades"]] for nombre_pokemon in self.equipo_ia}

        # ===== TEMA: Diccionarios (Clase 11) =====
        # Diccionarios anidados: bando -> (nombre del Pokémon -> valor). Se consultan así: self.energia["jugador"][nombre]
        # Energía acumulada de cada Pokémon (empieza en 0) y si tiene el Escudo activo (empieza en False)
        self.energia = {
            "jugador": {nombre_pokemon: 0 for nombre_pokemon in self.equipo_jugador},
            "ia": {nombre_pokemon: 0 for nombre_pokemon in self.equipo_ia},
        }
        self.escudo = {
            "jugador": {nombre_pokemon: False for nombre_pokemon in self.equipo_jugador},
            "ia": {nombre_pokemon: False for nombre_pokemon in self.equipo_ia},
        }

        # ===== TEMA: Listas (Clase 11) + Tuplas (Clase 11) =====
        # Lista de tuplas que se va llenando con append
        # Sucesos para que la interfaz los anime, ej: ("daño", "ia", 30)
        self.eventos = []

        # Carga nombre, datos y vida de los dos pokémons que combaten
        self.cargar_pokemons_activos()
        # turno: "jugador", "ia" o "fin"
        # sub_menu: menú que se muestra en combate ("principal", "luchar" o "cambiar")
        self.turno = "jugador"
        self.sub_menu = "principal"
        self.mensaje = f"¡El rival envió a {self.nombre_ia.capitalize()}!"

    # ===== TEMA: POO (Clase 16) + Diccionarios (Clase 11) =====
    # Método que actualiza datos del propio objeto (self)
    # Guarda en los diccionarios de vida la vida actual de los dos pokémons activos
    def actualizar_hp_actual(self):
        self.hp_jugador[self.nombre_jugador] = self.hp_actual_jugador
        self.hp_ia[self.nombre_ia] = self.hp_actual_ia

    # ===== TEMA: Diccionarios (Clase 11) =====
    # Indexación de diccionarios anidados: CATALOGO_POKEMONS[nombre]['hp']
    # Copia a atributos cómodos (nombre, datos, vida y vida máxima) los pokémons activos de cada bando
    def cargar_pokemons_activos(self):
        self.nombre_jugador = self.equipo_jugador[self.idx_activo_jugador]
        self.datos_jugador = CATALOGO_POKEMONS[self.nombre_jugador]
        self.hp_max_jugador = self.datos_jugador["hp"]
        self.hp_actual_jugador = self.hp_jugador[self.nombre_jugador]

        self.nombre_ia = self.equipo_ia[self.idx_activo_ia]
        self.datos_ia = CATALOGO_POKEMONS[self.nombre_ia]
        self.hp_max_ia = self.datos_ia["hp"]
        self.hp_actual_ia = self.hp_ia[self.nombre_ia]

    # ===== TEMA: Funciones (Clase 7) + Tuplas (Clase 11) =====
    # Retorna una tupla con los datos de un bando: (nombre del Pokémon activo, sus datos, su lista de PP, su energía actual)
    # Evita repetir if/else del jugador y la IA en cada método
    def recursos_de(self, bando):
        if bando == "jugador":
            return self.nombre_jugador, self.datos_jugador, self.pp_jugador[self.nombre_jugador], self.energia["jugador"][self.nombre_jugador]
        return self.nombre_ia, self.datos_ia, self.pp_ia[self.nombre_ia], self.energia["ia"][self.nombre_ia]

    # ===== TEMA: Listas (Clase 11) + Bucles (Clase 4) + Condicionales (Clase 4) =====
    # Retorna una lista de índices (posiciones en la lista de 4 habilidades); for + range, append y varias condiciones
    # Índices de las habilidades que el bando puede usar ahora: con PP, la fuerte con energía suficiente y el Escudo solo si no lo tiene ya activo
    def indices_usables(self, bando):
        nombre, datos, pp, energia = self.recursos_de(bando)
        usables = []
        for indice in range(len(datos["habilidades"])):
            habilidad = datos["habilidades"][indice]
            if es_fuerte(habilidad):
                if energia >= COSTO_FUERTE:
                    usables.append(indice)
            elif habilidad[2] == "Estado":
                if pp[indice] > 0 and not self.escudo[bando][nombre]:
                    usables.append(indice)
            elif pp[indice] > 0:
                usables.append(indice)
        return usables

    # ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) + Listas (Clase 11) =====
    # Retorna la tupla de la habilidad, FORCEJEO si no se puede usar ninguna o None si esa habilidad no está disponible
    # Decide qué habilidad usa el jugador (indice_habilidad es su posición en la lista de 4 habilidades)
    def habilidad_para_jugador(self, indice_habilidad):
        usables = self.indices_usables("jugador")
        # Sin ninguna opción se usa Forcejeo, así el combate nunca se queda trabado
        if not usables:
            return FORCEJEO
        # Esa habilidad se puede usar: se devuelve su tupla (nombre, potencia, tipo)
        if indice_habilidad in usables:
            return self.datos_jugador["habilidades"][indice_habilidad]
        # No está disponible (sin PP, sin energía o ya hay escudo)
        return None

    # ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) =====
    # Retorna el texto que explica por qué el jugador no puede usar esa habilidad (la interfaz lo muestra en la barra de mensajes)
    def mensaje_no_disponible(self, indice_habilidad):
        habilidad = self.datos_jugador["habilidades"][indice_habilidad]
        if es_fuerte(habilidad):
            energia = self.energia["jugador"][self.nombre_jugador]
            return f"¡{habilidad[0]} necesita {COSTO_FUERTE} de energía! Tienes {energia}."
        if habilidad[2] == "Estado" and self.escudo["jugador"][self.nombre_jugador]:
            return f"¡{self.nombre_jugador.capitalize()} ya tiene el escudo activo!"
        return f"¡No quedan PP en {habilidad[0]}!"

    # ===== TEMA: Listas (Clase 11) + Funciones (Clase 7) =====
    # Lista con las habilidades usables; random.choice elige una. El rival prioriza la fuerte cuando la tiene cargada y solo usa el Escudo con poca vida
    # El rival elige entre las habilidades que puede usar (Forcejeo si no puede ninguna)
    def elegir_habilidad_ia(self):
        usables = self.indices_usables("ia")
        if not usables:
            return FORCEJEO
        habilidades = self.datos_ia["habilidades"]
        opciones = []
        for indice in usables:
            habilidad = habilidades[indice]
            if habilidad[2] == "Estado":
                # El Escudo solo tiene sentido con la vida baja
                if self.hp_actual_ia <= self.hp_max_ia * IA_UMBRAL_ESCUDO:
                    opciones.append(habilidad)
            else:
                opciones.append(habilidad)
        # Si el filtro dejó la lista vacía (solo quedaba el Escudo), se usa lo que haya
        if not opciones:
            opciones = [habilidades[indice] for indice in usables]
        # Con la fuerte cargada la usa casi siempre (no siempre, para no ser predecible)
        fuertes = [habilidad for habilidad in opciones if es_fuerte(habilidad)]
        if fuertes and random.random() < IA_PROB_FUERTE:
            return random.choice(fuertes)
        return random.choice(opciones)

    # ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) + Diccionarios (Clase 11) =====
    # Aplica una habilidad de "bando" ("jugador" o "ia") sobre el otro: PP o energía, escudo, acierto, daño y mensajes.
    # La usan ejecutar_turno y turno_ia, así esta lógica está solo aquí. No cambia el turno: de eso se encargan ellas
    def aplicar_habilidad(self, bando, habilidad):
        nombre_habilidad, potencia, tipo_habilidad = habilidad

        # Quién ataca y quién defiende (datos, nombres, vida y cómo se nombran en los mensajes)
        if bando == "jugador":
            rival = "ia"
            atacante, defensor = self.datos_jugador, self.datos_ia
            nombre_atacante, nombre_defensor = self.nombre_jugador, self.nombre_ia
            hp_atacante, hp_defensor = self.hp_actual_jugador, self.hp_actual_ia
            etiqueta_atacante = nombre_atacante.capitalize()
            etiqueta_defensor = f"{nombre_defensor.capitalize()} rival"
        else:
            rival = "jugador"
            atacante, defensor = self.datos_ia, self.datos_jugador
            nombre_atacante, nombre_defensor = self.nombre_ia, self.nombre_jugador
            hp_atacante, hp_defensor = self.hp_actual_ia, self.hp_actual_jugador
            etiqueta_atacante = f"{nombre_atacante.capitalize()} rival"
            etiqueta_defensor = nombre_defensor.capitalize()

        # ===== TEMA: Listas (Clase 11) + Condicionales (Clase 4) =====
        # .index() busca la posición de la habilidad y se le resta 1 PP. La fuerte (energía) y Forcejeo (no está en la lista) no gastan PP
        if habilidad in atacante["habilidades"] and not es_fuerte(habilidad):
            posicion = atacante["habilidades"].index(habilidad)
            pp = self.pp_jugador[nombre_atacante] if bando == "jugador" else self.pp_ia[nombre_atacante]
            pp[posicion] = max(0, pp[posicion] - 1)

        # ===== TEMA: Condicionales (Clase 4) + Expresiones y operadores (Clase 3) =====
        # Habilidad de Estado = Escudo: bloquea el siguiente ataque recibido y cura (más si está en estado crítico)
        if tipo_habilidad == "Estado":
            if hp_atacante <= atacante["hp"] * UMBRAL_CRITICO:
                cura = int(atacante["hp"] * ESCUDO_CURA_CRITICO)
            else:
                cura = int(atacante["hp"] * ESCUDO_CURA)
            # min() evita pasar de la vida máxima; la cura real puede ser menor que la calculada
            cura_real = min(cura, atacante["hp"] - hp_atacante)
            hp_atacante = hp_atacante + cura_real
            self.escudo[bando][nombre_atacante] = True
            if cura_real > 0:
                self.eventos.append(("curar", bando, cura_real, 1.0))
            self.mensaje = f"¡{etiqueta_atacante} usó {nombre_habilidad}! Se protege con un escudo y recupera {cura_real} HP."
        else:
            # ===== TEMA: Diccionarios (Clase 11) + Expresiones y operadores (Clase 3) =====
            # Energía: la fuerte gasta COSTO_FUERTE (aunque falle); cualquier otro ataque suma ENERGIA_POR_ATAQUE (con tope ENERGIA_MAX)
            if es_fuerte(habilidad):
                self.energia[bando][nombre_atacante] = max(0, self.energia[bando][nombre_atacante] - COSTO_FUERTE)
            else:
                self.energia[bando][nombre_atacante] = min(ENERGIA_MAX, self.energia[bando][nombre_atacante] + ENERGIA_POR_ATAQUE)

            # ===== TEMA: Condicionales (Clase 4) + Funciones (Clase 7) =====
            # random.random() da un número entre 0 y 1; si el "dado" (0-100) cae en o por encima de la probabilidad, el ataque falla
            prob_acierto, esquiva = calcular_prob_acierto(atacante, defensor, habilidad)
            if random.random() * 100 >= prob_acierto:
                self.eventos.append(("fallo", rival, 0, 1.0))
                if esquiva > 0:
                    self.mensaje = f"¡{etiqueta_atacante} usó {nombre_habilidad}! ¡{etiqueta_defensor} lo esquivó!"
                else:
                    self.mensaje = f"¡{etiqueta_atacante} usó {nombre_habilidad}, pero falló!"
            # Si el defensor tenía el Escudo activo, bloquea el golpe y el escudo se gasta
            elif self.escudo[rival][nombre_defensor]:
                self.escudo[rival][nombre_defensor] = False
                self.eventos.append(("escudo", rival, 0, 1.0))
                self.mensaje = f"¡{etiqueta_atacante} usó {nombre_habilidad}! ¡El escudo de {etiqueta_defensor} bloqueó el ataque!"
            else:
                # El daño depende de la potencia, las estadísticas, el tipo y el tope (ver calcular_daño). La vida nunca baja de 0
                daño, multiplicador = calcular_daño(atacante, defensor, habilidad)
                hp_defensor = max(0, hp_defensor - daño)

                # Avisa a la interfaz para que anime el daño (parpadeo, texto flotante y sonido)
                self.eventos.append(("daño", rival, daño, multiplicador))

                # Recibir un golpe también carga energía en el defensor
                if daño > 0:
                    self.energia[rival][nombre_defensor] = min(ENERGIA_MAX, self.energia[rival][nombre_defensor] + ENERGIA_POR_GOLPE)

                # ===== TEMA: Condicionales (Clase 4) =====
                # if/elif/elif con comparación de floats
                # Texto extra del mensaje según la eficacia del ataque
                info_mult = ""
                if multiplicador == 2.0:
                    info_mult = " ¡Es muy eficaz!"
                elif multiplicador == 0.5:
                    info_mult = " No es muy eficaz..."
                elif multiplicador == 0.0:
                    info_mult = " ¡No afecta!"

                self.mensaje = f"¡{etiqueta_atacante} usó {nombre_habilidad}! Hizo {daño}.{info_mult}"

        # Se devuelven a los atributos del combate las vidas que pudieron cambiar
        if bando == "jugador":
            self.hp_actual_jugador, self.hp_actual_ia = hp_atacante, hp_defensor
        else:
            self.hp_actual_ia, self.hp_actual_jugador = hp_atacante, hp_defensor
        self.actualizar_hp_actual()

    # ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) =====
    # if/else anidados; la tupla habilidad se desempaqueta
    # Ejecuta la habilidad del jugador (indice_habilidad es su posición en la lista de 4 habilidades)
    def ejecutar_turno(self, indice_habilidad):
        # ===== TEMA: Algoritmos: pre y post condiciones (Clase 2) =====
        # Pre-condición: si no es el turno del jugador, la función no hace nada (return)
        # Turno del jugador
        if self.turno != "jugador":
            return

        # ===== TEMA: Algoritmos: pre y post condiciones (Clase 2) + Condicionales (Clase 4) =====
        # Pre-condición: la habilidad debe estar disponible; si no (retorna None) la función termina y no se gasta el turno
        habilidad = self.habilidad_para_jugador(indice_habilidad)
        if habilidad is None:
            return

        # Gasta PP o energía, comprueba si acierta, el escudo del rival y aplica el daño (todo en aplicar_habilidad)
        self.aplicar_habilidad("jugador", habilidad)

        # ===== TEMA: Condicionales (Clase 4) + Listas (Clase 11) =====
        # if anidado; len() y los índices de la lista del equipo
        # Si el rival se debilita: entra el siguiente de su equipo o, si no quedan, el jugador gana
        if self.hp_actual_ia <= 0:
            if self.idx_activo_ia < len(self.equipo_ia) - 1:
                self.idx_activo_ia += 1
                self.cargar_pokemons_activos()
                self.mensaje = f"¡El rival envió a {self.nombre_ia.capitalize()}!"
                self.turno = "jugador"
                self.sub_menu = "principal"
                return
            else:
                self.mensaje = "¡Has derrotado a todos los rivales! ¡Victoria!"
                self.turno = "fin"
                return

        # Si el rival sigue en pie, le toca atacar a él
        self.turno = "ia"
        self.sub_menu = "principal"

    # ===== TEMA: Condicionales (Clase 4) =====
    # Validaciones con return anticipado (pre-condiciones)
    # Cambia el Pokémon activo del jugador por el del índice nuevo_indice (gasta el turno)
    def cambiar_pokemon_jugador(self, nuevo_indice):
        # No se puede cambiar al Pokémon que ya está combatiendo
        if nuevo_indice == self.idx_activo_jugador:
            self.mensaje = "¡Ese Pokémon ya está combatiendo!"
            self.sub_menu = "principal"
            return
        
        nuevo_nombre = self.equipo_jugador[nuevo_indice]
        # Tampoco a uno que ya está debilitado
        if self.hp_jugador[nuevo_nombre] <= 0:
            self.mensaje = f"¡{nuevo_nombre.capitalize()} está debilitado y no puede combatir!"
            self.sub_menu = "principal"
            return

        # Se guarda la vida del Pokémon que sale y se carga el nuevo. El escudo del que sale se pierde
        self.escudo["jugador"][self.nombre_jugador] = False
        self.actualizar_hp_actual()
        self.idx_activo_jugador = nuevo_indice
        self.cargar_pokemons_activos()
        self.mensaje = f"¡Adelante, {self.nombre_jugador.capitalize()}!"
        # Cambiar de Pokémon gasta el turno: ahora ataca el rival
        self.turno = "ia"
        self.sub_menu = "principal"

    # ===== TEMA: Funciones (Clase 7) =====
    # Parámetro opcional (habilidad=None): si no llega, se elige al azar
    # Turno del rival. La interfaz puede elegir la habilidad antes (para animarla); si no, se elige al azar
    def turno_ia(self, habilidad=None):
        # Turno de la ia (la interfaz puede elegir la habilidad antes, para animarla)
        if self.turno != "ia":
            return

        # Si no llegó habilidad, el rival elige una según sus PP, su energía y su vida
        if habilidad is None:
            habilidad = self.elegir_habilidad_ia()

        # Misma lógica que el jugador (PP o energía, acierto, escudo y daño), pero con el bando "ia"
        self.aplicar_habilidad("ia", habilidad)

        # ===== TEMA: Bucles (Clase 4) + Listas (Clase 11) =====
        # for/range con break: busca el primer Pokémon vivo; -1 indica que no queda ninguno
        # Si cae el Pokémon del jugador: entra el primero vivo del equipo o, si no queda ninguno, se pierde
        if self.hp_actual_jugador <= 0:
            # -1 significa que no queda ningún Pokémon vivo para reemplazarlo
            siguiente_indice = -1
            for indice in range(len(self.equipo_jugador)):
                if self.hp_jugador[self.equipo_jugador[indice]] > 0 and indice != self.idx_activo_jugador:
                    siguiente_indice = indice
                    break

            if siguiente_indice != -1:
                self.idx_activo_jugador = siguiente_indice
                self.cargar_pokemons_activos()
                self.mensaje = f"¡{self.nombre_jugador.capitalize()} entra al combate!"
                self.turno = "jugador"
            else:
                self.mensaje = "¡Tu equipo ha caído debilitado! Derrota..."
                self.turno = "fin"
        else:
            self.turno = "jugador"