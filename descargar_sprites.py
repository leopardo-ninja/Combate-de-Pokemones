import os
import urllib.request

pokemons = {
    "charmander": 4,
    "vulpix": 37,
    "growlithe": 58,
    "ponyta": 77,
    "magmar": 126,
    "squirtle": 7,
    "psyduck": 54,
    "poliwag": 60,
    "horsea": 116,
    "staryu": 120,
    "bulbasaur": 1,
    "oddish": 43,
    "bellsprout": 69,
    "tangela": 114,
    "exeggcute": 102,
    "pikachu": 25,
    "magnemite": 81,
    "voltorb": 100,
    "electabuzz": 125,
    "mareep": 179,
    "sandshrew": 27,
    "geodude": 74,
    "cubone": 104,
    "phanpy": 231,
    "diglett": 50,
}

os.makedirs("assets/pokemons/frente", exist_ok=True)
os.makedirs("assets/pokemons/espalda", exist_ok=True)

print("Iniciando la descarga de los sprites...")

for nombre, pok_id in pokemons.items():
  try:
    url_frente = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pok_id}.png"
    urllib.request.urlretrieve(
        url_frente, f"assets/pokemons/frente/{nombre}.png"
    )

    url_espalda = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/{pok_id}.png"
    urllib.request.urlretrieve(
        url_espalda, f"assets/pokemons/espalda/{nombre}.png"
    )

    print(f"[OK] Descargado: {nombre}")
  except Exception as e:
    print(f"[ERROR] No se pudo descargar a {nombre}: {e}")

print("\n¡Listo! Todas las imágenes se han guardado con éxito.")
