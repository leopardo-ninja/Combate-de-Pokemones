# Paquete de interfaz
#
# utilidades   -> pos_virtual, dibujar_resalte, separar_texto_en_lineas, Boton
# recursos     -> carga y caché de imágenes (pokémons, fondos, bases, cajas)
# menu         -> menú principal (dibujo y botones)
# arena        -> EscenaArena (formato + escenario)
# seleccion    -> EscenaSeleccion (elegir equipo)
# pokedex      -> EscenaPokedex
# ficha        -> ficha de pokémon (compartida por la Pokédex y las estadísticas)
# estadisticas -> pantalla de estadísticas del equipo
# combate      -> EscenaCombate

from .utilidades import pos_virtual, dibujar_resalte, separar_texto_en_lineas, Boton
from .recursos import obtener_pokemon, obtener_fondo, obtener_fondo_escenario, obtener_vista_previa
from .menu import dibujar_menu_principal, crear_botones_menu
from .arena import EscenaArena
from .seleccion import EscenaSeleccion
from .pokedex import EscenaPokedex
from .estadisticas import dibujar_estadisticas, clic_comenzar
from .combate import EscenaCombate