# ===== TEMA: Modularidad (Clase 10) =====
# Se importan módulos de Python (random, sys, pygame) y propios (ui, sonido, config, motor_combate)
import random
import sys
import pygame
import ui
import sonido

from config import (
    ANCHO_VIRTUAL, ALTO_VIRTUAL, ANCHO_REAL, ALTO_REAL, MODO_VENTANA, AZUL_OSCURO,
)
from motor_combate import Combate


# ===== TEMA: Funciones (Clase 7) =====
# Sin parámetros ni retorno (void): solo produce un efecto (sonido)
# Reproduce el sonido de selección que se usa en todos los menús
def sonido_seleccion():
    sonido.efecto("interfaz/select_1")     # Sonido al darle al seleccionar


# ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) =====
# if/elif sobre la tecla; 'in' con una tupla; retorna una acción o None
# Traduce una tecla del combate a una acción (la misma que produce un clic).
# Las flechas solo mueven el botón resaltado; ENTER elige el resaltado; ESC vuelve.
def tecla_a_accion(tecla, escena):
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


# ===== TEMA: Funciones (Clase 7) + Condicionales (Clase 4) =====
# Cadena if/elif según la acción recibida
# Ejecuta sobre el motor una acción de combate (venga del teclado o del mouse).
def aplicar_accion(accion, combate, modo_juego, escena):
    # ===== TEMA: Algoritmos: pre y post condiciones (Clase 2) =====
    # Pre-condición: si no se cumple, la función termina sin hacer nada
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
    # ===== TEMA: Tuplas (Clase 11) =====
    # tipo, idx = accion desempaqueta la tupla
    # Las acciones con dato llegan como tupla: ("habilidad", indice) o ("pokemon", indice)
    elif isinstance(accion, tuple):
        tipo, idx = accion
        if tipo == "habilidad":
            # ===== TEMA: Condicionales (Clase 4) + Algoritmos: pre y post condiciones (Clase 2) =====
            # Si la habilidad no está disponible (el motor retorna None) no se anima nada: se avisa y se vuelve al menú principal
            habilidad = combate.habilidad_para_jugador(idx)
            if habilidad is None:
                # El motor explica el motivo: sin PP, energía insuficiente (habilidad fuerte) o escudo ya activo
                combate.mensaje = combate.mensaje_no_disponible(idx)
                combate.sub_menu = "principal"
                return
            # ===== TEMA: Funciones (Clase 7) =====
            # lambda: se pasa una función como argumento para ejecutarla al impactar
            # Se anima la habilidad y el motor aplica el daño justo al impactar
            escena.lanzar_habilidad("jugador", habilidad, lambda: combate.ejecutar_turno(idx),
                                    f"¡{combate.nombre_jugador.capitalize()} usó {habilidad[0]}!")
        # Cambia el Pokémon activo del jugador
        elif tipo == "pokemon":
            combate.cambiar_pokemon_jugador(idx)


# ===== TEMA: Funciones (Clase 7) + Modularidad (Clase 10) =====
# main() agrupa todo el programa; se invoca al final del archivo
def main():
    # ===== TEMA: Condicionales (Clase 4) + Pygame (fuera de temario) =====
    # if/else según MODO_VENTANA; creación de la ventana
    # Crea la ventana real: de tamaño fijo en modo ventana o a pantalla completa si no
    if MODO_VENTANA:
        pantalla_real = pygame.display.set_mode((ANCHO_REAL, ALTO_REAL))
    else:
        # Pantalla completa real (el sistema estirará la superficie virtual)
        pantalla_real = pygame.display.set_mode((ANCHO_REAL, ALTO_REAL), pygame.FULLSCREEN | pygame.SCALED)
    # Superficie virtual de 1920x1080 donde se dibuja todo; al final del frame se escala a la pantalla real
    pantalla = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
    pygame.display.set_caption("Combate Proyecto - Pokémon Añil Ultimate Edition (Responsivo)")

    # ===== TEMA: Expresiones y operadores (Clase 3) =====
    # Variables de estado: cadenas, números y booleanos
    # estado_app decide qué pantalla se muestra: menu_principal, arena, seleccion, estadisticas, combate o pokedex
    estado_app = "menu_principal"
    modo_juego = "1v1"
    escenario_sel = 0
    escena_arena = ui.EscenaArena()

    # Pantalla de selección de equipo: se crea al salir de la arena; equipo_seleccionado se llena al completar el equipo
    seleccion_idx = 0
    escena_seleccion = None
    equipo_seleccionado = []

    # Pokédex: usa la misma cuadrícula que la selección; se crea al entrar desde el menú
    escena_pokedex = None

    # Reloj para limitar el juego a 60 fotogramas por segundo
    reloj = pygame.time.Clock()
    # ejecutando: el bucle principal corre mientras sea True
    # combate / escena_combate se crean al empezar una pelea; retraso_ia cuenta frames antes de que ataque el rival
    ejecutando = True
    combate = None
    escena_combate = None
    retraso_ia = 0

    # Botones del menú principal (se definen en ui/menu.py)
    botones_menu = ui.crear_botones_menu()

    # ===== TEMA: Bucles (Clase 4) =====
    # while ejecutando: se repite hasta que sea False
    # Bucle principal: cada vuelta procesa los eventos, actualiza y dibuja un frame
    while ejecutando:
        # Limpia el frame anterior
        pantalla.fill(AZUL_OSCURO)
        # Se pone en True cuando el usuario confirma una opción del menú principal (ENTER o clic)
        activar_opcion = False
        # Se pone en True al confirmar COMENZAR en la pantalla de estadísticas (ENTER, ESPACIO o clic)
        comenzar_combate = False

        # ===== TEMA: Bucles (Clase 4) + Condicionales (Clase 4) =====
        # for recorre los eventos; if/elif encadenados según el tipo de evento y la pantalla
        # Revisa todos los eventos pendientes (teclado, mouse, cerrar ventana)
        for evento in pygame.event.get():
            # accion_combate guarda lo que el usuario pidió en el combate (por mouse o teclado)
            accion_combate = None
            if evento.type == pygame.QUIT:
                ejecutando = False

            # ===== TEMA: Bucles (Clase 4) =====
            # for + enumerate recorre la lista de botones
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
                    # Clic sobre un formato (1v1 / 3v3) o un escenario: suena la selección
                    resultado = escena_arena.clic(evento.pos)
                    if resultado is not None:
                        sonido_seleccion()
                    # Clic sobre un escenario: se guardan formato y escenario y se pasa a elegir equipo
                    if resultado == "continuar":
                        modo_juego = escena_arena.modo
                        escenario_sel = escena_arena.escenario
                        estado_app = "seleccion"
                        seleccion_idx = 0
                        escena_seleccion = ui.EscenaSeleccion(modo_juego)
                # Clic derecho = volver al menú principal
                elif evento.button == 3:
                    estado_app = "menu_principal"
                    seleccion_idx = 0

            # --- Mouse en la selección de pokémons ---
            elif evento.type == pygame.MOUSEMOTION and estado_app == "seleccion":
                escena_seleccion.pasar_mouse(evento.pos)

            elif evento.type == pygame.MOUSEWHEEL and estado_app == "seleccion":
                escena_seleccion.desplazar(evento.y)

            elif evento.type == pygame.MOUSEBUTTONDOWN and estado_app == "seleccion":
                if evento.button == 1:
                    # Clic sobre un pokémon: lo elige (o lo quita si ya estaba); al completar el equipo se pasa a las estadísticas
                    resultado = escena_seleccion.clic(evento.pos)
                    if resultado is not None:
                        sonido_seleccion()
                    if resultado == "completo":
                        equipo_seleccionado = list(escena_seleccion.equipo)
                        estado_app = "estadisticas"
                # Clic derecho = volver a la arena (como ESC)
                elif evento.button == 3:
                    estado_app = "arena"

            # --- Mouse en las estadísticas del equipo ---
            elif evento.type == pygame.MOUSEBUTTONDOWN and estado_app == "estadisticas":
                if evento.button == 1 and ui.clic_comenzar(evento.pos):
                    comenzar_combate = True
                # Clic derecho = volver a la selección de equipo (como ESC)
                elif evento.button == 3:
                    escena_seleccion.deshacer_ultimo()
                    estado_app = "seleccion"

            # --- Mouse en la pokédex ---
            elif evento.type == pygame.MOUSEMOTION and estado_app == "pokedex":
                escena_pokedex.pasar_mouse(evento.pos)

            elif evento.type == pygame.MOUSEWHEEL and estado_app == "pokedex":
                escena_pokedex.desplazar(evento.y)

            elif evento.type == pygame.MOUSEBUTTONDOWN and estado_app == "pokedex":
                if evento.button == 1:
                    # Clic sobre un pokémon: lo resalta y su ficha aparece en el panel
                    if escena_pokedex.clic(evento.pos) is not None:
                        sonido_seleccion()
                # Clic derecho = volver al menú principal (como ESC)
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
            # ===== TEMA: Condicionales (Clase 4) + Expresiones y operadores (Clase 3) =====
            # if/elif anidados por pantalla; % (módulo) hace circular la selección
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
                            escena_seleccion = ui.EscenaSeleccion(modo_juego)
                    else:
                        escena_arena.mover(evento.key)

                elif estado_app == "seleccion":
                    if evento.key == pygame.K_ESCAPE:
                        estado_app = "arena"
                    elif evento.key == pygame.K_RETURN:
                        sonido_seleccion()
                        # Elige (o quita) el pokémon resaltado; con el equipo completo se muestran las estadísticas
                        if escena_seleccion.elegir() == "completo":
                            equipo_seleccionado = list(escena_seleccion.equipo)
                            estado_app = "estadisticas"
                    else:
                        escena_seleccion.mover(evento.key)

                elif estado_app == "estadisticas":
                    if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                        comenzar_combate = True
                    elif evento.key == pygame.K_ESCAPE:
                        escena_seleccion.deshacer_ultimo()
                        estado_app = "seleccion"

                elif estado_app == "combate":
                    accion_combate = tecla_a_accion(evento.key, escena_combate)

                elif estado_app == "pokedex":
                    if evento.key == pygame.K_ESCAPE:
                        estado_app = "menu_principal"
                        seleccion_idx = 0
                    else:
                        escena_pokedex.mover(evento.key)

            # --- Seleccion combate ---
            # Si hubo una acción de combate: MENU vuelve al menú principal; el resto se aplica al motor
            if accion_combate is not None:
                if accion_combate == "menu":
                    sonido_seleccion()
                    estado_app = "menu_principal"
                    seleccion_idx = 0
                else:
                    aplicar_accion(accion_combate, combate, modo_juego, escena_combate)

        # ===== TEMA: POO (Clase 16) =====
        # Se crean objetos: Combate (motor) y EscenaCombate (dibujo)
        # --- Comenzar combate (desde las estadísticas) ---
        if comenzar_combate and estado_app == "estadisticas":
            sonido_seleccion()
            # Crea el motor del combate y la escena que lo dibuja
            combate = Combate(equipo_seleccionado, modo_juego)
            escena_combate = ui.EscenaCombate(combate, escenario_sel)
            estado_app = "combate"

        # ===== TEMA: Condicionales (Clase 4) =====
        # if/elif según el botón elegido
        # --- Seleccion Menu ---
        if activar_opcion and estado_app == "menu_principal":
            sonido_seleccion()
            if seleccion_idx == 0:
                estado_app = "arena"
            elif seleccion_idx == 1:
                estado_app = "pokedex"
                escena_pokedex = ui.EscenaPokedex()
            elif seleccion_idx == 2:
                ejecutando = False

        # ===== TEMA: Condicionales (Clase 4) + Modularidad (Clase 10) =====
        # if/elif elige qué pantalla dibujar llamando a funciones y objetos del paquete ui
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
            escena_seleccion.dibujar(pantalla)

        elif estado_app == "estadisticas":
            ui.dibujar_estadisticas(pantalla, equipo_seleccionado)

        elif estado_app == "combate":
            # ===== TEMA: Condicionales (Clase 4) + Listas (Clase 11) =====
            # Contador de frames; random.choice sobre la lista de habilidades (tuplas)
            # Turno del rival: espera 60 frames (1 segundo) y lanza una habilidad al azar con su animación
            if combate.turno == "ia" and not escena_combate.ocupado():
                retraso_ia += 1
                if retraso_ia > 60:
                    # ===== TEMA: Funciones (Clase 7) + Listas (Clase 11) =====
                    # El motor elige al azar solo entre las habilidades con PP (antes se elegía de toda la lista con random.choice)
                    habilidad_ia = combate.elegir_habilidad_ia()
                    escena_combate.lanzar_habilidad(
                        "ia", habilidad_ia, lambda elegida=habilidad_ia: combate.turno_ia(elegida),
                        f"¡{combate.nombre_ia.capitalize()} rival usó {habilidad_ia[0]}!")
                    retraso_ia = 0
            escena_combate.dibujar(pantalla)

        elif estado_app == "pokedex":
            escena_pokedex.dibujar(pantalla)

        # ===== TEMA: Pygame (fuera de temario) =====
        # Escala la superficie virtual a la pantalla real
        # Escalar el juego a la resolucion del monitor
        pantalla_real.blit(pygame.transform.smoothscale(pantalla, (ANCHO_REAL, ALTO_REAL)), (0, 0))
        pygame.display.flip()
        # Limita el bucle a 60 fotogramas por segundo
        reloj.tick(60)

    # Fuera del bucle: se cierra pygame y el programa
    pygame.quit()
    sys.exit()


# ===== TEMA: Modularidad (Clase 10) =====
# __name__ == '__main__' ejecuta main() solo si el archivo se corre directamente, no al importarlo
# Solo arranca el juego si se ejecuta este archivo directamente
if __name__ == "__main__":
    main()