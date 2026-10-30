import sys
import pygame
import ui

from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL, ANCHO_REAL, ALTO_REAL, MODO_VENTANA, AZUL_OSCURO,
)
from motor_combate import Combate
from pokemons import SECCIONES_POKEMON, LISTA_PLANA_POKES


def tecla_a_accion(tecla, escena):
    """Traduce una tecla del combate a una acción (la misma que produce un clic).

    Las flechas solo mueven el botón resaltado; ENTER elige el resaltado; ESC vuelve.
    """
    if tecla in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
        escena.mover_seleccion(tecla)
    elif tecla == pygame.K_RETURN:
        return escena.accion_seleccionada()
    elif tecla == pygame.K_ESCAPE:
        return "volver"
    return None


def aplicar_accion(accion, combate, modo_juego):
    """Ejecuta sobre el motor una acción de combate (venga del teclado o del mouse)."""
    if combate.turno != "jugador":
        return
    if accion == "luchar":
        combate.sub_menu = "luchar"
    elif accion == "cambiar":
        if modo_juego == "3v3":
            combate.sub_menu = "cambiar"
        else:
            combate.mensaje = "¡Solo tienes 1 Pokémon en 1v1!"
    elif accion == "volver":
        combate.sub_menu = "principal"
    elif isinstance(accion, tuple):
        tipo, idx = accion
        if tipo == "habilidad":
            combate.ejecutar_turno(idx)
        elif tipo == "pokemon":
            combate.cambiar_pokemon_jugador(idx)


def main():
    if MODO_VENTANA:
        pantalla_real = pygame.display.set_mode((ANCHO_REAL, ALTO_REAL))
    else:
        # Pantalla completa real (el sistema estirará la superficie virtual)
        pantalla_real = pygame.display.set_mode((ANCHO_REAL, ALTO_REAL), pygame.FULLSCREEN | pygame.SCALED)
    pantalla = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
    pygame.display.set_caption("Combate Proyecto - Pokémon Añil Ultimate Edition (Responsivo)")

    estado_app = "menu_principal"
    modo_juego = "1v1"
    escenario_sel = 0
    escena_arena = ui.EscenaArena()

    seleccion_idx = 0
    scroll_offset_sel = 0
    equipo_seleccionado = []

    lib_sec_idx = 0
    lib_poke_idx = 0
    lib_detalle = False
    scroll_offset_lib = 0

    reloj = pygame.time.Clock()
    ejecutando = True
    combate = None
    escena_combate = None
    retraso_ia = 0

    tipo_claves = list(SECCIONES_POKEMON.keys())

    textos_menu = ["Modo Arena", "Biblioteca de Pokémon", "Salir"]
    botones_menu = [ui.Boton(710, 430 + i * 90, 500, 70, t) for i, t in enumerate(textos_menu)]

    while ejecutando:
        pantalla.fill(AZUL_OSCURO)
        activar_opcion = False

        for evento in pygame.event.get():
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
                    if escena_arena.clic(evento.pos) == "continuar":
                        modo_juego = escena_arena.modo
                        escenario_sel = escena_arena.escenario
                        estado_app = "seleccion"
                        seleccion_idx = 0
                        scroll_offset_sel = 0
                        equipo_seleccionado = []
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
                    limite = len(LISTA_PLANA_POKES)
                    if evento.key == pygame.K_ESCAPE:
                        estado_app = "arena"
                    elif evento.key == pygame.K_DOWN:
                        seleccion_idx = (seleccion_idx + 1) % limite
                    elif evento.key == pygame.K_UP:
                        seleccion_idx = (seleccion_idx - 1) % limite
                    elif evento.key == pygame.K_RETURN:
                        poke_elegido = LISTA_PLANA_POKES[seleccion_idx]
                        if poke_elegido not in equipo_seleccionado:
                            equipo_seleccionado.append(poke_elegido)

                        meta_equipo = 1 if modo_juego == "1v1" else 3
                        if len(equipo_seleccionado) == meta_equipo:
                            estado_app = "estadisticas"

                    y_item_sel = 0
                    idx_actual = 0
                    for tipo_sec, pokes in SECCIONES_POKEMON.items():
                        y_item_sel += 45
                        for p_name in pokes:
                            if idx_actual == seleccion_idx:
                                break
                            y_item_sel += 50
                            idx_actual += 1
                        if idx_actual == seleccion_idx:
                            break
                        y_item_sel += 20

                    if y_item_sel - scroll_offset_sel > 800:
                        scroll_offset_sel = y_item_sel - 800
                    elif y_item_sel - scroll_offset_sel < 60:
                        scroll_offset_sel = max(0, y_item_sel - 60)

                elif estado_app == "estadisticas":
                    if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                        combate = Combate(equipo_seleccionado, modo_juego)
                        escena_combate = ui.EscenaCombate(combate, escenario_sel)
                        estado_app = "combate"

                elif estado_app == "combate":
                    accion_combate = tecla_a_accion(evento.key, escena_combate)

                elif estado_app == "biblioteca":
                    tipo_actual = tipo_claves[lib_sec_idx]
                    pokes_actuales = SECCIONES_POKEMON[tipo_actual]

                    if lib_detalle:
                        if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                            lib_detalle = False
                    else:
                        if evento.key == pygame.K_DOWN:
                            row = lib_poke_idx // 2
                            if row < 1:
                                nuevo_idx = lib_poke_idx + 2
                                if nuevo_idx < len(pokes_actuales):
                                    lib_poke_idx = nuevo_idx
                                else:
                                    lib_poke_idx = len(pokes_actuales) - 1
                            elif row == 1:
                                if len(pokes_actuales) > 4:
                                    lib_poke_idx = 4
                                else:
                                    lib_sec_idx = (lib_sec_idx + 1) % len(tipo_claves)
                                    lib_poke_idx = 0
                            else:
                                lib_sec_idx = (lib_sec_idx + 1) % len(tipo_claves)
                                lib_poke_idx = 0

                        elif evento.key == pygame.K_UP:
                            row = lib_poke_idx // 2
                            if row > 0:
                                lib_poke_idx -= 2
                            else:
                                lib_sec_idx = (lib_sec_idx - 1) % len(tipo_claves)
                                prev_pokes = SECCIONES_POKEMON[tipo_claves[lib_sec_idx]]
                                lib_poke_idx = len(prev_pokes) - 1

                        elif evento.key == pygame.K_RIGHT:
                            col = lib_poke_idx % 2
                            if col == 0 and lib_poke_idx + 1 < len(pokes_actuales):
                                lib_poke_idx += 1

                        elif evento.key == pygame.K_LEFT:
                            col = lib_poke_idx % 2
                            if col == 1:
                                lib_poke_idx -= 1

                        elif evento.key == pygame.K_RETURN:
                            lib_detalle = True
                        elif evento.key == pygame.K_ESCAPE:
                            estado_app = "menu_principal"

                        y_tarjeta = lib_sec_idx * 700 + 50 + (lib_poke_idx // 2) * 190
                        if y_tarjeta - scroll_offset_lib > 700:
                            scroll_offset_lib = y_tarjeta - 700
                        elif y_tarjeta - scroll_offset_lib < 80:
                            scroll_offset_lib = max(0, y_tarjeta - 80)

            # --- Seleccion combate ---
            if accion_combate is not None:
                if accion_combate == "menu":
                    estado_app = "menu_principal"
                    seleccion_idx = 0
                else:
                    aplicar_accion(accion_combate, combate, modo_juego)

        # --- Seleccion Menu ---
        if activar_opcion and estado_app == "menu_principal":
            if seleccion_idx == 0:
                estado_app = "arena"
            elif seleccion_idx == 1:
                estado_app = "biblioteca"
                lib_sec_idx = 0
                lib_poke_idx = 0
                lib_detalle = False
                scroll_offset_lib = 0
            elif seleccion_idx == 2:
                ejecutando = False

        # ================= RENDERIZADO VISUAL RESPONSIVO =================
        if estado_app == "menu_principal":
            ui.dibujar_menu_principal(pantalla, botones_menu, seleccion_idx)

        elif estado_app == "arena":
            escena_arena.dibujar(pantalla)

        elif estado_app == "seleccion":
            ui.dibujar_seleccion(pantalla, equipo_seleccionado, seleccion_idx, scroll_offset_sel, modo_juego)

        elif estado_app == "estadisticas":
            ui.dibujar_estadisticas(pantalla, equipo_seleccionado)

        elif estado_app == "combate":
            if combate.turno == "ia":
                retraso_ia += 1
                if retraso_ia > 60:
                    combate.turno_ia()
                    retraso_ia = 0
            escena_combate.dibujar(pantalla)

        elif estado_app == "biblioteca":
            ui.dibujar_biblioteca(pantalla, tipo_claves, scroll_offset_lib, lib_detalle, lib_sec_idx, lib_poke_idx)

        # Escalar el juego a la resolucion del monitor
        pantalla_real.blit(pygame.transform.smoothscale(pantalla, (ANCHO_REAL, ALTO_REAL)), (0, 0))
        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()