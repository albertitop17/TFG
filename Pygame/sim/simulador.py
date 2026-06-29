import os
# Fijamos los drivers antes de abrir pygame, le decimos que simule la pantalla y audio sin abrirlos de verdad 
# (sino fallaría al intentar abrirlos y no haber)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import csv
import time
from sim.config_sim import ConfigSimulacion
from main import Game

# Columnas para recoger los datos de la simulación
columnas_csv = ["sim", "nivel_superado", "muertes", "puntuacion", "tiempo_sim_s"]

def simular(config=None, n_partidas=100, semilla_base=0, csv_path="resultados.csv", consola=True):
    '''
    Ejecuta n_partidas con la IA y guarda los resultados en un CSV (se ejecuta la partida según confg)
    consola indica si se quiere mostrar por pantalla cada partida o directamente en el csv
    '''
    if config is None: # Si no hay configuración extra se simula el predeterminado sin pantalla
        config = ConfigSimulacion(sin_ventana=True)

    # Creamos el motor una sola vez y lo reutilizamos para todas las partidas.
    # Así no se reinicia pygame ni se recargan los sprites en cada partida.
    juego = Game(config)
    filas = []

    t0 = time.perf_counter() # Contamos el tiempo que tardan
    for i in range(n_partidas):
        resultado = juego.simular_una_partida(semilla=semilla_base + i) # cada vez una semilla distinta
        resultado["sim"] = i + 1 # Añadimos al diccionario el número de la partida (para el csv)
        filas.append(resultado)
        if consola: # si se quiere imprimir por consola el resumen (por cada partida)
            print(f"  Partida {i + 1}/{n_partidas} — "
                  f"victoria={bool(resultado['nivel_superado'])} | "
                  f"muertes={resultado['muertes']} | "
                  f"pts={resultado['puntuacion']}")
        if (i + 1) % 500 == 0: # Para saber por que partida vamos añadimos un mensaje cada 500 partidas
            print(f"  Partida {i + 1}/{n_partidas}")
    dt = time.perf_counter() - t0

    # Escribimos en el CSV
    if csv_path is not None:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columnas_csv, extrasaction="ignore")
            writer.writeheader() # Escribe la primera linea con los nombres de las columnas 
            writer.writerows(filas) # Escribe todas las demás filas

    # Resumen en la consola
    n = len(filas)
    tasa_victoria  = sum(f["nivel_superado"] for f in filas) / n
    media_muertes  = sum(f["muertes"]        for f in filas) / n
    media_puntos   = sum(f["puntuacion"]     for f in filas) / n

    print(f"\nResumen ({n} partidas, {dt:.1f} s de cómputo)")
    print(f"  Tasa de victoria : {tasa_victoria * 100:.1f} %")
    print(f"  Muertes (media)  : {media_muertes:.2f}")
    print(f"  Puntuación (media): {media_puntos:.0f}")
    if csv_path:
        print(f"  CSV guardado en  : {csv_path}")

    return filas