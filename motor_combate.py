import random

from pokemons import CATALOGO_POKEMONS, LISTA_PLANA_POKES


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

        # Sucesos para que la interfaz los anime, ej: ("daño", "ia", 30)
        self.eventos = []

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

            self.eventos.append(("daño", "ia", daño, mult))

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

            self.eventos.append(("daño", "jugador", daño, mult))

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