import random

criaturas = {
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
    atacante = criaturas[atacante_nombre]
    defensor = criaturas[defensor_nombre]
    
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

def seleccionar_criatura():
    nombres = list(criaturas.keys())
    while True:
        print("--- SELECCIONA TU CRIATURA ---")
        for i, nombre in enumerate(nombres, 1):
            print(f"{i}. {nombre} (Tipos: {', '.join(criaturas[nombre]['tipos'])})")
        
        opcion = input("Elige el numero de tu criatura: ")
        if opcion.isdigit():
            idx = int(opcion) - 1
            if 0 <= idx < len(nombres):
                seleccionado = nombres[idx]
                print(f"Has elegido a {seleccionado}.\n")
                return seleccionado
        print("Opcion invalida. Intenta de nuevo.\n")

def iniciar_combate():
    print("========================================")
    print("MODO JUGADOR VS BOT")
    print("========================================\n")
    
    # El usuario elige su criatura
    jugador = seleccionar_criatura()
    
    # El bot elige una criatura al azar de la lista
    nombres = list(criaturas.keys())
    bot = random.choice(nombres)
    
    print(f"El bot ha seleccionado a {bot}.\n")
    
    print("========================================")
    print(f"INICIA LA BATALLA: {jugador} VS {bot}")
    print("========================================\n")
    
    hp_jugador = criaturas[jugador]["hp"]
    hp_bot = criaturas[bot]["hp"]
    
    turno = 1
    while hp_jugador > 0 and hp_bot > 0:
        print(f"Turno {turno}")
        
        # Ataca el jugador
        hp_bot = simular_turno(jugador, bot, hp_bot)
        if hp_bot == 0:
            print(f"¡{jugador} ha ganado la batalla!")
            break
            
        # Ataca el bot
        hp_jugador = simular_turno(bot, jugador, hp_jugador)
        if hp_jugador == 0:
            print(f"¡{bot} ha ganado la batalla!")
            break
            
        turno += 1

if __name__ == "__main__":
    iniciar_combate()