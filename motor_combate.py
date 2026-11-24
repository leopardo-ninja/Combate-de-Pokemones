import random

from pokemons import CATALOGO_POKEMONS, LISTA_PLANA_POKES


# Devuelve cuánto se multiplica el daño según el tipo del ataque y el del defensor:
# 0.0 = no afecta, 2.0 = muy eficaz, 0.5 = poco eficaz, 1.0 = daño normal
def calcular_multiplicador(tipo_ataque, tipo_defensor):
    # Caso especial: los de tipo Tierra son inmunes a los ataques Eléctricos
    if tipo_ataque == "Eléctrico" and tipo_defensor == "Tierra":
        return 0.0
    # Cada tipo atacante -> lista de tipos contra los que es muy eficaz
    tablas_ventajas = {
        "Fuego": ["Planta"],
        "Agua": ["Fuego", "Tierra"],
        "Planta": ["Agua", "Tierra"],
        "Eléctrico": ["Agua"],
        "Tierra": ["Fuego", "Eléctrico"],
    }
    # El ataque tiene ventaja sobre el defensor: daño doble
    if tipo_ataque in tablas_ventajas and tipo_defensor in tablas_ventajas[tipo_ataque]:
        return 2.0
    # Desventaja: si el defensor tendría ventaja sobre este tipo de ataque, el golpe es poco eficaz
    for atacante, defensores in tablas_ventajas.items():
        if tipo_defensor == atacante and tipo_ataque in defensores:
            return 0.5
    # Cualquier otra combinación hace daño normal
    return 1.0


# ----------------- CLASE DE COMBATE -----------------
# Guarda todo el estado del combate (equipos, vida, turno y mensajes). No dibuja nada: de eso se encarga la interfaz
class Combate:
    def __init__(self, equipo_jugador, modo):
        # modo es "1v1" o "3v3"
        self.modo = modo
        # Equipo del jugador y posición (índice) del Pokémon que está combatiendo ahora
        self.equipo_jugador = list(equipo_jugador)
        self.idx_activo_jugador = 0

        # El rival recibe un equipo aleatorio del mismo tamaño, sin repetir pokémons del jugador
        pool_disponible = [nombre_pokemon for nombre_pokemon in LISTA_PLANA_POKES if nombre_pokemon not in self.equipo_jugador]
        self.equipo_ia = random.sample(pool_disponible, len(self.equipo_jugador))
        self.idx_activo_ia = 0

        # Vida actual de cada Pokémon de ambos equipos (nombre -> vida). Empiezan con la vida máxima
        self.hp_jugador = {nombre_pokemon: CATALOGO_POKEMONS[nombre_pokemon]["hp"] for nombre_pokemon in self.equipo_jugador}
        self.hp_ia = {nombre_pokemon: CATALOGO_POKEMONS[nombre_pokemon]["hp"] for nombre_pokemon in self.equipo_ia}

        # Sucesos para que la interfaz los anime, ej: ("daño", "ia", 30)
        self.eventos = []

        # Carga nombre, datos y vida de los dos pokémons que combaten
        self.cargar_pokemons_activos()
        # turno: "jugador", "ia" o "fin"
        # sub_menu: menú que se muestra en combate ("principal", "luchar" o "cambiar")
        self.turno = "jugador"
        self.sub_menu = "principal"
        self.mensaje = f"¡El rival envió a {self.nombre_ia.capitalize()}!"

    # Guarda en los diccionarios de vida la vida actual de los dos pokémons activos
    def actualizar_hp_actual(self):
        self.hp_jugador[self.nombre_jugador] = self.hp_actual_jugador
        self.hp_ia[self.nombre_ia] = self.hp_actual_ia

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

    # Ejecuta la habilidad del jugador (indice_habilidad es su posición en la lista de 4 habilidades)
    def ejecutar_turno(self, indice_habilidad):
        # Turno del jugador
        if self.turno != "jugador":
            return

        habilidad = self.datos_jugador["habilidades"][indice_habilidad]
        nombre_habilidad, potencia, tipo_habilidad = habilidad

        # Las habilidades de Estado no hacen daño, solo muestran el mensaje
        if tipo_habilidad == "Estado":
            self.mensaje = f"¡{self.nombre_jugador.capitalize()} usó {nombre_habilidad}!"
        else:
            multiplicador = calcular_multiplicador(tipo_habilidad, self.datos_ia["tipo"])
            # Daño = potencia x multiplicador de tipos. La vida nunca baja de 0
            daño = int(potencia * multiplicador)
            self.hp_actual_ia = max(0, self.hp_actual_ia - daño)

            # Avisa a la interfaz para que anime el daño (parpadeo, texto flotante y sonido)
            self.eventos.append(("daño", "ia", daño, multiplicador))

            # Texto extra del mensaje según la eficacia del ataque
            info_mult = ""
            if multiplicador == 2.0:
                info_mult = " ¡Es muy eficaz!"
            elif multiplicador == 0.5:
                info_mult = " No es muy eficaz..."
            elif multiplicador == 0.0:
                info_mult = " ¡No afecta!"

            self.mensaje = f"¡{self.nombre_jugador.capitalize()} usó {nombre_habilidad}! Hizo {daño}.{info_mult}" # Mensaje de aviso de la eficacia del ataque

        self.actualizar_hp_actual()

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

        # Se guarda la vida del Pokémon que sale y se carga el nuevo
        self.actualizar_hp_actual()
        self.idx_activo_jugador = nuevo_indice
        self.cargar_pokemons_activos()
        self.mensaje = f"¡Adelante, {self.nombre_jugador.capitalize()}!"
        # Cambiar de Pokémon gasta el turno: ahora ataca el rival
        self.turno = "ia"
        self.sub_menu = "principal"

    # Turno del rival. La interfaz puede elegir la habilidad antes (para animarla); si no, se elige al azar
    def turno_ia(self, habilidad=None):
        # Turno de la ia (la interfaz puede elegir la habilidad antes, para animarla)
        if self.turno != "ia":
            return

        # Si no llegó habilidad, el rival elige una al azar
        if habilidad is None:
            habilidad = random.choice(self.datos_ia["habilidades"])
        nombre_habilidad, potencia, tipo_habilidad = habilidad

        if tipo_habilidad == "Estado":
            self.mensaje = f"¡El rival usó {nombre_habilidad}!"
        else:
            multiplicador = calcular_multiplicador(tipo_habilidad, self.datos_jugador["tipo"])
            daño = int(potencia * multiplicador)
            self.hp_actual_jugador = max(0, self.hp_actual_jugador - daño)

            self.eventos.append(("daño", "jugador", daño, multiplicador))

            self.mensaje = f"¡{self.nombre_ia.capitalize()} rival usó {nombre_habilidad}! Hizo {daño}."    # Mensaje de aviso de la eficacia del ataque

        self.actualizar_hp_actual()

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