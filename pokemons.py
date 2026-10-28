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
