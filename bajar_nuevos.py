import os
import time
import urllib.error
import urllib.request

# Solo los Pokémon NUEVOS de tu lista (ID PokéAPI -> nombre del archivo .png)
NUEVOS_POKEMONES = {
    # Fuego
    146: "moltres",

    # Agua
    72: "tentacool",
    79: "slowpoke",
    86: "seel",
    90: "shellder",
    98: "krabby",
    118: "goldeen",
    129: "magikarp",
    131: "lapras",

    # Eléctrico
    145: "zapdos",

    # Tierra (según tu lista)
    111: "rhyhorn",
    95: "onix",
    138: "omanyte",
    140: "kabuto",
    142: "aerodactyl",

    # Normal
    16: "pidgey",
    19: "rattata",
    21: "spearow",
    35: "clefairy",
    39: "jigglypuff",
    52: "meowth",
    83: "farfetchd",
    84: "doduo",
    108: "lickitung",
    113: "chansey",
    115: "kangaskhan",
    128: "tauros",
    132: "ditto",
    133: "eevee",
    137: "porygon",
    143: "snorlax",

    # Bicho
    10: "caterpie",
    13: "weedle",
    46: "paras",
    48: "venonat",
    123: "scyther",
    127: "pinsir",

    # Veneno
    23: "ekans",
    29: "nidoran_f",
    32: "nidoran_m",
    41: "zubat",
    88: "grimer",
    109: "koffing",

    # Psíquico
    63: "abra",
    96: "drowzee",
    122: "mr_mime",
    150: "mewtwo",
    151: "mew",

    # Lucha
    56: "mankey",
    66: "machop",
    106: "hitmonlee",
    107: "hitmonchan",

    # Fantasma
    92: "gastly",

    # Hielo
    124: "jynx",
    144: "articuno",

    # Dragón
    147: "dratini",
}

CARPETA_FRENTE = "assets/pokemons/frente"
CARPETA_ESPALDA = "assets/pokemons/espalda"

os.makedirs(CARPETA_FRENTE, exist_ok=True)
os.makedirs(CARPETA_ESPALDA, exist_ok=True)

URL_FRENTE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-iii/firered-leafgreen/{id}.png"
URL_ESPALDA = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-iii/firered-leafgreen/back/{id}.png"


def bajar_png(url, ruta):
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    data = resp.read()
                    if data:
                        with open(ruta, "wb") as f:
                            f.write(data)
                        return True
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(0.3 * (intento + 1))
    return False


for poke_id, nombre in NUEVOS_POKEMONES.items():
    ok_f = bajar_png(URL_FRENTE.format(id=poke_id), os.path.join(CARPETA_FRENTE, f"{nombre}.png"))
    ok_e = bajar_png(URL_ESPALDA.format(id=poke_id), os.path.join(CARPETA_ESPALDA, f"{nombre}.png"))
    estado = "OK" if (ok_f and ok_e) else f"FALLO (frente={ok_f}, espalda={ok_e})"
    print(f"{nombre}.png -> {estado}")