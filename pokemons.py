# ----------------- BASE DE DATOS DE LOS 81 POKÉMON -----------------


# ===== TEMA: Diccionarios (Clase 11) =====
# Diccionario tipo -> lista de nombres
# Pokémons agrupados por tipo (cada tipo es una sección en la selección y en la biblioteca)
SECCIONES_POKEMON = {
    "FUEGO": ["charmander", "vulpix", "growlithe", "ponyta", "magmar", "moltres"],
    "AGUA": ["squirtle", "psyduck", "poliwag", "horsea", "staryu", "tentacool", "slowpoke", "seel", "shellder", "krabby", "goldeen", "magikarp", "lapras"],
    "PLANTA": ["bulbasaur", "oddish", "bellsprout", "tangela", "exeggcute"],
    "ELÉCTRICO": ["pikachu", "magnemite", "voltorb", "electabuzz", "mareep", "zapdos"],
    "TIERRA": ["sandshrew", "geodude", "cubone", "phanpy", "diglett", "rhyhorn", "onix", "omanyte", "kabuto", "aerodactyl"],
    "NORMAL": ["pidgey", "rattata", "spearow", "clefairy", "jigglypuff", "meowth", "farfetchd", "doduo", "lickitung", "chansey", "kangaskhan", "tauros", "ditto", "eevee", "porygon", "snorlax"],
    "BICHO": ["caterpie", "weedle", "paras", "venonat", "scyther", "pinsir"],
    "VENENO": ["ekans", "nidoran_f", "nidoran_m", "zubat", "grimer", "koffing"],
    "PSÍQUICO": ["abra", "drowzee", "mr_mime", "mewtwo", "mew"],
    "LUCHA": ["mankey", "machop", "hitmonlee", "hitmonchan"],
    "FANTASMA": ["gastly"],
    "HIELO": ["jynx", "articuno"],
    "DRAGÓN": ["dratini"],
}

# ===== TEMA: Tuplas (Clase 11) =====
# Cuarta habilidad de todos los Pokémon: la Poción. Es una tupla (nombre, potencia, tipo) compartida por los 81 (una tupla no se puede modificar,
# así que compartirla es seguro). No hace daño: cura un poco y activa un escudo que bloquea el siguiente ataque (ver motor_combate.py).
# Para cambiarle el nombre a todos los Pokémon a la vez basta con cambiarlo aquí
POCION = ("Recuperación", 0, "Estado")

# ===== TEMA: Diccionarios anidados (Clase 11) =====
# nombre -> diccionario de datos; 'habilidades' es una lista de tuplas (nombre, potencia, tipo)
# Datos de cada Pokémon: tipo, vida (hp), estadísticas base, descripción y sus 4 habilidades.
# Cada habilidad es (nombre, potencia, tipo); la cuarta siempre es la Poción (tipo "Estado", potencia 0): no hace daño, cura y da un escudo
CATALOGO_POKEMONS = {
    "charmander": {
        "tipo": "Fuego", "hp": 120, "ataque": 52, "defensa": 43, "atk_esp": 60, "def_esp": 50, "velocidad": 65,
        "desc": "Criatura de naturaleza cálida que habita en zonas montañosas y rocosas. La llama en la punta de su cola refleja su estado vital y anímico.",
        "habilidades": [("Arañazo", 45, "Normal"), ("Lanzallamas", 65, "Fuego"), ("Envite Ígneo", 110, "Fuego"), POCION]
    },
    "vulpix": {
        "tipo": "Fuego", "hp": 110, "ataque": 41, "defensa": 40, "atk_esp": 50, "def_esp": 65, "velocidad": 65,
        "desc": "Ágil zorro de pelaje rojizo que manipula llamas internas a voluntad. Al nacer posee una sola cola que se ramifica con los años.",
        "habilidades": [("Ataque Rápido", 40, "Normal"), ("Ascuas", 60, "Fuego"), ("Giro Fuego", 105, "Fuego"), POCION]
    },
    "growlithe": {
        "tipo": "Fuego", "hp": 130, "ataque": 70, "defensa": 45, "atk_esp": 70, "def_esp": 50, "velocidad": 60,
        "desc": "Fiel canino dotado de un valor inquebrantable. Protege su territorio con fiereza y guarda un fuerte lazo de lealtad con su cuidador.",
        "habilidades": [("Mordisco", 50, "Normal"), ("Colmillo Ígneo", 70, "Fuego"), ("Envite Ígneo", 120, "Fuego"), POCION]
    },
    "ponyta": {
        "tipo": "Fuego", "hp": 115, "ataque": 85, "defensa": 55, "atk_esp": 65, "def_esp": 65, "velocidad": 90,
        "desc": "Equino veloz cuyas patas y crines arden en llamas. Sus aptitudes para el galope se potencian al saltar obstáculos naturales.",
        "habilidades": [("Patada", 45, "Normal"), ("Rueda Fuego", 65, "Fuego"), ("Nitrocarga", 110, "Fuego"), POCION]
    },
    "magmar": {
        "tipo": "Fuego", "hp": 140, "ataque": 95, "defensa": 57, "atk_esp": 100, "def_esp": 85, "velocidad": 93,
        "desc": "Habita inmerso en las profundidades de los cráteres volcánicos. Su temperatura corporal alcanza niveles extremos capaces de fundir la roca.",
        "habilidades": [("Puño Certero", 50, "Normal"), ("Puño Fuego", 70, "Fuego"), ("Llamarada", 120, "Fuego"), POCION]
    },
    "squirtle": {
        "tipo": "Agua", "hp": 125, "ataque": 48, "defensa": 65, "atk_esp": 50, "def_esp": 64, "velocidad": 43,
        "desc": "Tortuga acuática cuyo caparazón hidroaerodinámico reduce la resistencia al nadar y sirve como poderosa defensa ante impactos.",
        "habilidades": [("Placaje", 45, "Normal"), ("Pistola Agua", 60, "Agua"), ("Hidrobomba", 115, "Agua"), POCION]
    },
    "psyduck": {
        "tipo": "Agua", "hp": 120, "ataque": 52, "defensa": 48, "atk_esp": 65, "def_esp": 50, "velocidad": 55,
        "desc": "Criatura despistada que sufre jaquecas crónicas. Cuando el dolor de cabeza llega al límite, libera ondas de poder psíquico oculto.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Surf", 65, "Agua"), ("Hidropulso", 110, "Agua"), POCION]
    },
    "poliwag": {
        "tipo": "Agua", "hp": 110, "ataque": 50, "defensa": 40, "atk_esp": 40, "def_esp": 40, "velocidad": 90,
        "desc": "Anfibio de piel traslúcida que permite observar su órgano vital en espiral. Se desenvuelve con soltura en corrientes fluviales.",
        "habilidades": [("Bofetón", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Hidrobomba", 120, "Agua"), POCION]
    },
    "horsea": {
        "tipo": "Agua", "hp": 105, "ataque": 40, "defensa": 70, "atk_esp": 70, "def_esp": 25, "velocidad": 60,
        "desc": "Pequeño habitante marino que nada oscilando su aleta dorsal. Ante amenazas inminentes, expulsa chorros de tinta para camuflarse.",
        "habilidades": [("Pistola Agua", 45, "Agua"), ("Rayos Burbuja", 65, "Agua"), ("Hidrobomba", 115, "Agua"), POCION]
    },
    "staryu": {
        "tipo": "Agua", "hp": 115, "ataque": 45, "defensa": 55, "atk_esp": 70, "def_esp": 55, "velocidad": 85,
        "desc": "Misterioso organismo marino con simetría estelar. Su núcleo central emite pulsos lumínicos durante las horas nocturnas.",
        "habilidades": [("Rapidez", 45, "Normal"), ("Pistola Agua", 60, "Agua"), ("Rayo Hielo", 110, "Agua"), POCION]
    },
    "bulbasaur": {
        "tipo": "Planta", "hp": 125, "ataque": 49, "defensa": 49, "atk_esp": 65, "def_esp": 65, "velocidad": 45,
        "desc": "Reptil pacífico que transporta un bulbo vegetal en el dorso. Este bulbo crece absorbiendo la luz solar durante el día.",
        "habilidades": [("Placaje", 45, "Normal"), ("Látigo Cepa", 60, "Planta"), ("Rayo Solar", 115, "Planta"), POCION]
    },
    "oddish": {
        "tipo": "Planta", "hp": 110, "ataque": 50, "defensa": 55, "atk_esp": 75, "def_esp": 65, "velocidad": 30,
        "desc": "Organismo de hábitos nocturnos. Durante el día permanece enterrado absorbiendo nutrientes minerales del suelo forestal.",
        "habilidades": [("Absorber", 40, "Planta"), ("Hoja Afilada", 65, "Planta"), ("Gigadrenado", 110, "Planta"), POCION]
    },
    "bellsprout": {
        "tipo": "Planta", "hp": 105, "ataque": 75, "defensa": 35, "atk_esp": 70, "def_esp": 30, "velocidad": 40,
        "desc": "Planta carnívora de tallo flexible capaz de esquivar embestidas ágilmente antes de atrapar a sus presas con lianas.",
        "habilidades": [("Látigo", 40, "Normal"), ("Látigo Cepa", 60, "Planta"), ("Bomba Lodo", 105, "Planta"), POCION]
    },
    "tangela": {
        "tipo": "Planta", "hp": 135, "ataque": 55, "defensa": 115, "atk_esp": 100, "def_esp": 40, "velocidad": 60,
        "desc": "Enigmática criatura envuelta en densas lianas azules. Si una de sus extremidades vegetales se desprende, no experimenta dolor.",
        "habilidades": [("Constricción", 45, "Normal"), ("Megaagotar", 65, "Planta"), ("Látigo Cerval", 115, "Planta"), POCION]
    },
    "exeggcute": {
        "tipo": "Planta", "hp": 120, "ataque": 40, "defensa": 80, "atk_esp": 60, "def_esp": 45, "velocidad": 40,
        "desc": "Conjunto de seis semillas con aspecto de frutos que se mantienen unidas y sincronizadas mediante telepatía constante.",
        "habilidades": [("Confusión", 45, "Psíquico"), ("Megaagotar", 65, "Planta"), ("Psíquico", 110, "Psíquico"), POCION]
    },
    "pikachu": {
        "tipo": "Eléctrico", "hp": 110, "ataque": 55, "defensa": 40, "atk_esp": 50, "def_esp": 50, "velocidad": 90,
        "desc": "Roedor ágil que almacena energía eléctrica en sus mejillas. Al sentirse amenazado, emite potentes descargas defensivas.",
        "habilidades": [("Ataque Rápido", 45, "Normal"), ("Impactrueno", 60, "Eléctrico"), ("Trueno", 120, "Eléctrico"), POCION]
    },
    "magnemite": {
        "tipo": "Eléctrico", "hp": 115, "ataque": 35, "defensa": 70, "atk_esp": 95, "def_esp": 55, "velocidad": 45,
        "desc": "Unidad mecánica flotante que desafía la gravedad mediante campos electromagnéticos emitidos por sus terminales laterales.",
        "habilidades": [("Tacleada", 40, "Normal"), ("Chispa", 65, "Eléctrico"), ("Electrocañón", 115, "Eléctrico"), POCION]
    },
    "voltorb": {
        "tipo": "Eléctrico", "hp": 100, "ataque": 30, "defensa": 50, "atk_esp": 55, "def_esp": 55, "velocidad": 100,
        "desc": "Esfera energética inestable que guarda gran parecido con una Poké Ball. Detona ante sacudidas o estímulos bruscos.",
        "habilidades": [("Placaje", 45, "Normal"), ("Impactrueno", 60, "Eléctrico"), ("Autodestrucción", 120, "Eléctrico"), POCION]
    },
    "electabuzz": {
        "tipo": "Eléctrico", "hp": 135, "ataque": 83, "defensa": 57, "atk_esp": 95, "def_esp": 85, "velocidad": 105,
        "desc": "Humanoide corpulento atraído por las subestaciones eléctricas. Se alimenta directamente de generadores de energía.",
        "habilidades": [("Puño Certero", 50, "Normal"), ("Puño Trueno", 70, "Eléctrico"), ("Trueno", 120, "Eléctrico"), POCION]
    },
    "mareep": {
        "tipo": "Eléctrico", "hp": 120, "ataque": 40, "defensa": 40, "atk_esp": 65, "def_esp": 45, "velocidad": 35,
        "desc": "Ovejita pacífica cuya suave lana acumula electricidad estática por fricción atmosférica, brillando en la oscuridad.",
        "habilidades": [("Placaje", 40, "Normal"), ("Onda Shock", 60, "Eléctrico"), ("Trueno", 110, "Eléctrico"), POCION]
    },
    "sandshrew": {
        "tipo": "Tierra", "hp": 125, "ataque": 75, "defensa": 85, "atk_esp": 20, "def_esp": 30, "velocidad": 40,
        "desc": "Mamífero cavador adaptado a entornos áridos. Al rodar sobre sí mismo absorbe impactos y amortigua caídas con su piel acorazada.",
        "habilidades": [("Arañazo", 45, "Normal"), ("Disparo Lodo", 60, "Tierra"), ("Terremoto", 120, "Tierra"), POCION]
    },
    "geodude": {
        "tipo": "Tierra", "hp": 130, "ataque": 80, "defensa": 100, "atk_esp": 30, "def_esp": 30, "velocidad": 20,
        "desc": "Formación rocosa con consciencia propia que habita en senderos montañosos, confundiéndose fácilmente con rocas ordinarias.",
        "habilidades": [("Placaje", 45, "Normal"), ("Terratemblor", 65, "Tierra"), ("Terremoto", 120, "Tierra"), POCION]
    },
    "cubone": {
        "tipo": "Tierra", "hp": 120, "ataque": 50, "defensa": 95, "atk_esp": 40, "def_esp": 50, "velocidad": 35,
        "desc": "Solitaria criatura que resguarda su rostro con el cráneo de su progenitora, emitiendo melancólicos lamentos al atardecer.",
        "habilidades": [("Hueso Palo", 50, "Normal"), ("Bofetón Lodo", 60, "Tierra"), ("Huesomerang", 110, "Tierra"), POCION]
    },
    "phanpy": {
        "tipo": "Tierra", "hp": 140, "ataque": 60, "defensa": 60, "atk_esp": 40, "def_esp": 40, "velocidad": 40,
        "desc": "Pequeño paquidermo juguetón que utiliza su larga trompa para interactuar con su entorno y saludar a otros ejemplares.",
        "habilidades": [("Placaje", 45, "Normal"), ("Disparo Lodo", 65, "Tierra"), ("Terremoto", 115, "Tierra"), POCION]
    },
    "diglett": {
        "tipo": "Tierra", "hp": 95, "ataque": 55, "defensa": 25, "atk_esp": 35, "def_esp": 45, "velocidad": 95,
        "desc": "Especie subterránea que perfora la tierra a poca profundidad para alimentarse de raíces sin exponerse al exterior.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Bofetón Lodo", 60, "Tierra"), ("Terremoto", 110, "Tierra"), POCION]
    },
    "moltres": {
        "tipo": "Fuego", "hp": 145, "ataque": 97, "defensa": 87, "atk_esp": 121, "def_esp": 82, "velocidad": 90,
        "desc": "Ave legendaria de plumaje en llamas. Se dice que su canto anuncia la llegada de la primavera.",
        "habilidades": [("Ataque Rápido", 50, "Normal"), ("Lanzallamas", 70, "Fuego"), ("Llamarada", 120, "Fuego"), POCION]
    },
    "tentacool": {
        "tipo": "Agua", "hp": 115, "ataque": 55, "defensa": 48, "atk_esp": 69, "def_esp": 137, "velocidad": 70,
        "desc": "Medusa marina casi transparente que flota con las corrientes. Sus tentáculos paralizan a quien se acerca demasiado.",
        "habilidades": [("Constricción", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Hidropulso", 105, "Agua"), POCION]
    },
    "slowpoke": {
        "tipo": "Agua", "hp": 145, "ataque": 53, "defensa": 53, "atk_esp": 32, "def_esp": 32, "velocidad": 15,
        "desc": "Criatura lenta y distraída que tarda en reaccionar a todo. Pasa los días pescando con la cola a orillas del agua.",
        "habilidades": [("Placaje", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Hidropulso", 105, "Agua"), POCION]
    },
    "seel": {
        "tipo": "Agua", "hp": 130, "ataque": 45, "defensa": 55, "atk_esp": 45, "def_esp": 70, "velocidad": 45,
        "desc": "Mamífero marino de pelaje blanco que se desliza con soltura entre el hielo. Le encantan las aguas frías del norte.",
        "habilidades": [("Placaje", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Hidropulso", 105, "Agua"), POCION]
    },
    "shellder": {
        "tipo": "Agua", "hp": 110, "ataque": 51, "defensa": 79, "atk_esp": 36, "def_esp": 20, "velocidad": 40,
        "desc": "Molusco encerrado en una concha casi indestructible. Solo abre su caparazón para atacar con su lengua.",
        "habilidades": [("Tacleada", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Rayo Hielo", 105, "Agua"), POCION]
    },
    "krabby": {
        "tipo": "Agua", "hp": 110, "ataque": 97, "defensa": 83, "atk_esp": 23, "def_esp": 23, "velocidad": 50,
        "desc": "Cangrejo de grandes pinzas que vive en las playas rocosas. Si pierde una pinza, le vuelve a crecer en poco tiempo.",
        "habilidades": [("Bofetón", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Hidrobomba", 105, "Agua"), POCION]
    },
    "goldeen": {
        "tipo": "Agua", "hp": 120, "ataque": 60, "defensa": 53, "atk_esp": 31, "def_esp": 44, "velocidad": 63,
        "desc": "Pez de aletas largas y elegantes que nada en ríos y estanques. Su cuerno es muy resistente y lo usa para defenderse.",
        "habilidades": [("Rapidez", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Hidropulso", 105, "Agua"), POCION]
    },
    "magikarp": {
        "tipo": "Agua", "hp": 105, "ataque": 14, "defensa": 80, "atk_esp": 22, "def_esp": 29, "velocidad": 80,
        "desc": "Pez débil que apenas puede hacer algo más que chapotear. Aun así es muy resistente y se encuentra en cualquier lugar.",
        "habilidades": [("Placaje", 40, "Normal"), ("Burbuja", 60, "Agua"), ("Hidropulso", 105, "Agua"), POCION]
    },
    "lapras": {
        "tipo": "Agua", "hp": 150, "ataque": 70, "defensa": 66, "atk_esp": 70, "def_esp": 78, "velocidad": 60,
        "desc": "Criatura dócil y amable que transporta personas sobre el agua. Entiende el lenguaje humano y canta melodías tranquilas.",
        "habilidades": [("Placaje", 45, "Normal"), ("Surf", 65, "Agua"), ("Rayo Hielo", 115, "Agua"), POCION]
    },
    "zapdos": {
        "tipo": "Eléctrico", "hp": 145, "ataque": 102, "defensa": 96, "atk_esp": 142, "def_esp": 102, "velocidad": 100,
        "desc": "Ave legendaria que vive entre nubes de tormenta. Dicen que cae sobre quien la desafía acompañada de rayos.",
        "habilidades": [("Ataque Rápido", 50, "Normal"), ("Onda Shock", 70, "Eléctrico"), ("Trueno", 120, "Eléctrico"), POCION]
    },
    "rhyhorn": {
        "tipo": "Tierra", "hp": 140, "ataque": 83, "defensa": 93, "atk_esp": 29, "def_esp": 29, "velocidad": 25,
        "desc": "Gran rinoceronte de piel gruesa y cuerno resistente. Embiste sin pensar y se olvida de lo que hacía al instante.",
        "habilidades": [("Placaje", 40, "Normal"), ("Terratemblor", 60, "Tierra"), ("Terremoto", 105, "Tierra"), POCION]
    },
    "onix": {
        "tipo": "Tierra", "hp": 115, "ataque": 56, "defensa": 197, "atk_esp": 37, "def_esp": 56, "velocidad": 70,
        "desc": "Serpiente de roca de gran tamaño que excava túneles bajo tierra. Con los años, su cuerpo se vuelve más duro y liso.",
        "habilidades": [("Constricción", 45, "Normal"), ("Terratemblor", 65, "Tierra"), ("Terremoto", 115, "Tierra"), POCION]
    },
    "omanyte": {
        "tipo": "Tierra", "hp": 115, "ataque": 45, "defensa": 112, "atk_esp": 100, "def_esp": 61, "velocidad": 35,
        "desc": "Pokémon prehistórico que revivió desde un fósil. Nadaba con sus tentáculos y se protegía dentro de su concha espiral.",
        "habilidades": [("Constricción", 40, "Normal"), ("Disparo Lodo", 60, "Tierra"), ("Terremoto", 105, "Tierra"), POCION]
    },
    "kabuto": {
        "tipo": "Tierra", "hp": 110, "ataque": 94, "defensa": 106, "atk_esp": 65, "def_esp": 53, "velocidad": 55,
        "desc": "Pokémon antiguo que regresó de un fósil y casi no ha cambiado en millones de años. Se camufla en el fondo marino.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Disparo Lodo", 60, "Tierra"), ("Terremoto", 105, "Tierra"), POCION]
    },
    "aerodactyl": {
        "tipo": "Tierra", "hp": 140, "ataque": 91, "defensa": 56, "atk_esp": 52, "def_esp": 65, "velocidad": 130,
        "desc": "Pterosaurio resucitado de un fósil que domina los cielos. Sus colmillos afilados desgarran cualquier cosa que atrapa.",
        "habilidades": [("Mordisco", 45, "Normal"), ("Terratemblor", 65, "Tierra"), ("Terremoto", 115, "Tierra"), POCION]
    },
    "pidgey": {
        "tipo": "Normal", "hp": 115, "ataque": 54, "defensa": 48, "atk_esp": 42, "def_esp": 42, "velocidad": 56,
        "desc": "Ave pequeña y dócil que evita los combates. Agita la arena con sus alas para esconderse de sus enemigos.",
        "habilidades": [("Ataque Rápido", 40, "Normal"), ("Picotazo", 60, "Normal"), ("Derribo", 105, "Normal"), POCION]
    },
    "rattata": {
        "tipo": "Normal", "hp": 110, "ataque": 63, "defensa": 39, "atk_esp": 28, "def_esp": 39, "velocidad": 72,
        "desc": "Roedor ágil que se adapta a cualquier entorno. Sus dientes crecen sin parar y los usa para roer casi todo.",
        "habilidades": [("Placaje", 40, "Normal"), ("Hipercolmillo", 60, "Normal"), ("Derribo", 105, "Normal"), POCION]
    },
    "spearow": {
        "tipo": "Normal", "hp": 115, "ataque": 63, "defensa": 31, "atk_esp": 32, "def_esp": 32, "velocidad": 70,
        "desc": "Ave temperamental que defiende su territorio con furia. Debe batir las alas rápido porque no puede planear mucho.",
        "habilidades": [("Ataque Rápido", 40, "Normal"), ("Picotazo", 60, "Normal"), ("Derribo", 105, "Normal"), POCION]
    },
    "clefairy": {
        "tipo": "Normal", "hp": 135, "ataque": 42, "defensa": 45, "atk_esp": 57, "def_esp": 61, "velocidad": 35,
        "desc": "Criatura tierna y misteriosa que baila bajo la luz de la luna llena. Su aspecto encantador la hace muy popular.",
        "habilidades": [("Bofetón", 40, "Normal"), ("Golpe Cuerpo", 60, "Normal"), ("Derribo", 105, "Normal"), POCION]
    },
    "jigglypuff": {
        "tipo": "Normal", "hp": 150, "ataque": 51, "defensa": 23, "atk_esp": 51, "def_esp": 28, "velocidad": 20,
        "desc": "Criatura de cuerpo redondo y suave que canta una melodía que da sueño. Si nadie la escucha, se enfurece.",
        "habilidades": [("Bofetón", 40, "Normal"), ("Golpe Cuerpo", 60, "Normal"), ("Derribo", 105, "Normal"), POCION]
    },
    "meowth": {
        "tipo": "Normal", "hp": 115, "ataque": 52, "defensa": 40, "atk_esp": 46, "def_esp": 46, "velocidad": 90,
        "desc": "Gato que sale de noche en busca de objetos brillantes. La moneda de su frente cambia con su estado de ánimo.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Cuchillada", 60, "Normal"), ("Derribo", 105, "Normal"), POCION]
    },
    "farfetchd": {
        "tipo": "Normal", "hp": 125, "ataque": 94, "defensa": 58, "atk_esp": 61, "def_esp": 65, "velocidad": 60,
        "desc": "Pato salvaje que siempre lleva un puerro como arma. Defiende ese puerro con su vida porque es su bien más preciado.",
        "habilidades": [("Ataque Rápido", 45, "Normal"), ("Cuchillada", 65, "Normal"), ("Doble Filo", 115, "Normal"), POCION]
    },
    "doduo": {
        "tipo": "Normal", "hp": 115, "ataque": 71, "defensa": 37, "atk_esp": 29, "def_esp": 29, "velocidad": 75,
        "desc": "Ave de dos cabezas que corre muy rápido en vez de volar. Sus cabezas se turnan para dormir y vigilar.",
        "habilidades": [("Ataque Rápido", 40, "Normal"), ("Picotazo", 60, "Normal"), ("Derribo", 105, "Normal"), POCION]
    },
    "lickitung": {
        "tipo": "Normal", "hp": 145, "ataque": 60, "defensa": 82, "atk_esp": 66, "def_esp": 82, "velocidad": 30,
        "desc": "Criatura cuya lengua es el doble de larga que su cuerpo. La usa para atrapar cosas y como mano para agarrar.",
        "habilidades": [("Bofetón", 45, "Normal"), ("Golpe Cuerpo", 65, "Normal"), ("Derribo", 115, "Normal"), POCION]
    },
    "chansey": {
        "tipo": "Normal", "hp": 150, "ataque": 4, "defensa": 4, "atk_esp": 27, "def_esp": 80, "velocidad": 50,
        "desc": "Pokémon bondadoso que lleva un huevo nutritivo en la bolsa. Comparte ese huevo con quienes están heridos o enfermos.",
        "habilidades": [("Bofetón", 45, "Normal"), ("Golpe Cuerpo", 65, "Normal"), ("Doble Filo", 115, "Normal"), POCION]
    },
    "kangaskhan": {
        "tipo": "Normal", "hp": 150, "ataque": 71, "defensa": 60, "atk_esp": 30, "def_esp": 60, "velocidad": 90,
        "desc": "Madre protectora que lleva a su cría en la bolsa del vientre. Ataca sin piedad a cualquiera que amenace a su pequeño.",
        "habilidades": [("Puño Certero", 45, "Normal"), ("Golpe Cuerpo", 65, "Normal"), ("Hiperrayo", 115, "Normal"), POCION]
    },
    "tauros": {
        "tipo": "Normal", "hp": 135, "ataque": 70, "defensa": 67, "atk_esp": 28, "def_esp": 49, "velocidad": 110,
        "desc": "Toro salvaje que se azota con sus colas antes de embestir. Una vez que encuentra un objetivo, nada lo detiene.",
        "habilidades": [("Placaje", 45, "Normal"), ("Golpe Cuerpo", 65, "Normal"), ("Derribo", 115, "Normal"), POCION]
    },
    "ditto": {
        "tipo": "Normal", "hp": 120, "ataque": 48, "defensa": 48, "atk_esp": 48, "def_esp": 48, "velocidad": 48,
        "desc": "Criatura amorfa capaz de transformarse en cualquier cosa que ve. Reorganiza sus células para copiar a otros seres.",
        "habilidades": [("Placaje", 45, "Normal"), ("Golpe Cuerpo", 65, "Normal"), ("Derribo", 115, "Normal"), POCION]
    },
    "eevee": {
        "tipo": "Normal", "hp": 125, "ataque": 48, "defensa": 44, "atk_esp": 39, "def_esp": 57, "velocidad": 55,
        "desc": "Criatura de genética inestable que puede evolucionar de muchas formas. Se adapta a su entorno con facilidad.",
        "habilidades": [("Ataque Rápido", 40, "Normal"), ("Golpe Cuerpo", 60, "Normal"), ("Derribo", 105, "Normal"), POCION]
    },
    "porygon": {
        "tipo": "Normal", "hp": 130, "ataque": 68, "defensa": 80, "atk_esp": 97, "def_esp": 85, "velocidad": 40,
        "desc": "Pokémon artificial formado por código digital. Puede entrar en el ciberespacio y moverse por redes de datos.",
        "habilidades": [("Tacleada", 45, "Normal"), ("Golpe Cuerpo", 65, "Normal"), ("Hiperrayo", 115, "Normal"), POCION]
    },
    "snorlax": {
        "tipo": "Normal", "hp": 150, "ataque": 77, "defensa": 46, "atk_esp": 46, "def_esp": 77, "velocidad": 30,
        "desc": "Gigante que come toneladas de comida al día y duerme el resto del tiempo. Nada lo despierta salvo el hambre.",
        "habilidades": [("Placaje", 50, "Normal"), ("Golpe Cuerpo", 70, "Normal"), ("Hiperrayo", 120, "Normal"), POCION]
    },
    "caterpie": {
        "tipo": "Bicho", "hp": 120, "ataque": 44, "defensa": 51, "atk_esp": 29, "def_esp": 29, "velocidad": 45,
        "desc": "Oruga voraz que devora hojas sin parar. Sus antenas desprenden un olor fuerte para espantar a sus enemigos.",
        "habilidades": [("Placaje", 40, "Normal"), ("Picadura", 60, "Bicho"), ("Zumbido", 105, "Bicho"), POCION]
    },
    "weedle": {
        "tipo": "Bicho", "hp": 115, "ataque": 51, "defensa": 44, "atk_esp": 29, "def_esp": 29, "velocidad": 50,
        "desc": "Larva con un aguijón venenoso en la cabeza. Se esconde en el follaje de los bosques y se alimenta de hojas.",
        "habilidades": [("Placaje", 40, "Normal"), ("Picadura", 60, "Bicho"), ("Zumbido", 105, "Bicho"), POCION]
    },
    "paras": {
        "tipo": "Bicho", "hp": 115, "ataque": 71, "defensa": 56, "atk_esp": 46, "def_esp": 56, "velocidad": 25,
        "desc": "Insecto con dos hongos creciendo en su lomo. Los hongos absorben sus nutrientes y toman parte de su energía.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Picadura", 60, "Bicho"), ("Zumbido", 105, "Bicho"), POCION]
    },
    "venonat": {
        "tipo": "Bicho", "hp": 130, "ataque": 56, "defensa": 51, "atk_esp": 41, "def_esp": 56, "velocidad": 45,
        "desc": "Insecto peludo de ojos enormes que brillan en la noche. Atrae a su presa con luz y la envuelve con su polvo.",
        "habilidades": [("Placaje", 40, "Normal"), ("Picadura", 60, "Bicho"), ("Zumbido", 105, "Bicho"), POCION]
    },
    "scyther": {
        "tipo": "Bicho", "hp": 135, "ataque": 93, "defensa": 68, "atk_esp": 47, "def_esp": 68, "velocidad": 105,
        "desc": "Insecto con guadañas que se mueve con una velocidad asombrosa. Sus cuchillas cortan casi cualquier cosa.",
        "habilidades": [("Acuchillar", 45, "Normal"), ("Tijera X", 65, "Bicho"), ("Megacuerno", 115, "Bicho"), POCION]
    },
    "pinsir": {
        "tipo": "Bicho", "hp": 130, "ataque": 95, "defensa": 76, "atk_esp": 42, "def_esp": 53, "velocidad": 85,
        "desc": "Escarabajo de grandes pinzas que atrapa a sus presas y las aprieta con fuerza. Si no logra vencer, las lanza lejos.",
        "habilidades": [("Constricción", 45, "Normal"), ("Tijera X", 65, "Bicho"), ("Megacuerno", 115, "Bicho"), POCION]
    },
    "ekans": {
        "tipo": "Veneno", "hp": 115, "ataque": 63, "defensa": 46, "atk_esp": 42, "def_esp": 57, "velocidad": 55,
        "desc": "Serpiente sigilosa que se enrosca en los matorrales. Se mueve sin hacer ruido para atacar por sorpresa.",
        "habilidades": [("Mordisco", 40, "Normal"), ("Ácido", 60, "Veneno"), ("Bomba Lodo", 105, "Veneno"), POCION]
    },
    "nidoran_f": {
        "tipo": "Veneno", "hp": 125, "ataque": 52, "defensa": 57, "atk_esp": 44, "def_esp": 44, "velocidad": 41,
        "desc": "Pokémon pequeño de púas venenosas. Las hembras tienen cuernos pequeños y protegen a su grupo con cuidado.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Picotazo Veneno", 60, "Veneno"), ("Bomba Lodo", 105, "Veneno"), POCION]
    },
    "nidoran_m": {
        "tipo": "Veneno", "hp": 120, "ataque": 65, "defensa": 46, "atk_esp": 46, "def_esp": 46, "velocidad": 50,
        "desc": "El macho de Nidoran mueve sus grandes orejas para detectar peligros. Su cuerno pequeño inyecta un veneno fuerte.",
        "habilidades": [("Placaje", 40, "Normal"), ("Picotazo Veneno", 60, "Veneno"), ("Bomba Lodo", 105, "Veneno"), POCION]
    },
    "zubat": {
        "tipo": "Veneno", "hp": 115, "ataque": 60, "defensa": 47, "atk_esp": 40, "def_esp": 53, "velocidad": 55,
        "desc": "Murciélago sin ojos que vuela por cuevas oscuras usando ondas ultrasónicas. Chupa la sangre de sus presas de noche.",
        "habilidades": [("Mordisco", 40, "Normal"), ("Ácido", 60, "Veneno"), ("Bomba Lodo", 105, "Veneno"), POCION]
    },
    "grimer": {
        "tipo": "Veneno", "hp": 140, "ataque": 70, "defensa": 44, "atk_esp": 35, "def_esp": 44, "velocidad": 25,
        "desc": "Masa de lodo tóxico nacida de residuos contaminados. Se arrastra por zonas sucias y todo lo que toca se pudre.",
        "habilidades": [("Placaje", 40, "Normal"), ("Ácido", 60, "Veneno"), ("Bomba Lodo", 105, "Veneno"), POCION]
    },
    "koffing": {
        "tipo": "Veneno", "hp": 115, "ataque": 84, "defensa": 123, "atk_esp": 77, "def_esp": 58, "velocidad": 35,
        "desc": "Globo de gas tóxico que flota por zonas contaminadas. Si se calienta de más, puede llegar a explotar.",
        "habilidades": [("Tacleada", 40, "Normal"), ("Ácido", 60, "Veneno"), ("Bomba Lodo", 105, "Veneno"), POCION]
    },
    "abra": {
        "tipo": "Psíquico", "hp": 110, "ataque": 16, "defensa": 12, "atk_esp": 85, "def_esp": 45, "velocidad": 90,
        "desc": "Pokémon que duerme casi todo el día pero siente el peligro y se teletransporta. Rara vez se queda quieto en un lugar.",
        "habilidades": [("Confusión", 40, "Psíquico"), ("Psicorrayo", 60, "Psíquico"), ("Psíquico", 105, "Psíquico"), POCION]
    },
    "drowzee": {
        "tipo": "Psíquico", "hp": 130, "ataque": 43, "defensa": 41, "atk_esp": 39, "def_esp": 81, "velocidad": 42,
        "desc": "Criatura que se alimenta de los sueños de otros. Su trompa le permite detectar quién está dormido cerca.",
        "habilidades": [("Confusión", 40, "Psíquico"), ("Psicorrayo", 60, "Psíquico"), ("Psíquico", 105, "Psíquico"), POCION]
    },
    "mr_mime": {
        "tipo": "Psíquico", "hp": 115, "ataque": 37, "defensa": 54, "atk_esp": 82, "def_esp": 99, "velocidad": 90,
        "desc": "Mimo maestro de la pantomima que crea barreras invisibles con sus manos. Sus gestos hacen que los objetos parezcan reales.",
        "habilidades": [("Confusión", 45, "Psíquico"), ("Psicorrayo", 65, "Psíquico"), ("Psíquico", 115, "Psíquico"), POCION]
    },
    "mewtwo": {
        "tipo": "Psíquico", "hp": 150, "ataque": 89, "defensa": 73, "atk_esp": 125, "def_esp": 73, "velocidad": 130,
        "desc": "Pokémon creado por manipulación genética para ser el más fuerte. Su poder psíquico no tiene comparación.",
        "habilidades": [("Confusión", 50, "Psíquico"), ("Psicorrayo", 70, "Psíquico"), ("Psíquico", 120, "Psíquico"), POCION]
    },
    "mew": {
        "tipo": "Psíquico", "hp": 150, "ataque": 101, "defensa": 101, "atk_esp": 101, "def_esp": 101, "velocidad": 100,
        "desc": "Pokémon legendario de aspecto juguetón que posee el ADN de todos los demás. Casi nadie lo ha visto.",
        "habilidades": [("Confusión", 50, "Psíquico"), ("Psicorrayo", 70, "Psíquico"), ("Psíquico", 120, "Psíquico"), POCION]
    },
    "mankey": {
        "tipo": "Lucha", "hp": 115, "ataque": 64, "defensa": 28, "atk_esp": 28, "def_esp": 36, "velocidad": 70,
        "desc": "Mono de carácter explosivo que se enfurece sin motivo. Cuando se enoja, nada lo detiene hasta quedar agotado.",
        "habilidades": [("Arañazo", 40, "Normal"), ("Golpe Kárate", 60, "Lucha"), ("Sumisión", 105, "Lucha"), POCION]
    },
    "machop": {
        "tipo": "Lucha", "hp": 135, "ataque": 59, "defensa": 37, "atk_esp": 26, "def_esp": 26, "velocidad": 35,
        "desc": "Criatura de músculos muy desarrollados que entrena a todas horas. Puede levantar cien personas sin esfuerzo.",
        "habilidades": [("Puño Certero", 40, "Normal"), ("Golpe Kárate", 60, "Lucha"), ("Sumisión", 105, "Lucha"), POCION]
    },
    "hitmonlee": {
        "tipo": "Lucha", "hp": 120, "ataque": 84, "defensa": 37, "atk_esp": 24, "def_esp": 77, "velocidad": 87,
        "desc": "Luchador de patas elásticas que patea con gran fuerza. Sus piernas se estiran para golpear desde lejos.",
        "habilidades": [("Patada", 45, "Normal"), ("Doble Patada", 65, "Lucha"), ("A Bocajarro", 115, "Lucha"), POCION]
    },
    "hitmonchan": {
        "tipo": "Lucha", "hp": 120, "ataque": 74, "defensa": 55, "atk_esp": 24, "def_esp": 77, "velocidad": 76,
        "desc": "Boxeador de puños veloces como un relámpago. Golpea con la fuerza de un cañón y se mueve como una sombra.",
        "habilidades": [("Puño Certero", 45, "Normal"), ("Golpe Kárate", 65, "Lucha"), ("A Bocajarro", 115, "Lucha"), POCION]
    },
    "gastly": {
        "tipo": "Fantasma", "hp": 110, "ataque": 43, "defensa": 36, "atk_esp": 122, "def_esp": 43, "velocidad": 80,
        "desc": "Ser gaseoso que casi no tiene cuerpo físico. Se desliza por las paredes y envuelve a sus víctimas con su gas.",
        "habilidades": [("Tacleada", 40, "Normal"), ("Lengüetazo", 60, "Fantasma"), ("Bola Sombra", 105, "Fantasma"), POCION]
    },
    "jynx": {
        "tipo": "Hielo", "hp": 130, "ataque": 48, "defensa": 33, "atk_esp": 109, "def_esp": 90, "velocidad": 95,
        "desc": "Pokémon de aspecto humano que baila y emite sonidos extraños. Sus movimientos recuerdan a una danza rítmica.",
        "habilidades": [("Bofetón", 45, "Normal"), ("Viento Hielo", 65, "Hielo"), ("Rayo Hielo", 115, "Hielo"), POCION]
    },
    "articuno": {
        "tipo": "Hielo", "hp": 145, "ataque": 93, "defensa": 110, "atk_esp": 104, "def_esp": 137, "velocidad": 85,
        "desc": "Ave legendaria de plumas azules que parecen hechas de hielo. Se dice que aparece ante los viajeros perdidos en las montañas nevadas.",
        "habilidades": [("Ataque Rápido", 50, "Normal"), ("Viento Hielo", 70, "Hielo"), ("Ventisca", 120, "Hielo"), POCION]
    },
    "dratini": {
        "tipo": "Dragón", "hp": 120, "ataque": 68, "defensa": 48, "atk_esp": 53, "def_esp": 53, "velocidad": 50,
        "desc": "Dragón diminuto de cuerpo alargado que muda de piel con frecuencia. Durante mucho tiempo se creyó que no existía.",
        "habilidades": [("Constricción", 40, "Normal"), ("Garra Dragón", 60, "Dragón"), ("Pulso Dragón", 105, "Dragón"), POCION]
    },
}

# ===== TEMA: Diccionarios (Clase 11) + Listas (Clase 11) =====
# Diccionario categoría -> lista de nombres
# Categorías de fuerza: cada Pokémon es DÉBIL, NORMAL o LEGENDARIO (según la suma de sus estadísticas y los 5 legendarios de la Gen 1).
# El rival usa estas categorías para elegir su equipo: por cada Pokémon del jugador escoge uno de la misma categoría (ver motor_combate.py)
CATEGORIAS_POKEMON = {
    "DÉBIL": [
        "charmander", "vulpix", "squirtle", "psyduck", "poliwag", "horsea", "slowpoke", "seel", "shellder", "goldeen", "magikarp", "bulbasaur",
        "oddish", "bellsprout", "exeggcute", "pikachu", "voltorb", "mareep", "sandshrew", "geodude", "cubone", "phanpy", "diglett", "pidgey",
        "rattata", "spearow", "clefairy", "jigglypuff", "meowth", "doduo", "chansey", "ditto", "eevee", "caterpie", "weedle", "paras", "venonat",
        "ekans", "nidoran_f", "nidoran_m", "zubat", "grimer", "abra", "drowzee", "mankey", "machop", "gastly", "dratini",
    ],
    "NORMAL": [
        "growlithe", "ponyta", "magmar", "staryu", "tentacool", "krabby", "lapras", "tangela", "magnemite", "electabuzz", "rhyhorn", "onix",
        "omanyte", "kabuto", "aerodactyl", "farfetchd", "lickitung", "kangaskhan", "tauros", "porygon", "snorlax", "scyther", "pinsir", "koffing",
        "mr_mime", "hitmonlee", "hitmonchan", "jynx",
    ],
    "LEGENDARIO": [
        "moltres", "zapdos", "articuno", "mewtwo", "mew",
    ],
}

# ===== TEMA: Bucles (Clase 4) + Listas (Clase 11) =====
# for anidado sobre dict.items(); append agrega cada nombre a la lista
# Lista única con todos los pokémons en orden (la selección la usa para moverse con las flechas)
LISTA_PLANA_POKES = []
for tipo_seccion, nombres_pokemons in SECCIONES_POKEMON.items():
    for nombre_pokemon in nombres_pokemons:
        LISTA_PLANA_POKES.append(nombre_pokemon)