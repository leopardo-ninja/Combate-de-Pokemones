# Cómo dibujar a los entrenadores

El juego carga los dibujos de esta carpeta. Cada personaje tiene la suya:

```
assets/entrenadores/
  tortuga/   busto.png   caminar.png
  leopardo/  busto.png   caminar.png
  tullio/    busto.png   caminar.png
  plantilla_caminar.png        (guías de la hoja de caminar)
```

Si un PNG no existe, el juego usa el dibujo guardado en `personajes/<nombre>.py`.

## Qué hay que dibujar

### `busto.png`: retrato para elegir personaje y para el panel del mapa
- Cuadrado y con fondo transparente. Tamaño recomendado: **112×112** (también sirven 96, 128...).
- Cabeza y hombros, con los hombros tocando el borde de abajo.
- El juego lo amplía sin suavizar, así que los píxeles se mantienen nítidos.

### `caminar.png`: el personaje en el mapa
- Hoja de **3 columnas × 4 filas**. Todos los cuadros miden lo mismo: **32×48** si se dibuja a mano (hoja de 96×192)
  o **64×96** para hojas hechas con IA (más detalle; es el tamaño con que se ve en el mapa).
- Columnas: **quieto**, **paso A** y **paso B**. El juego las anima en el orden quieto, A, quieto, B.
- Filas, de arriba hacia abajo: **abajo** (de frente), **izquierda**, **derecha**, **arriba** (de espaldas).
- Los pies van en la última fila de píxeles de cada cuadro. En el mapa el personaje mide 96 px de alto, así que un cuadro de 32×48 se dibuja al doble.
- Es el formato de RPG Maker: sirven sus tutoriales y plantillas.

## Con Piskel (gratis, en el navegador: piskelapp.com)
1. **Import** → elegir el `caminar.png` del personaje (o `plantilla_caminar.png` para empezar de cero) → "Import as spritesheet" con cuadros de **32×48**. Cada cuadro queda como un frame y se puede ver la animación.
2. Dibujar. Para calcar, se puede poner la foto en una capa de abajo con transparencia.
3. **Export** → PNG → "Spritesheet" con **3 columnas** → guardar como `caminar.png` en la carpeta del personaje.
4. Para el busto: un sprite nuevo de 112×112, dibujar y exportar como `busto.png`.

Con **Aseprite** o **LibreSprite**: abrir el PNG, usar *Import Sprite Sheet* (32×48) y para guardar *Export Sprite Sheet* por filas con 3 columnas.

## Probar
Guardar el PNG y abrir el juego (`.venv/bin/python combate_juego.py` → Modo Aventura). No hay que tocar código.

## Herramientas del proyecto
- `herramientas/importar_ia.py`: convierte un retrato hecho con IA (Gemini, Higgsfield...) en `busto.png`
  limpio (cuadrícula real, paleta corta, sin fondo). Opciones `--ensanchar` y `--acercar` para ajustar el encuadre.
- `herramientas/importar_hoja_ia.py`: importa una hoja de caminar hecha con IA (quita el fondo de cuadritos,
  encuentra cada muñequito y lo pasa a 64×96). Con `--cuadros` se eligen los cuadros si la IA mezcla direcciones.
- `herramientas/sprite_desde_busto.py`: crea `caminar.png` a partir de `busto.png` (cabeza reducida y
  limpiada sobre el cuerpo de `cuerpo_base.png`, recoloreado con la ropa). Para un personaje nuevo se
  agrega su entrada (caja de la cabeza, ojos, gafas, colores) en `PERSONAJES` dentro del script.
- `herramientas/foto_a_pixel.py`: convierte una foto en un busto pixelado que sirve de referencia para calcar.
- `herramientas/exportar_png.py`: vuelve a crear los PNG a partir de `personajes/<nombre>.py` (solo los que no existan).
