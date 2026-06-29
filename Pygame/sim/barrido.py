import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import csv
import matplotlib
matplotlib.use("Agg")  # backend sin ventana (no intenta abrir una pantalla, antes de pyplot)
import matplotlib.pyplot as plt

from sim.config_sim import ConfigSimulacion
from sim.simulador import simular
from src import constantes

tam = constantes.tamano_celda

def calcular_resumen(filas):
    '''Calcula el resumen de las partidas simuladas para imprimirlas por pantalla'''
    n = len(filas)
    return {
        "tasa_victoria":    round(sum(f["nivel_superado"] for f in filas) / n, 4),
        "media_muertes":    round(sum(f["muertes"]        for f in filas) / n, 3),
        "media_puntuacion": round(sum(f["puntuacion"]     for f in filas) / n, 1),
    }


def barrido_radio(nombre_radio, valores_celdas, n_partidas=30, semilla_base=0,
              otros_radios=None, csv_path=None, png_path=None):
    '''
    Recorre diferentes valores de un radio y devuelve el resumen por cada valor.
    - nombre_radio: 'radio_caza', 'radio_super' o 'radio_bolita_optima'
    - valores_celdas: lista de valores que se quieren probar del radio (en número de celdas) 
    - otros_radios: si se quisiera fijar el resto de radios en otro valor que el predeterminado 
    - csv_path: ruta del CSV de salida (si es None no lo escribe)
    - png_path: ruta de la gráfica PNG (si es None no la genera)
    '''
    # Convertimos los radios base de celdas a píxeles)
    base_px = {}
    if otros_radios is not None:
        for nombre, valor_celdas in otros_radios.items():
            base_px[nombre] = valor_celdas * tam

    filas_resumen = []
    # Se printea para saber qué se está ejecutando
    print(f"Barrido de {nombre_radio} sobre {list(valores_celdas)} celdas ({n_partidas} partidas/valor)")

    for c in valores_celdas:
        # Construimos el dict de radios: los fijos más el que estamos recorriendo
        radios = dict(base_px) # Tenemos que crear una nueva instancia para no modificar el original
        radios[nombre_radio] = c * tam

        cfg = ConfigSimulacion(sin_ventana=True, radios_ia=radios) # Obtenemos la configuración asignada
        filas = simular(cfg, n_partidas, semilla_base, csv_path=None, consola=False) # Se simulan las partidas
        resumen = calcular_resumen(filas)
        
        # Creamos las filas para el CSV
        fila = {}
        fila[nombre_radio + "_celdas"] = c
        fila["tasa_victoria"]    = resumen["tasa_victoria"]
        fila["media_muertes"]    = resumen["media_muertes"]
        fila["media_puntuacion"] = resumen["media_puntuacion"]
        filas_resumen.append(fila)
        
        # Se descomenta si se quiere ir viend los resultados para también ir sabiendo como va 
        # print(f"  {nombre_radio}={c:2d} celdas: "
        #       f"victoria {resumen['tasa_victoria']*100:5.1f}% | "
        #       f"muertes {resumen['media_muertes']:.2f} | "
        #       f"pts {resumen['media_puntuacion']:.0f}")

    if csv_path: # escribimos en el CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(filas_resumen[0].keys()))
            writer.writeheader()
            writer.writerows(filas_resumen)
        print("CSV:", csv_path)

    if png_path: # Creamos las gráficas
        grafica(filas_resumen, nombre_radio, png_path)
        print("PNG:", png_path)

    return filas_resumen

import matplotlib.pyplot as plt

def grafica(filas_resumen, nombre_radio, png_path):
    '''Genera una imagen con 3 gráficas (2 arriba y 1 centrada abajo).'''
    eje_X = [f[nombre_radio + "_celdas"] for f in filas_resumen]
    eje_y_victorias = [f["tasa_victoria"] for f in filas_resumen]
    eje_y_muertes = [f["media_muertes"] for f in filas_resumen]
    eje_y_puntos = [f["media_puntuacion"] for f in filas_resumen]

    # Hacemos la figura un poco más ancha para que quepan dos lado a lado
    fig = plt.figure(figsize=(12, 8))

    # Creamos las 3 graficas
    g1 = plt.subplot2grid((2, 4), (0, 0), colspan=2)
    g2 = plt.subplot2grid((2, 4), (0, 2), colspan=2)
    g3 = plt.subplot2grid((2, 4), (1, 1), colspan=2)

    # Grafica de tasa de victoria
    g1.set_title("Tasa de Victoria")
    g1.set_xlabel(f"{nombre_radio}")
    g1.set_ylabel("Victoria", color="black")
    g1.plot(eje_X, eje_y_victorias, "o-", color="tab:green", linewidth=2)
    g1.tick_params(axis="y", labelcolor="black")
    g1.set_ylim(0, 1)
    g1.grid(True, linestyle='--', alpha=0.6)

    # Grafica de muertes
    g2.set_title("Media de Muertes")
    g2.set_xlabel(f"{nombre_radio}")
    g2.set_ylabel("Muertes", color="black")
    g2.plot(eje_X, eje_y_muertes, "s-", color="tab:red", linewidth=2)
    g2.tick_params(axis="y", labelcolor="black")
    g2.grid(True, linestyle='--', alpha=0.6)

    # Grafica de puntuación
    g3.set_title("Puntuación Media")
    g3.set_xlabel(f"{nombre_radio}")
    g3.set_ylabel("Puntuación", color="black")
    g3.plot(eje_X, eje_y_puntos, "^-", color="tab:blue", linewidth=2)
    g3.tick_params(axis="y", labelcolor="black")
    g3.grid(True, linestyle='--', alpha=0.6)

    # Para que queden bien los títulos ajustamos los márgenes
    fig.tight_layout()
    fig.savefig(png_path, dpi=120)
    plt.close(fig)