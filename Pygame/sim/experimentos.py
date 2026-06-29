import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from sim.config_sim import ConfigSimulacion, EspecFantasma, fantasmas_clasicos
from sim.simulador import simular
from src import constantes

# ARCHIVO COMO TRABAJO FUTURO

# Más fantasmas
def config_n_fantasmas(n, vidas=3):
    '''
    Crea una ConfigSimulacion con n fantasmas.
    Los 4 primeros son los clásicos. A partir del quinto se reciclan cerebros/colores/spawns
    en orden. El primero es siempre Blinky (índice 0), pues lo necesita CerebroInky.
    '''
    base = fantasmas_clasicos()
    specs = []
    for i in range(n):
        b = base[i % len(base)]
        specs.append(EspecFantasma(b.cerebro, b.color, b.spawn_celda, liberar_con=i * 5))
    return ConfigSimulacion(fantasmas=specs, vidas=vidas, sin_ventana=True)

def experimento_fantasmas(cuentas=(4, 5, 6, 8), n_partidas=20):
    '''
    Mide cómo cambia el rendimiento al añadir más fantasmas
    '''
    for n in cuentas:
        cfg = config_n_fantasmas(n)
        filas = simular(cfg, n_partidas, csv_path=None, consola=False)

        n_filas = len(filas)
        tasa_victoria  = sum(f["nivel_superado"] for f in filas) / n_filas
        media_muertes  = sum(f["muertes"]        for f in filas) / n_filas
        media_puntos   = sum(f["puntuacion"]     for f in filas) / n_filas

        print(f"  {n} fantasmas -> "
              f"victoria {tasa_victoria*100:5.1f}% | "
              f"muertes {media_muertes:.2f} | "
              f"pts {media_puntos:.0f}")

# Más mapas 

def otros_mapas(mapa):
    pass


if __name__ == "__main__":
    experimento_fantasmas()