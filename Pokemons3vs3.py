
import random

pokemones = {
    "El Musc": {
        "tipos": ["Bicho", "Volador"],
        "hp": 70,
        "ataque": 75,
        "defensa": 65,
    },
    "Neuromusc": {
        "tipos": ["Bicho", "Psíquico"],
        "hp": 65,
        "ataque": 70,
        "defensa": 60,
    },
    "Pingüinardo": {
        "tipos": ["Agua", "Hielo"],
        "hp": 85,
        "ataque": 65,
        "defensa": 80,
    },
    "Charmander": {
        "tipos": ["Fuego"],
        "hp": 70,
        "ataque": 80,
        "defensa": 55,
    },
    "Pikachu": {
        "tipos": ["Eléctrico"],
        "hp": 60,
        "ataque": 85,
        "defensa": 50,
    },
    "Bulbasaur": {
        "tipos": ["Planta", "Veneno"],
        "hp": 75,
        "ataque": 65,
        "defensa": 65,
    },
    "Topomont": {
        "tipos": ["Tierra"],
        "hp": 70,
        "ataque": 80,
        "defensa": 60,
    },
    "El Coñaseador": {
        "tipos": ["Lucha"],
        "hp": 75,
        "ataque": 85,
        "defensa": 70,
    },
}

efectividades = {
    "Fuego": {"Planta": 2.0, "Bicho": 2.0, "Hielo": 2.0, "Agua": 0.5, "Fuego": 0.5},
    "Agua": {"Fuego": 2.0, "Tierra": 2.0, "Planta": 0.5, "Agua": 0.5, "Hielo": 0.5},
    "Planta": {"Agua": 2.0, "Tierra": 2.0, "Fuego": 0.5, "Planta": 0.5, "Veneno": 0.5, "Bicho": 0.5, "Volador": 0.5},
    "Eléctrico": {"Agua": 2.0, "Volador": 2.0, "Planta": 0.5, "Eléctrico": 0.5, "Tierra": 0.0},
    "Hielo": {"Planta": 2.0, "Volador": 2.0, "Tierra": 2.0, "Fuego": 0.5, "Agua": 0.5, "Hielo": 0.5},
    "Lucha": {"Hielo": 2.0, "Psíquico": 0.5, "Volador": 0.5},
    "Tierra": {"Fuego": 2.0, "Eléctrico": 2.0, "Planta": 0.5, "Bicho": 0.5},
    "Bicho": {"Planta": 2.0, "Fuego": 0.5, "Lucha": 0.5, "Volador": 0.5, "Psíquico": 1.0},
    "Volador": {"Planta": 2.0, "Bicho": 2.0, "Lucha": 2.0, "Eléctrico": 0.5},
    "Psíquico": {"Lucha": 2.0, "Veneno": 2.0},
    "Veneno": {"Planta": 2.0}
}

def calcular_multiplicador(tipo_ataque, tipos_defensor):
    multiplicador = 1.0
    if tipo_ataque in efectividades:
        for t_def in tipos_defensor:
            if t_def in efectividades[tipo_ataque]:
                multiplicador *= efectividades[tipo_ataque][t_def]
    return multiplicador

def simular_turno(atacante_nombre, defensor_nombre, hp_defensor):
    atacante = pokemones[atacante_nombre]
    defensor = pokemones[defensor_nombre]
    
    tipo_ataque = atacante["tipos"][0]
    mult = calcular_multiplicador(tipo_ataque, defensor["tipos"])
    
    daño_base = (atacante["ataque"] / defensor["defensa"]) * 10
    daño_final = int(daño_base * mult * random.uniform(0.9, 1.1))
    daño_final = max(1, daño_final)
    
    hp_restante = max(0, hp_defensor - daño_final)
    
    print(f"{atacante_nombre} ataca a {defensor_nombre} con tipo {tipo_ataque}.")
    if mult > 1.0:
        print("Es un golpe super eficaz.")
    elif 0.0 < mult < 1.0:
        print("No es muy efectivo.")
    elif mult == 0.0:
        print("No le afecta en absoluto.")
        
    print(f"Causa {daño_final} de daño. ({defensor_nombre} HP: {hp_defensor} -> {hp_restante})\n")
    return hp_restante

def seleccionar_equipo_jugador():
    nombres_disponibles = list(pokemones.keys())
    equipo = []
    
    print("SELECCIONA TU EQUIPO DE 3 POKEMONES\n")
    
    while len(equipo) < 3:
        for i, nombre in enumerate(nombres_disponibles, 1):
            print(f"{i}. {nombre} (Tipos: {', '.join(pokemones[nombre]['tipos'])})")
        
        opcion = input(f"Elige el numero del pokemon {len(equipo) + 1}/3: ")
        if opcion.isdigit():
            idx = int(opcion) - 1
            if 0 <= idx < len(nombres_disponibles):
                seleccionado = nombres_disponibles.pop(idx)
                equipo.append(seleccionado)
                print(f"Has añadido a {seleccionado} a tu equipo.\n")
                continue
        print("Opcion invalida o repetida. Intenta de nuevo.\n")
        
    return equipo

def iniciar_combate_3vs3():
    equipo_jugador = seleccionar_equipo_jugador()
    
    nombres_disponibles = [nombre for nombre in pokemones.keys() if nombre not in equipo_jugador]
    equipo_bot = random.sample(nombres_disponibles, 3)
    
    print("========================================")
    print("EQUIPOS ENFRENTADOS")
    print(f"Tu equipo: {', '.join(equipo_jugador)}")
    print(f"Equipo del bot: {', '.join(equipo_bot)}")
    print("========================================\n")
    
    hp_jugador_equipo = {p: pokemones[p]["hp"] for p in equipo_jugador}
    hp_bot_equipo = {p: pokemones[p]["hp"] for p in equipo_bot}
    
    idx_j = 0
    idx_b = 0
    
    pokemon_activo_j = equipo_jugador[idx_j]
    pokemon_activo_b = equipo_bot[idx_b]
    
    print(f"Sales al combate con {pokemon_activo_j}!")
    print(f"El bot saca a {pokemon_activo_b}!\n")
    
    turno = 1
    while idx_j < len(equipo_jugador) and idx_b < len(equipo_bot):
        print(f"Turno {turno}")
        
        hp_b = hp_bot_equipo[pokemon_activo_b]
        hp_j = hp_jugador_equipo[pokemon_activo_j]
        
        hp_b = simular_turno(pokemon_activo_j, pokemon_activo_b, hp_b)
        hp_bot_equipo[pokemon_activo_b] = hp_b
        
        if hp_b == 0:
            print(f"El pokemon {pokemon_activo_b} del bot ha sido derrotado.\n")
            idx_b += 1
            if idx_b < len(equipo_bot):
                pokemon_activo_b = equipo_bot[idx_b]
                print(f"El bot saca a su siguiente pokemon: {pokemon_activo_b}!\n")
            else:
                print("¡Has derrotado a todo el equipo del bot! ¡Has ganado la batalla!")
                break
            turno += 1
            continue
            
        hp_j = simular_turno(pokemon_activo_b, pokemon_activo_j, hp_j)
        hp_jugador_equipo[pokemon_activo_j] = hp_j
        
        if hp_j == 0:
            print(f"Tu pokemon {pokemon_activo_j} ha sido derrotado.\n")
            idx_j += 1
            if idx_j < len(equipo_jugador):
                pokemon_activo_j = equipo_jugador[idx_j]
                print(f"Sales al combate con tu siguiente pokemon: {pokemon_activo_j}!\n")
            else:
                print("¡Todos tus pokemones han caído! El bot ha ganado la batalla.")
                break
                
        turno += 1

if __name__ == "__main__":
    iniciar_combate_3vs3()