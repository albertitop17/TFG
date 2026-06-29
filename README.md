# TFG -  Diseño de agentes inteligentes para la construcción del juego de Pac-Man

Implementación del juego de Pac-Man en Python con Pygame.

El proyecto incluye a los cuatro fantasmas originales con sus comportamientos clásicos y añade dos controladores basados en Inteligencia Artificial para manejar a Pac-Man de forma autónoma.

## Controladores de Pac-Man

Tiene tres tipos de controladores distintos:

* **Humano**: Es controlado por el humano mediante las flechitas del teclado
* **IA_Segura**: Prioriza  la supervivencia.
* **IA_Ptos**: Prioriza la puntuación. Su comportamiento depende de tres parámetros: los radios (radio_caza, radio_super, radio_bolita_optima).

## Estructura del proyecto

```text
main.py              <- Archivo principal
src/
├── constantes.py    <- Recoge todas las constantes del juego: dimensiones, velocidades, mapas, radios, etc.
├── mapa.py          <- Construcción del mapa a partir la matriz
├── fisica.py        <- Motor físico (colisiones, teletransporte, etc)
├── pacman.py        <- Se encarga de Pac-Man y sus animaciones
├── fantasma.py      <- se encarga de los fantasmas y sus animaciones
└── controladores.py <- Recoge la lógica de decisión (IAs de Pac-Man y fantasmas)
sim/
├── config_sim.py    <- Parámetros para la partida (controlador, vidas, radios, etc.)
├── simulador.py     <- Simula n partidas sin abrir la ventana del juego y recoge las estadísticas en un CSV
└── barrido.py       <- Recorre un radio de IA_Ptos para generar un archivo CSV con estadísticas y gráficas PNG
assets/graficos/     <- Sprite sheet original
```

## Requisitos


* Python 3.10 o superior
* Librerías: pygame y matplotlib


```bash
pip install pygame matplotlib
```

## Uso

Se debe ejecutar el juego desde el archivo main.py o escribiendo en la terminal:
```bash
python main.py
```

Aparecerá un menú de texto con tres opciones diferentes:

```
1 - Jugar
2 - Simular
3 - Recorrer valores de un radio
```

**1. Jugar**
Abre la ventana de juego normal. 
Las teclas disponibles en esta ejecución son:

| Tecla | Acción |
|-------|--------|
| `H` | Controlador humano (flechas) |
| `S` | IA Segura |
| `P` | IA Puntos |
| `D` | Cambiar modo debug visual (ciclo de: apagado → valores → ruta → peligro) |

**2. Simular** 
Ejecuta N partidas a máxima velocidad sin ventana y guarda un CSV con columnas `sim`, `nivel_superado`, `muertes`, `puntuacion`, `tiempo_sim_s`.
Al inicio de la ejecución pedirá fijar valores para la simulación o de la configuración de la partida:

| Pregunta | Opciones | Por defecto |
|----------|----------|-------------|
| Controlador | `1` = IA_Ptos, `2` = IA_Segura | `1` |
| Partidas | número entero | `10_000` |
| Nombre del CSV donde escribir | nombre del archivo de salida (ej: `simulacion.csv`)| `resultados.csv` |
| ¿Imprimir cada partida por pantalla? | `s` / `n` | `n` |



**3. Recorrer valores de un radio** 
Simula N paritdas a maxima velocidad para **IA_Ptos** variando el radio elegido entre [2,4,6,8,10,12,14] y genera un CSV y un PNG con tres gráficas de `tasa de victoria`, `muertes` y `puntuación media`.
Al inicio de la ejecución pedirá fijar valores para la simulación o de la configuración de la partida:

| Pregunta | Opciones | Por defecto |
|----------|----------|-------------|
| Radio | `1` = radio_caza, `2` = radio_super, `3` = radio_bolita_optima | `1` |
| Partidas por cada radio | número entero | `2500` |
| Nombre del archivo PNG | nombre del archivo de salida (ej: `simulacion.png`)| no se guarda |
| Nombre del archivo CSV | nombre del archivo de salida (ej: `simulacion.csv`)| no se guarda |


## Notas

- La velocidad (`velocidad = 2 px/frame`) debe ser obligatoriamente un divisor del tamaño de celda (20 px) para que los giros cuadren con la cuadrícula.
- Para cambiar los radios del modo **Barrido** se deben cambiar en el archivo main al hacer la llamada a la función `barrido_radio()` antes de la ejecución del código.
- Hay incluido una carpeta con archivos CSV y PNG donde guardan los archivos que referencian los resultados expuestos en la memoria del TFG. Para mantenerlos organizados puedes incluir la carpeta en el nombre al ejecutar una simulación: `resultados_TFG/simulacion.csv`.