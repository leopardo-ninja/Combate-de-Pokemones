import random
import sys
import pygame
import ui
import sonido

from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL, ANCHO_REAL, ALTO_REAL, MODO_VENTANA, AZUL_OSCURO,
)
from motor_combate import Combate
from pokemons import SECCIONES_POKEMON, LISTA_PLANA_POKES


# Reproduce el sonido de selección que se usa en todos los menús
def sonido_seleccion():
    sonido.efecto("interfaz/select_1")     # Sonido al darle al seleccionar


def tecla_a_accion(tecla, escena):
    """Traduce una tecla del combate a una acción (la misma que produce un clic).

    Las flechas solo mueven el botón resaltado; ENTER elige el resaltado; ESC vuelve.
    """
    # Flechas: solo mueven el botón resaltado
    if tecla in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
        escena.mover_seleccion(tecla)
    # ENTER: elige el botón resaltado
    elif tecla == pygame.K_RETURN:
        return escena.accion_seleccionada()
    # ESC: volver al menú anterior
    elif tecla == pygame.K_ESCAPE:
        return "volver"
    return None


def aplicar_accion(accion, combate, modo_juego, escena):
    """Ejecuta sobre el motor una acción de combate (venga del teclado o del mouse)."""
    # No se acepta nada si no es el turno del jugador o si hay una animación en curso
    if combate.turno != "jugador" or escena.ocupado():
        return
    # Todas las acciones suenan menos volver
    if accion != "volver":
        sonido_seleccion()
    # LUCHAR: abre el submenú con las habilidades
    if accion == "luchar":
        combate.sub_menu = "luchar"
    # CAMBIAR: abre el submenú del equipo (solo tiene sentido en 3v3)
    elif accion == "cambiar":
        if modo_juego == "3v3":
            combate.sub_menu = "cambiar"
        else:
            combate.mensaje = "¡Solo tienes 1 Pokémon en 1v1!"
    # VOLVER: regresa al menú principal del combate
    elif accion == "volver":
        combate.sub_menu = "principal"
    # Las acciones con dato llegan como tupla: ("habilidad", indice) o ("pokemon", indice)
    elif isinstance(accion, tuple):
        tipo, idx = accion
        if tipo == "habilidad":
            habilidad = combate.datos_jugador["habilidades"][idx]
            # Se anima la habilidad y el motor aplica el daño justo al impactar
            escena.lanzar_habilidad("jugador", habilidad, lambda: combate.ejecutar_turno(idx),
                                    f"¡{combate.nombre_jugador.capitalize()} usó {habilidad[0]}!")
        # Cambia el Pokémon activo del jugador
        elif tipo == "pokemon":
            combate.cambiar_pokemon_jugador(idx)


def main():
    # Crea la ventana real: de tamaño fijo en modo ventana o a pantalla completa si no
    if MODO_VENTANA:
        pantalla_real = pygame.display.set_mode((ANCHO_REAL, ALTO_REAL))
    else:
        # Pantalla completa real (el sistema estirará la superficie virtual)
        pantalla_real = pygame.display.set_mode((ANCHO_REAL, ALTO_REAL), pygame.FULLSCREEN | pygame.SCALED)
    # Superficie virtual de 1920x1080 donde se dibuja todo; al final del frame se escala a la pantalla real
    pantalla = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
    pygame.display.set_caption("Combate Proyecto - Pokémon Añil Ultimate Edition (Responsivo)")

    # estado_app decide qué pantalla se muestra: menu_principal, arena, seleccion, estadisticas, combate o biblioteca
    estado_app = "menu_principal"
    modo_juego = "1v1"
    escenario_sel = 0
    escena_arena = ui.EscenaArena()

    # Pantalla de selección de equipo: elemento resaltado, scroll de la lista y equipo elegido hasta ahora
    seleccion_idx = 0
    scroll_offset_sel = 0
    equipo_seleccionado = []

    # Biblioteca: sección (tipo) y Pokémon resaltados, si la ficha está abierta y el scroll
    lib_seccion_idx = 0
    lib_pokemon_idx = 0
    lib_detalle = False
    scroll_offset_lib = 0

    # Reloj para limitar el juego a 60 fotogramas por segundo
    reloj = pygame.time.Clock()
    # ejecutando: el bucle principal corre mientras sea True
    # combate / escena_combate se crean al empezar una pelea; retraso_ia cuenta frames antes de que ataque el rival
    ejecutando = True
    combate = None
    escena_combate = None
    retraso_ia = 0

    # Lista de tipos (FUEGO, AGUA...) para recorrer la biblioteca por secciones
    tipo_claves = list(SECCIONES_POKEMON.keys())

    # Botones del menú principal (x, y, ancho, alto, texto), uno debajo del otro
    textos_menu = ["Modo Arena", "Biblioteca de Pokémon", "Salir"]
    botones_menu = [ui.Boton(710, 430 + i * 90, 500, 70, texto) for i, texto in enumerate(textos_menu)]

    # Bucle principal: cada vuelta procesa los eventos, actualiza y dibuja un frame
    while ejecutando:
        # Limpia el frame anterior
        pantalla.fill(AZUL_OSCURO)
        # Se pone en True cuando el usuario confirma una opción del menú principal (ENTER o clic)
        activar_opcion = False

        # Revisa todos los eventos pendientes (teclado, mouse, cerrar ventana)
        for evento in pygame.event.get():
            # accion_combate guarda lo que el usuario pidió en el combate (por mouse o teclado)
            accion_combate = None
            if evento.type == pygame.QUIT:
                ejecutando = False

            # --- Mouse en el menú principal ---
            elif evento.type == pygame.MOUSEMOTION and estado_app == "menu_principal":
                for i, boton in enumerate(botones_menu):
                    if boton.contiene(evento.pos):
                        seleccion_idx = i

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and estado_app == "menu_principal":
                for i, boton in enumerate(botones_menu):
                    if boton.contiene(evento.pos):
                        seleccion_idx = i
                        activar_opcion = True

            # --- Mouse en la arena ---
            elif evento.type == pygame.MOUSEMOTION and estado_app == "arena":
                escena_arena.pasar_mouse(evento.pos)

            elif evento.type == pygame.MOUSEBUTTONDOWN and estado_app == "arena":
                if evento.button == 1:
                    # Clic sobre un escenario: se guardan formato y escenario y se pasa a elegir equipo
                    if escena_arena.clic(evento.pos) == "continuar":
                        sonido_seleccion()
                        modo_juego = escena_arena.modo
                        escenario_sel = escena_arena.escenario
                        estado_app = "seleccion"
                        seleccion_idx = 0
                        scroll_offset_sel = 0
                        equipo_seleccionado = []
                # Clic derecho = volver al menú principal
                elif evento.button == 3:
                    estado_app = "menu_principal"
                    seleccion_idx = 0

            # --- Mouse en el combate ---
            elif evento.type == pygame.MOUSEMOTION and estado_app == "combate":
                escena_combate.seleccionar_en(evento.pos)

            elif evento.type == pygame.MOUSEBUTTONDOWN and estado_app == "combate":
                if evento.button == 1:
                    accion_combate = escena_combate.accion_en(evento.pos)
                elif evento.button == 3:  # clic derecho = volver (como ESC)
                    accion_combate = "volver"

            # --- Teclado ---
            # Teclado: cada pantalla interpreta las teclas a su manera
            elif evento.type == pygame.KEYDOWN:
                if estado_app == "menu_principal":
                    if evento.key == pygame.K_DOWN:
                        seleccion_idx = (seleccion_idx + 1) % len(botones_menu)
                    elif evento.key == pygame.K_UP:
                        seleccion_idx = (seleccion_idx - 1) % len(botones_menu)
                    elif evento.key == pygame.K_RETURN:
                        activar_opcion = True
                    elif evento.key == pygame.K_ESCAPE:
                        ejecutando = False

                elif estado_app == "arena":
                    if evento.key == pygame.K_ESCAPE:
                        estado_app = "menu_principal"
                        seleccion_idx = 0
                    elif evento.key == pygame.K_RETURN:
                        sonido_seleccion()
                        if escena_arena.elegir() == "continuar":
                            modo_juego = escena_arena.modo
                            escenario_sel = escena_arena.escenario
                            estado_app = "seleccion"
                            seleccion_idx = 0
                            scroll_offset_sel = 0
                            equipo_seleccionado = []
                    else:
                        escena_arena.mover(evento.key)

                elif estado_app == "seleccion":
                    # El cursor recorre la lista de todos los pokémons y da la vuelta al llegar a los extremos
                    limite = len(LISTA_PLANA_POKES)
                    if evento.key == pygame.K_ESCAPE:
                        estado_app = "arena"
                    elif evento.key == pygame.K_DOWN:
                        seleccion_idx = (seleccion_idx + 1) % limite
                    elif evento.key == pygame.K_UP:
                        seleccion_idx = (seleccion_idx - 1) % limite
                    elif evento.key == pygame.K_RETURN:
                        sonido_seleccion()
                        pokemon_elegido = LISTA_PLANA_POKES[seleccion_idx]
                        # Evita repetir el mismo Pokémon en el equipo
                        if pokemon_elegido not in equipo_seleccionado:
                            equipo_seleccionado.append(pokemon_elegido)

                        # 1v1 necesita 1 Pokémon y 3v3 necesita 3; al completarlos se muestran las estadísticas
                        meta_equipo = 1 if modo_juego == "1v1" else 3
                        if len(equipo_seleccionado) == meta_equipo:
                            estado_app = "estadisticas"

                    # Calcula la altura (y) del Pokémon resaltado dentro de la lista, para mover el scroll y que no se salga de la vista
                    y_item_sel = 0
                    idx_actual = 0
                    for tipo_seccion, pokemons_seccion in SECCIONES_POKEMON.items():
                        y_item_sel += 45
                        for nombre_pokemon in pokemons_seccion:
                            if idx_actual == seleccion_idx:
                                break
                            y_item_sel += 50
                            idx_actual += 1
                        if idx_actual == seleccion_idx:
                            break
                        y_item_sel += 20

                    # Si se sale por abajo, baja el scroll; si se sale por arriba, lo sube
                    if y_item_sel - scroll_offset_sel > 800:
                        scroll_offset_sel = y_item_sel - 800
                    elif y_item_sel - scroll_offset_sel < 60:
                        scroll_offset_sel = max(0, y_item_sel - 60)

                elif estado_app == "estadisticas":
                    if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                        sonido_seleccion()
                        # Crea el motor del combate y la escena que lo dibuja
                        combate = Combate(equipo_seleccionado, modo_juego)
                        escena_combate = ui.EscenaCombate(combate, escenario_sel)
                        estado_app = "combate"

                elif estado_app == "combate":
                    accion_combate = tecla_a_accion(evento.key, escena_combate)

                elif estado_app == "biblioteca":
                    # Biblioteca: tipo (sección) que se está viendo y sus pokémons
                    tipo_actual = tipo_claves[lib_seccion_idx]
                    pokemons_actuales = SECCIONES_POKEMON[tipo_actual]

                    # Con la ficha abierta, ESC o ENTER la cierran
                    if lib_detalle:
                        if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                            lib_detalle = False
                    else:
                        # Las tarjetas se muestran en 2 columnas por fila.
                        # Abajo: baja una fila; si no hay más filas en la sección, pasa a la siguiente
                        if evento.key == pygame.K_DOWN:
                            # fila = índice // 2 y columna = índice % 2 (dos tarjetas por fila)
                            fila = lib_pokemon_idx // 2
                            if fila < 1:
                                nuevo_indice = lib_pokemon_idx + 2
                                if nuevo_indice < len(pokemons_actuales):
                                    lib_pokemon_idx = nuevo_indice
                                else:
                                    lib_pokemon_idx = len(pokemons_actuales) - 1
                            elif fila == 1:
                                if len(pokemons_actuales) > 4:
                                    lib_pokemon_idx = 4
                                else:
                                    lib_seccion_idx = (lib_seccion_idx + 1) % len(tipo_claves)
                                    lib_pokemon_idx = 0
                            else:
                                lib_seccion_idx = (lib_seccion_idx + 1) % len(tipo_claves)
                                lib_pokemon_idx = 0

                        elif evento.key == pygame.K_UP:
                            fila = lib_pokemon_idx // 2
                            if fila > 0:
                                lib_pokemon_idx -= 2
                            else:
                                lib_seccion_idx = (lib_seccion_idx - 1) % len(tipo_claves)
                                pokemons_seccion_anterior = SECCIONES_POKEMON[tipo_claves[lib_seccion_idx]]
                                lib_pokemon_idx = len(pokemons_seccion_anterior) - 1

                        elif evento.key == pygame.K_RIGHT:
                            columna = lib_pokemon_idx % 2
                            if columna == 0 and lib_pokemon_idx + 1 < len(pokemons_actuales):
                                lib_pokemon_idx += 1

                        elif evento.key == pygame.K_LEFT:
                            columna = lib_pokemon_idx % 2
                            if columna == 1:
                                lib_pokemon_idx -= 1

                        elif evento.key == pygame.K_RETURN:
                            sonido_seleccion()
                            lib_detalle = True
                        elif evento.key == pygame.K_ESCAPE:
                            estado_app = "menu_principal"

                        # Ajusta el scroll para que la tarjeta resaltada siga visible
                        y_tarjeta = lib_seccion_idx * 700 + 50 + (lib_pokemon_idx // 2) * 190
                        if y_tarjeta - scroll_offset_lib > 700:
                            scroll_offset_lib = y_tarjeta - 700
                        elif y_tarjeta - scroll_offset_lib < 80:
                            scroll_offset_lib = max(0, y_tarjeta - 80)

            # --- Seleccion combate ---
            # Si hubo una acción de combate: MENU vuelve al menú principal; el resto se aplica al motor
            if accion_combate is not None:
                if accion_combate == "menu":
                    sonido_seleccion()
                    estado_app = "menu_principal"
                    seleccion_idx = 0
                else:
                    aplicar_accion(accion_combate, combate, modo_juego, escena_combate)

        # --- Seleccion Menu ---
        if activar_opcion and estado_app == "menu_principal":
            sonido_seleccion()
            if seleccion_idx == 0:
                estado_app = "arena"
            elif seleccion_idx == 1:
                estado_app = "biblioteca"
                lib_seccion_idx = 0
                lib_pokemon_idx = 0
                lib_detalle = False
                scroll_offset_lib = 0
            elif seleccion_idx == 2:
                ejecutando = False

        # ================= RENDERIZADO VISUAL RESPONSIVO =================
        if estado_app != "combate":     # Detiene el sonido de vida baja si el combate acaba
            sonido.parar_loop("efectos/health_low_loop")

        if estado_app == "combate":
            # La música de batalla solo suena en combate
            sonido.musica("musica/battle_1")
        else: 
            sonido.parar_musica()

        if estado_app == "menu_principal":
            ui.dibujar_menu_principal(pantalla, botones_menu, seleccion_idx)

        elif estado_app == "arena":
            escena_arena.dibujar(pantalla)

        elif estado_app == "seleccion":
            ui.dibujar_seleccion(pantalla, equipo_seleccionado, seleccion_idx, scroll_offset_sel, modo_juego)

        elif estado_app == "estadisticas":
            ui.dibujar_estadisticas(pantalla, equipo_seleccionado)

        elif estado_app == "combate":
            # Turno del rival: espera 60 frames (1 segundo) y lanza una habilidad al azar con su animación
            if combate.turno == "ia" and not escena_combate.ocupado():
                retraso_ia += 1
                if retraso_ia > 60:
                    habilidad_ia = random.choice(combate.datos_ia["habilidades"])
                    escena_combate.lanzar_habilidad(
                        "ia", habilidad_ia, lambda elegida=habilidad_ia: combate.turno_ia(elegida),
                        f"¡{combate.nombre_ia.capitalize()} rival usó {habilidad_ia[0]}!")
                    retraso_ia = 0
            escena_combate.dibujar(pantalla)

        elif estado_app == "biblioteca":
            ui.dibujar_biblioteca(pantalla, tipo_claves, scroll_offset_lib, lib_detalle, lib_seccion_idx, lib_pokemon_idx)

        # Escalar el juego a la resolucion del monitor
        pantalla_real.blit(pygame.transform.smoothscale(pantalla, (ANCHO_REAL, ALTO_REAL)), (0, 0))
        pygame.display.flip()
        # Limita el bucle a 60 fotogramas por segundo
        reloj.tick(60)

    # Fuera del bucle: se cierra pygame y el programa
    pygame.quit()
    sys.exit()


# Solo arranca el juego si se ejecuta este archivo directamente
if __name__ == "__main__":
    main()