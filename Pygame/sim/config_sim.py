from src import constantes, controladores


class CrearFantasma:
    '''
    Creamos los fantasmas. Realmente esto no se utiliza en lo que se ha descrito en el TFG.
    Está pensado para poder extrapolar el juego a experimentos con más fantasmas. 
    '''
    def __init__(self, cerebro, color, spawn_celda, liberar_con=0):
        self.cerebro     = cerebro      # Clase del cerebro
        self.color       = color        # 'rojo', 'rosa', 'azul', 'naranja'
        self.spawn_celda = spawn_celda  # (columna, fila) en la cuadrícula
        self.liberar_con = liberar_con  # nº de bolitas comidas necesarias para liberarlo


def fantasmas_clasicos():
    '''
    Los 4 fantasmas originales en sus posiciones en casillas
    '''
    return [
        CrearFantasma(controladores.CerebroBlinky, 'rojo',    (13, 14), 0), CrearFantasma(controladores.CerebroPinky,  'rosa',    (13, 17), 5),
        CrearFantasma(controladores.CerebroInky,   'azul',    (14, 17), 15), CrearFantasma(controladores.CerebroClyde,  'naranja', (15, 17), 20)]


class ConfigSimulacion:
    '''
    Configuración de una partida. Si se recoge todo aquí es más sencillo para poder modificar las configuraciones.
    '''
    def __init__(self, mapa=None, fantasmas=None, vidas=3,
                 radios_ia=None, sin_ventana=True, semilla=None, max_frames=100_000, controlador_pacman=None):
        self.mapa       = mapa      if mapa      is not None else constantes.MAPA #util para el trabajo futuro probar nuevos mapas
        # Si no se especifican otros se usan los cuatro clásicos
        self.fantasmas  = fantasmas if fantasmas is not None else fantasmas_clasicos() #util para el trabajo futuro probar más fantasmas
        self.radios_ia  = radios_ia if radios_ia is not None else {} #  dict con claves de IA_Ptos: {'radio_caza', 'radio_super', 'radio_bolita_optima'}
        self.sin_ventana   = sin_ventana #  True para simular sin ventana ni sprites, False para jugar (así se puede simular más eficientemente)
        self.vidas      = vidas 
        self.semilla    = semilla
        self.max_frames = max_frames # por si acaso se pillase 
        self.controlador_pacman = controlador_pacman if controlador_pacman is not None else controladores.IA_Ptos

