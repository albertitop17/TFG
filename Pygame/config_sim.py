from src import constantes, controladores


class EspecFantasma:
    '''
    Especificación de un fantasma antes de construirlo
    spawn_celda = (columna, fila) de la cuadrícula
    '''
    def __init__(self, cerebro, color, spawn_celda, liberar_con=0):
        self.cerebro     = cerebro      # Clase del cerebro: CerebroBlinky, CerebroPinky, ...
        self.color       = color        # 'rojo', 'rosa', 'azul', 'naranja'
        self.spawn_celda = spawn_celda  # (columna, fila) en la cuadrícula
        self.liberar_con = liberar_con  # nº de bolitas comidas necesarias para liberarlo


def fantasmas_clasicos():
    '''
    Los 4 fantasmas originales en sus posiciones en casillas
    '''
    return [
        EspecFantasma(controladores.CerebroBlinky, 'rojo',    (13, 14), 0),
        EspecFantasma(controladores.CerebroPinky,  'rosa',    (13, 17), 5),
        EspecFantasma(controladores.CerebroInky,   'azul',    (14, 17), 15),
        EspecFantasma(controladores.CerebroClyde,  'naranja', (15, 17), 20),
        ]


class ConfigSimulacion:
    '''
    Configuración completa de una partida.

    - mapa: matriz de strings (28 columnas, fila de túnel = 13) de constantes.py
    - fantasmas: lista de EspecFantasma
    - vidas: vidas iniciales
    - radios_ia: dict con claves de IA_Ptos : {'radio_caza', 'radio_super', 'radio_bolita_optima'}
    - headless: True para simular sin ventana ni sprites, False para jugar
    - semilla: semilla (afecta a los fantasmas asustados, que se mueven al azar)
    - max_frames: tope de seguridad para no colgar la simulación si Pac-Man se atasca
    '''
    def __init__(self, mapa=None, fantasmas=None, vidas=3,
                 radios_ia=None, headless=True, semilla=None, max_frames=100_000):
        self.mapa       = mapa      if mapa      is not None else constantes.MAPA
        self.fantasmas  = fantasmas if fantasmas is not None else fantasmas_clasicos()
        self.radios_ia  = radios_ia if radios_ia is not None else {}
        self.headless   = headless
        self.vidas      = vidas
        self.semilla    = semilla
        self.max_frames = max_frames

